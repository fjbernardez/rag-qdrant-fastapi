from typing import Any, Protocol


class LlmProvider(Protocol):
    def generate_answer(
            self,
            *,
            question: str,
            context_chunks: list[dict[str, Any]],
    ) -> str:
        ...
