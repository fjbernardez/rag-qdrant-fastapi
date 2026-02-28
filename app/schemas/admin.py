from pydantic import BaseModel


class QdrantResetResponse(BaseModel):
    collection: str
    recreated: bool
