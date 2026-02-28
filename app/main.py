from fastapi import FastAPI

from app.routers.base import router as base_router
from app.routers.ingest import router as ingest_router

app = FastAPI(title="RAG Qdrant API")

app.include_router(base_router)
app.include_router(ingest_router)
