from fastapi import FastAPI

from app.routers.admin import router as admin_router
from app.routers.base import router as base_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router

app = FastAPI(title="RAG Qdrant API")

app.include_router(base_router)
app.include_router(ingest_router)
app.include_router(admin_router)
app.include_router(search_router)
