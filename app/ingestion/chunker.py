from dataclasses import dataclass


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


@dataclass(frozen=True)
class Chunk:
    content: str
    chunk_index: int
    page_start: int | None
    page_end: int | None


def chunk_text(
    text: str,
    *,
    page_start: int | None,
    page_end: int | None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    chunks: list[Chunk] = []
    start = 0
    chunk_index = 0
    step = chunk_size - chunk_overlap

    while start < len(text):
        end = min(start + chunk_size, len(text))
        content = text[start:end]
        if content:
            chunks.append(
                Chunk(
                    content=content,
                    chunk_index=chunk_index,
                    page_start=page_start,
                    page_end=page_end,
                )
            )
            chunk_index += 1
        if end == len(text):
            break
        start += step

    return chunks
