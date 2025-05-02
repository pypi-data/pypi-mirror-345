"""FastAPI application lifecycle management."""

from contextlib import asynccontextmanager
from logging import DEBUG, config
from typing import Callable

from fastapi import FastAPI

from mockstack.config import Settings
from mockstack.display import announce


def lifespan_provider(
    settings: Settings,
) -> Callable:
    """Provide the lifespan context manager."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """FastAPI application lifespan management.

        This is the context manager that FastAPI will use to manage the lifecycle of the application.
        """
        if settings.debug:
            # Enable verbose debug logging if debug mode is set.
            settings.logging["handlers"]["console"]["level"] = DEBUG

        config.dictConfig(settings.logging)

        announce(app, settings)

        yield

    return lifespan
