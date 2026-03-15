from collections.abc import Sequence
from typing import Any

from app.clients.qdrant_client import get_qdrant_client
from app.core.settings import settings
from app.ingestion.embedder import get_embedding_provider
from app.schemas.search import SearchChunk, SearchResponse

QDRANT_TOP_K = 20
MAX_SELECTED_CHUNKS = 8
MIN_SELECTED_WITHOUT_FILTER = 5
SCORE_THRESHOLD = 0.50
ENOUGH_CONTEXT_MIN_CHUNKS = 3


def retrieve_chunks(question: str) -> SearchResponse:
    embedding_provider = get_embedding_provider()
    query_vector = embedding_provider.embed_texts([question])[0]

    client = get_qdrant_client()
    search_result = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        with_payload=True,
        with_vectors=False,
        limit=QDRANT_TOP_K,
    )
    points = getattr(search_result, "points", [])

    retrieved_chunks = sorted(
        (_to_search_chunk(point) for point in points),
        key=lambda chunk: chunk.score,
        reverse=True,
    )

    selected_chunks = _select_chunks(retrieved_chunks)

    if selected_chunks:
        answer_preview = (
            f"Retrieved {len(selected_chunks)} relevant chunks. "
            "LLM answer generation is pending integration."
        )
    else:
        answer_preview = "No relevant context found."

    return SearchResponse(
        question=question,
        enough_context=len(selected_chunks) >= ENOUGH_CONTEXT_MIN_CHUNKS,
        retrieved_count=len(retrieved_chunks),
        selected_count=len(selected_chunks),
        answer_preview=answer_preview,
        chunks=selected_chunks,
    )


def _select_chunks(chunks: Sequence[SearchChunk]) -> list[SearchChunk]:
    threshold_filtered = [chunk for chunk in chunks if chunk.score >= SCORE_THRESHOLD][:MAX_SELECTED_CHUNKS]
    if threshold_filtered:
        return threshold_filtered

    return list(chunks[:MIN_SELECTED_WITHOUT_FILTER])


def _to_search_chunk(point: Any) -> SearchChunk:
    payload = getattr(point, "payload", {}) or {}
    score = getattr(point, "score", 0.0)

    return SearchChunk(
        content=str(payload.get("content", "")),
        document_name=str(payload.get("document_name", "")),
        page_start=_optional_int(payload.get("page_start")),
        page_end=_optional_int(payload.get("page_end")),
        chunk_index=int(payload.get("chunk_index", 0)),
        score=float(score if score is not None else 0.0),
    )


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)
