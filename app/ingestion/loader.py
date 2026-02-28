from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterator

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".pdf"}


@dataclass(frozen=True)
class LoadedText:
    document_name: str
    text: str
    page_start: int | None
    page_end: int | None


def data_dir_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def normalize_text(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text.strip())
    return collapsed


def iter_supported_files(data_dir: Path) -> Iterator[Path]:
    if not data_dir.exists():
        return iter(())

    files = (
        path
        for path in data_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return iter(sorted(files))


def load_text_fragments(data_dir: Path) -> Iterator[LoadedText]:
    for file_path in iter_supported_files(data_dir):
        extension = file_path.suffix.lower()
        if extension == ".txt":
            yield from _load_txt(file_path)
        elif extension == ".pdf":
            yield from _load_pdf(file_path)


def _load_txt(file_path: Path) -> list[LoadedText]:
    text = normalize_text(file_path.read_text(encoding="utf-8", errors="ignore"))
    if not text:
        return []

    return [
        LoadedText(
            document_name=file_path.name,
            text=text,
            page_start=None,
            page_end=None,
        )
    ]


def _load_pdf(file_path: Path) -> list[LoadedText]:
    reader = PdfReader(str(file_path))
    fragments: list[LoadedText] = []

    for page_index, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        text = normalize_text(raw_text)
        if not text:
            continue

        fragments.append(
            LoadedText(
                document_name=file_path.name,
                text=text,
                page_start=page_index,
                page_end=page_index,
            )
        )

    return fragments
