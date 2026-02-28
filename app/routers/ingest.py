from fastapi import APIRouter

from app.ingestion.pipeline import run_ingestion
from app.schemas.ingestion import IngestResponse


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    result = run_ingestion()
    return IngestResponse(
        documents_processed=result.documents_processed,
        chunks_upserted=result.chunks_upserted,
        skipped=result.skipped,
    )
