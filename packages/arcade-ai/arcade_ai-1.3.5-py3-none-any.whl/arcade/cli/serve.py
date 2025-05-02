import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

import fastapi
import uvicorn
from loguru import logger

from arcade.core.telemetry import OTELHandler
from arcade.sdk import Toolkit
from arcade.worker.fastapi.worker import FastAPIWorker


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore[assignment]

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(log_level: int = logging.INFO) -> None:
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    # Remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Configure loguru with custom format, no colors
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "serialize": False,
                "level": log_level,
                "format": "{level}  [{time:HH:mm:ss.SSS}] {message}"
                + (" {name}:{function}:{line}" if log_level <= logging.DEBUG else "")
                + ("\n{exception}" if "{exception}" in "{message}" else ""),
            }
        ]
    )


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):  # type: ignore[no-untyped-def]
    try:
        yield
    except asyncio.CancelledError:
        # This is necessary to prevent an unhandled error
        # when the user presses Ctrl+C
        logger.debug("Lifespan cancelled.")


def serve_default_worker(
    host: str = "127.0.0.1",
    port: int = 8002,
    disable_auth: bool = False,
    workers: int = 1,
    timeout_keep_alive: int = 5,
    enable_otel: bool = False,
    debug: bool = False,
    **kwargs: Any,
) -> None:
    """
    Get an instance of a FastAPI server with the Arcade Worker.
    """
    # Setup unified logging
    setup_logging(log_level=logging.DEBUG if debug else logging.INFO)

    toolkits = Toolkit.find_all_arcade_toolkits()
    if not toolkits:
        raise RuntimeError("No toolkits found in Python environment.")

    worker_secret = os.environ.get("ARCADE_WORKER_SECRET")
    if not disable_auth and not worker_secret:
        logger.warning(
            "Warning: ARCADE_WORKER_SECRET environment variable is not set. Using 'dev' as the worker secret.",
        )
        worker_secret = worker_secret or "dev"

    app = fastapi.FastAPI(
        title="Arcade Worker",
        description="Arcade default Worker implementation using FastAPI.",
        version="0.1.0",
        lifespan=lifespan,  # Use custom lifespan to catch errors, notably KeyboardInterrupt (Ctrl+C)
    )

    otel_handler = OTELHandler(app, enable=enable_otel)

    worker = FastAPIWorker(
        app, secret=worker_secret, disable_auth=disable_auth, otel_meter=otel_handler.get_meter()
    )

    toolkit_tool_counts = {}
    for toolkit in toolkits:
        prev_tool_count = worker.catalog.get_tool_count()
        worker.register_toolkit(toolkit)
        new_tool_count = worker.catalog.get_tool_count()
        toolkit_tool_counts[f"{toolkit.name} ({toolkit.package_name})"] = (
            new_tool_count - prev_tool_count
        )

    logger.info("Serving the following toolkits:")
    for name, tool_count in toolkit_tool_counts.items():
        logger.info(f"  - {name}: {tool_count} tools")

    logger.info("Starting FastAPI server...")

    class CustomUvicornServer(uvicorn.Server):
        def install_signal_handlers(self) -> None:
            pass  # Disable Uvicorn's default signal handlers

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        workers=workers,
        timeout_keep_alive=timeout_keep_alive,
        log_config=None,
        **kwargs,
    )
    server = CustomUvicornServer(config=config)

    async def serve() -> None:
        await server.serve()

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    finally:
        if enable_otel:
            otel_handler.shutdown()
        logger.debug("Server shutdown complete.")
