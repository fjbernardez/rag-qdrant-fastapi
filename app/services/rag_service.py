from app.core.settings import settings
from app.providers.llm.openai_provider import OpenAILlmProvider
from app.schemas.ask import AskChunk, AskResponse
from app.schemas.search import SearchChunk
from app.services.retrieval_service import retrieve_chunks


def ask_question(question: str) -> AskResponse:
    retrieval_result = retrieve_chunks(question)
    llm_provider = OpenAILlmProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    answer = llm_provider.generate_answer(
        question=question,
        context_chunks=[_chunk_to_context(chunk) for chunk in retrieval_result.chunks],
    )

    return AskResponse(
        question=question,
        answer=answer,
        enough_context=retrieval_result.enough_context,
        retrieved_count=retrieval_result.retrieved_count,
        selected_count=retrieval_result.selected_count,
        chunks=[AskChunk.model_validate(chunk.model_dump()) for chunk in retrieval_result.chunks],
    )


def _chunk_to_context(chunk: SearchChunk) -> dict[str, object]:
    return {
        "content": chunk.content,
        "document_name": chunk.document_name,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
        "chunk_index": chunk.chunk_index,
        "score": chunk.score,
    }
