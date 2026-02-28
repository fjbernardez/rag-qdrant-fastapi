from fastapi import APIRouter
from qdrant_client import models

from app.clients.qdrant_client import get_qdrant_client
from app.core.settings import settings
from app.schemas.admin import QdrantResetResponse


router = APIRouter()


@router.post("/admin/qdrant/reset", response_model=QdrantResetResponse)
def reset_qdrant_collection() -> QdrantResetResponse:
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection

    if client.collection_exists(collection_name=collection_name):
        client.delete_collection(collection_name=collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=1536,
            distance=models.Distance.COSINE,
        ),
    )

    return QdrantResetResponse(collection=collection_name, recreated=True)
