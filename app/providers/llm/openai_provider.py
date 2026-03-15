from typing import Any

from openai import APIError, OpenAI

from app.providers.llm.base import LlmProvider


class OpenAILlmProvider(LlmProvider):
    def __init__(self, *, api_key: str, model: str) -> None:
        self._model = model
        self._client = OpenAI(api_key=api_key)

    def generate_answer(
            self,
            *,
            question: str,
            context_chunks: list[dict[str, Any]],
    ) -> str:
        system_prompt = (
            "You are a retrieval-augmented assistant. "
            "Answer ONLY using the provided context. "
            "If the answer is not present in the context, say clearly that it was not found in the documents. "
            "Do not invent information. "
            "Be clear and concise. "
            "Include simple references at the end using document name and page range when available."
        )
        user_prompt = _build_user_prompt(
            question=question,
            context_chunks=context_chunks,
        )

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": system_prompt}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": user_prompt}],
                    },
                ],
            )
        except APIError as exc:
            raise RuntimeError("OpenAI text generation request failed.") from exc

        output_text = getattr(response, "output_text", "")
        if output_text:
            return output_text.strip()

        extracted_text = _extract_output_text(response)
        if extracted_text:
            return extracted_text

        raise RuntimeError("OpenAI returned an empty response.")


def _build_user_prompt(
        *,
        question: str,
        context_chunks: list[dict[str, Any]],
) -> str:
    context_sections = [_format_context_chunk(chunk) for chunk in context_chunks]
    context_block = "\n\n".join(context_sections) if context_sections else "[No context provided]"

    return (
        f"Question:\n{question}\n\n"
        "Context:\n"
        f"{context_block}\n\n"
        "Instructions:\n"
        "- Answer only from the context.\n"
        "- If the answer is not in the context, say it was not found in the documents.\n"
        "- Do not add external knowledge.\n"
        "- End with references."
    )


def _format_context_chunk(chunk: dict[str, Any]) -> str:
    document_name = str(chunk.get("document_name", "unknown"))
    chunk_index = int(chunk.get("chunk_index", 0))
    page_start = chunk.get("page_start")
    page_end = chunk.get("page_end")
    content = str(chunk.get("content", ""))

    if page_start is not None or page_end is not None:
        page_range = f"{page_start}-{page_end}"
    else:
        page_range = "n/a"

    return (
        f"[Fuente: {document_name} | paginas {page_range} | chunk {chunk_index}]\n"
        f"{content}"
    )


def _extract_output_text(response: Any) -> str:
    output = getattr(response, "output", [])
    parts: list[str] = []

    for item in output:
        content_items = getattr(item, "content", [])
        for content_item in content_items:
            text_value = getattr(content_item, "text", "")
            if text_value:
                parts.append(str(text_value).strip())

    return "\n".join(part for part in parts if part).strip()
