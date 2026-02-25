from fastapi import FastAPI

from app.routers.base import router as base_router

app = FastAPI(title="RAG Qdrant API")

app.include_router(base_router)
