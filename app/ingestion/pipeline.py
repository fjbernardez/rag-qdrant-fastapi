import hashlib
import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client import models

from app.clients.qdrant_client import get_qdrant_client
from app.core.settings import settings
from app.infra.qdrant_setup import ensure_collection_exists
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import get_embedding_provider
from app.ingestion.loader import data_dir_path, load_text_fragments
from app.providers.embeddings.base import EmbeddingProvider


@dataclass(frozen=True)
class IngestionResult:
    documents_processed: int
    chunks_upserted: int
    skipped: int


def run_ingestion() -> IngestionResult:
    ensure_collection_exists()
    client = get_qdrant_client()
    provider = get_embedding_provider()
    fragments = load_text_fragments(data_dir_path())

    pending_chunks: list[_ChunkRecord] = []
    document_names: set[str] = set()
    chunks_upserted = 0

    for fragment in fragments:
        document_names.add(fragment.document_name)
        chunks = chunk_text(
            fragment.text,
            page_start=fragment.page_start,
            page_end=fragment.page_end,
        )
        for chunk in chunks:
            pending_chunks.append(
                _ChunkRecord(
                    document_name=fragment.document_name,
                    content=chunk.content,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    chunk_index=chunk.chunk_index,
                )
            )

            if len(pending_chunks) >= settings.embedding_batch_size:
                chunks_upserted += _upsert_batch(
                    client=client,
                    provider=provider,
                    chunk_records=pending_chunks,
                )
                pending_chunks = []

    if pending_chunks:
        chunks_upserted += _upsert_batch(
            client=client,
            provider=provider,
            chunk_records=pending_chunks,
        )

    return IngestionResult(
        documents_processed=len(document_names),
        chunks_upserted=chunks_upserted,
        skipped=0,
    )


@dataclass(frozen=True)
class _ChunkRecord:
    document_name: str
    content: str
    page_start: int | None
    page_end: int | None
    chunk_index: int


def _upsert_batch(
    *,
    client: QdrantClient,
    provider: EmbeddingProvider,
    chunk_records: list[_ChunkRecord],
) -> int:
    texts = [record.content for record in chunk_records]
    vectors = provider.embed_texts(texts)

    points = [
        models.PointStruct(
            id=_point_id(
                document_name=record.document_name,
                page_start=record.page_start,
                page_end=record.page_end,
                chunk_index=record.chunk_index,
                content=record.content,
            ),
            vector=vector,
            payload={
                "content": record.content,
                "document_name": record.document_name,
                "page_start": record.page_start,
                "page_end": record.page_end,
                "chunk_index": record.chunk_index,
            },
        )
        for record, vector in zip(chunk_records, vectors, strict=True)
    ]

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


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
