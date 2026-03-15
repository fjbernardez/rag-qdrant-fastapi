from fastapi import APIRouter

from app.schemas.search import SearchRequest, SearchResponse
from app.services.retrieval_service import retrieve_chunks


router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    return retrieve_chunks(question=request.question)
