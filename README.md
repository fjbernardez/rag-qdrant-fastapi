# rag-qdrant-fastapi

Base API project with FastAPI, managed with `uv`.

## Requirements

- Python 3.14 (according to `pyproject.toml`)
- `uv` installed

## Installation

```bash
uv sync
```

## Run in development

```bash
uv run uvicorn app.main:app --reload
```

The API is available at:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Initial structure

```text
app/
  __init__.py
  main.py
pyproject.toml
uv.lock
```
