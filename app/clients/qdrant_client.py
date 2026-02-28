from app.core.settings import settings
from qdrant_client import QdrantClient


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)
