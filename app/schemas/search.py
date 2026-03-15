from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str


class SearchChunk(BaseModel):
    content: str
    document_name: str
    page_start: int | None
    page_end: int | None
    chunk_index: int
    score: float


class SearchResponse(BaseModel):
    question: str
    enough_context: bool
    retrieved_count: int
    selected_count: int
    answer_preview: str
    chunks: list[SearchChunk]
