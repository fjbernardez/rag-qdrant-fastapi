from pydantic import BaseModel


class IngestResponse(BaseModel):
    documents_processed: int
    chunks_upserted: int
    skipped: int
