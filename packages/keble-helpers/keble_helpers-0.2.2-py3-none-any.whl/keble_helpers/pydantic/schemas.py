from typing import Any
from urllib.parse import urlparse


def is_http_url(url: Any) -> bool:
    if url is None:
        return False
    val = str(url)
    parsed = urlparse(val)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    return True
