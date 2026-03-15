# rag-qdrant-fastapi

Simple RAG API built with FastAPI, Qdrant, and OpenAI.

This first version includes:
- document ingestion into Qdrant
- semantic retrieval using OpenAI embeddings
- a `/search` endpoint to inspect retrieved chunks
- an `/ask` endpoint to generate a final answer from retrieved context

## Requirements

- Python 3.14 or newer
- `uv`
- Docker, or an accessible Qdrant instance
- a valid OpenAI API key

## Installation

```bash
uv sync
```

## Configuration

Create a `.env` file in the project root. You can start from `.env.example`.

Required variables:

- `QDRANT_URL`
- `QDRANT_COLLECTION`
- `OPENAI_API_KEY`

Optional variables:

- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_CHAT_MODEL`
- `EMBEDDING_BATCH_SIZE`

Example:

```env
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=documents
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-5-mini
EMBEDDING_BATCH_SIZE=64
```

## Start Qdrant

The project includes `docker-compose.yml` for local Qdrant:

```bash
docker compose up -d
```

Qdrant will be available at:

- `http://localhost:6333`
- `http://localhost:6334`

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/health/qdrant`
- `http://127.0.0.1:8000/docs`

## Add source documents

Put your source documents inside `data/`.

Supported file types:

- `.txt`
- `.pdf`

Then run ingestion:

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

The ingestion flow:
- reads documents from `data/`
- splits them into chunks
- generates embeddings with OpenAI
- creates the Qdrant collection if it does not exist
- upserts vectorized chunks into the configured collection

## Example documents

Sample `.txt` files are useful for onboarding and smoke testing, but they should not live inside `data/` by default because everything under `data/` is ingested automatically.

This repository includes sample files under `examples/`:

- [employee_handbook.txt](/C:/Users/francisco/Documents/personal/projects/rag-qdrant-fastapi/examples/employee_handbook.txt)
- [remote_work_policy.txt](/C:/Users/francisco/Documents/personal/projects/rag-qdrant-fastapi/examples/remote_work_policy.txt)

If you want to test the pipeline quickly, copy them into `data/` and run `/ingest`.

## Main endpoints

### `POST /ingest`

Runs ingestion for the documents in `data/`.

### `POST /search`

Runs semantic retrieval without calling the final LLM.

Request:

```json
{
  "question": "What is the vacation policy?"
}
```

Response:

```json
{
  "question": "What is the vacation policy?",
  "enough_context": true,
  "retrieved_count": 20,
  "selected_count": 4,
  "answer_preview": "Retrieved 4 relevant chunks. LLM answer generation is pending integration.",
  "chunks": [
    {
      "content": "...",
      "document_name": "manual.pdf",
      "page_start": 2,
      "page_end": 3,
      "chunk_index": 0,
      "score": 0.81
    }
  ]
}
```

### `POST /ask`

Runs the full RAG flow:
- question embedding
- retrieval from Qdrant
- chunk selection
- prompt construction with context
- OpenAI Responses API call

Request:

```json
{
  "question": "What is the vacation policy?"
}
```

Response:

```json
{
  "question": "What is the vacation policy?",
  "answer": "The policy states ...\n\nReferences: manual.pdf pages 2-3",
  "enough_context": true,
  "retrieved_count": 20,
  "selected_count": 4,
  "chunks": [
    {
      "content": "...",
      "document_name": "manual.pdf",
      "page_start": 2,
      "page_end": 3,
      "chunk_index": 0,
      "score": 0.81
    }
  ]
}
```

## Internal flow

### Retrieval

- generates a question embedding with OpenAI
- queries Qdrant using the configured collection
- requests the top 20 results
- sorts by score
- applies a simple threshold
- keeps up to 8 chunks
- falls back to the top 5 chunks if threshold filtering returns none

### Final generation

- takes the selected chunks
- builds a prompt with source and page metadata
- sends the prompt to the model configured in `OPENAI_CHAT_MODEL`
- instructs the model to answer only from retrieved context

## Current structure

```text
app/
  clients/
  core/
  infra/
  ingestion/
  providers/
    embeddings/
    llm/
  routers/
  schemas/
  services/
  main.py
data/
examples/
docker-compose.yml
pyproject.toml
README.md
```
