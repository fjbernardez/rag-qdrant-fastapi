from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter

from app.clients.qdrant_client import get_qdrant_client
from app.infra.qdrant_setup import ensure_collection_exists


@asynccontextmanager
async def router_lifespan(_: APIRouter) -> AsyncIterator[None]:
    ensure_collection_exists()
    yield


router = APIRouter(lifespan=router_lifespan)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/")
def root():
    return {"message": "RAG service running"}


@router.get("/health/qdrant")
def health_qdrant():
    client = get_qdrant_client()
    collections = client.get_collections()
    return {
        "status": "ok",
        "collections": [collection.name for collection in collections.collections],
    }
