from pathlib import Path
from typing import Generator
from urllib.parse import urlparse, unquote
import pymupdf
from chercher import Document, hookimpl

pymupdf.JM_mupdf_show_errors = 0


def normalize_uri(uri: str) -> Path:
    if uri.startswith("file://"):
        parsed_uri = urlparse(uri)
        decoded_path = unquote(parsed_uri.path)
        return Path(decoded_path).resolve()

    return Path(uri)


@hookimpl()
def ingest(uri: str) -> Generator[Document, None, None]:
    path = normalize_uri(uri)
    if not path.exists() or not path.is_file() or path.suffix != ".pdf":
        return

    body = ""
    with pymupdf.open(path) as doc:
        metadata = doc.metadata
        for page in doc:
            body += page.get_text()

    yield Document(
        uri=path.as_uri(),
        title=metadata.get("title", ""),
        body=body,
        metadata=metadata,
    )


@hookimpl()
def prune(uri: str) -> bool | None:
    if uri.startswith("file://"):
        parsed_uri = urlparse(uri)
        decoded_path = unquote(parsed_uri.path)
        path = Path(decoded_path).resolve()
    else:
        return

    if path.suffix != ".pdf":
        return

    if not path.exists() or not path.is_file():
        return True
