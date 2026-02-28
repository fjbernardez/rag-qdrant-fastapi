from openai import APIError, OpenAI

from app.providers.embeddings.base import EmbeddingProvider


EMBEDDING_DIMENSIONS = 1536


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, *, api_key: str, model: str) -> None:
        self._model = model
        self._client = OpenAI(api_key=api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = self._client.embeddings.create(
                model=self._model,
                input=texts,
            )
        except APIError as exc:
            raise RuntimeError("OpenAI embeddings request failed.") from exc

        vectors = [item.embedding for item in response.data]
        if len(vectors) != len(texts):
            raise RuntimeError(
                "OpenAI embeddings response size mismatch with input batch."
            )

        for vector in vectors:
            if len(vector) != EMBEDDING_DIMENSIONS:
                raise RuntimeError(
                    f"Invalid embedding dimension: expected {EMBEDDING_DIMENSIONS}."
                )

        return vectors
