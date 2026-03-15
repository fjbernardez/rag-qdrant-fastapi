from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskChunk(BaseModel):
    content: str
    document_name: str
    page_start: int | None
    page_end: int | None
    chunk_index: int
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    enough_context: bool
    retrieved_count: int
    selected_count: int
    chunks: list[AskChunk]
