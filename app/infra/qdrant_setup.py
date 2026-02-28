from qdrant_client import models

from app.clients.qdrant_client import get_qdrant_client
from app.core.settings import settings


def ensure_collection_exists() -> None:
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection

    if client.collection_exists(collection_name=collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=1536,
            distance=models.Distance.COSINE,
        ),
    )
