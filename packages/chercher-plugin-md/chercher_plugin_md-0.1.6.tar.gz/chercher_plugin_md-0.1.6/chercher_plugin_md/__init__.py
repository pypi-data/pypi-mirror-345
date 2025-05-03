from pathlib import Path
from typing import Generator
from urllib.parse import urlparse
import hashlib
import frontmatter
from chercher import Document, hookimpl


def normalize_uri(uri: str) -> Path:
    if uri.startswith("file://"):
        parsed_uri = urlparse(uri)
        return Path(parsed_uri.path).resolve()

    return Path(uri)


@hookimpl
def ingest(uri: str) -> Generator[Document, None, None]:
    path = normalize_uri(uri)
    if not path.exists() or not path.is_file() or path.suffix != ".md":
        return

    with path.open("rb") as f:
        content = f.read()
        hash = hashlib.sha256(content)
        post = frontmatter.loads(content.decode("utf-8"))

    yield Document(
        uri=path.as_uri(),
        title=path.name,
        body=post.content,
        hash=hash.hexdigest(),
        metadata={},
    )


@hookimpl()
def prune(uri: str) -> bool | None:
    if uri.startswith("file://"):
        parsed_uri = urlparse(uri)
        path = Path(parsed_uri.path).resolve()
    else:
        return

    if path.suffix != ".md":
        return

    if not path.exists() or not path.is_file():
        return True
