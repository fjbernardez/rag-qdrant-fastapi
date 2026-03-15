from fastapi import APIRouter

from app.schemas.ask import AskRequest, AskResponse
from app.services.rag_service import ask_question


router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return ask_question(request.question)
