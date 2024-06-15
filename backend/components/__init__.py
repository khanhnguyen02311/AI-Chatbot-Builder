from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configurations.arguments import APP_STAGE, APP_DEBUG
from components.data import init_data_structure
from agent_system.data import init_embedding_structure
from .endpoints import super_hub, tags_metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Do something at the start
    yield
    # Clean up


def serve_api():
    init_data_structure()
    init_embedding_structure()

    app = FastAPI(lifespan=lifespan, debug=APP_DEBUG, openapi_tags=tags_metadata, redoc_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # your frontend urls
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "PATCH"],  # OPTIONS method is handled by NGINX
        allow_headers=["*"]
    )
    app.include_router(super_hub)
    # if APP_STAGE in ['staging', 'prod']:
    return app
