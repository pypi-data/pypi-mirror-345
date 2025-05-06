from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from crypticorn.common.logging import configure_logging
import logging


def add_cors_middleware(app: "FastAPI"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # vite dev server
            "http://localhost:4173",  # vite preview server
        ],
        allow_origin_regex="^https:\/\/([a-zA-Z0-9-]+\.)*crypticorn\.(dev|com)\/?$",  # matches (multiple or no) subdomains of crypticorn.dev and crypticorn.com
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def default_lifespan(app: FastAPI):
    """Default lifespan for the applications.
    This is used to configure the logging for the application.
    To override this, pass a different lifespan to the FastAPI constructor or call this lifespan within a custom lifespan.
    """
    configure_logging(__name__)  # for the consuming app
    logger = logging.getLogger(__name__)
    yield
