from app.core.settings import settings
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.embeddings.openai_provider import OpenAIEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )
