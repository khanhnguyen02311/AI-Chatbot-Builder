from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import super_hub
from . import data

tags_metadata = [
    {
        "name": "system",
        "description": "Operations with application system",
    },
    {
        "name": "auth",
        "description": "Operations with authentication methods & user validation",
    },
    {
        "name": "user",
        "description": "Operations with user information",
    },
    {
        "name": "model",
        "description": "Operations with AI models & agents",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Do something at the start
    yield
    # Clean up


def serve_api(stage: str, debug: bool):
    app = FastAPI(lifespan=lifespan, debug=debug, openapi_tags=tags_metadata, redoc_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # your frontend urls
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "PATCH"],  # OPTIONS method is handled by NGINX
        allow_headers=["*"]
    )
    app.include_router(super_hub)
    # if stage in ['staging', 'prod']:
    return app
