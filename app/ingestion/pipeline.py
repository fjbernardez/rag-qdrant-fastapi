import hashlib
import uuid
from dataclasses import dataclass

from qdrant_client import models

from app.clients.qdrant_client import get_qdrant_client
from app.core.settings import settings
from app.infra.qdrant_setup import ensure_collection_exists
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_text
from app.ingestion.loader import data_dir_path, load_text_fragments


@dataclass(frozen=True)
class IngestionResult:
    documents_processed: int
    chunks_upserted: int
    skipped: int


def run_ingestion() -> IngestionResult:
    ensure_collection_exists()
    client = get_qdrant_client()
    fragments = load_text_fragments(data_dir_path())

    points: list[models.PointStruct] = []
    document_names: set[str] = set()

    for fragment in fragments:
        document_names.add(fragment.document_name)
        chunks = chunk_text(
            fragment.text,
            page_start=fragment.page_start,
            page_end=fragment.page_end,
        )
        for chunk in chunks:
            point_id = _point_id(
                document_name=fragment.document_name,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
            )
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embed_text(chunk.content),
                    payload={
                        "content": chunk.content,
                        "document_name": fragment.document_name,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "chunk_index": chunk.chunk_index,
                    },
                )
            )

    if points:
        client.upsert(collection_name=settings.qdrant_collection, points=points)

    return IngestionResult(
        documents_processed=len(document_names),
        chunks_upserted=len(points),
        skipped=0,
    )


def _point_id(
        *,
        document_name: str,
        page_start: int | None,
        page_end: int | None,
        chunk_index: int,
        content: str,
) -> str:
    fingerprint = (
        f"{document_name}|{page_start}|{page_end}|{chunk_index}|{content}"
    ).encode("utf-8")

    hash_bytes = hashlib.sha256(fingerprint).digest()
    return str(uuid.UUID(bytes=hash_bytes[:16]))


# def _point_id(
#         *,
#         document_name: str,
#         page_start: int | None,
#         page_end: int | None,
#         chunk_index: int,
#         content: str,
# ) -> str:
#     fingerprint = (
#         f"{document_name}|{page_start}|{page_end}|{chunk_index}|{content}"
#     ).encode("utf-8")
#     return hashlib.sha256(fingerprint).hexdigest()
