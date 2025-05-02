import os
import hashlib
import urllib.parse
from pathlib import Path
from typing import Optional

from lavender_data.storage.abc import Storage


MULTIPART_CHUNKSIZE = 1 << 23


class HttpStorage(Storage):
    scheme = "http"

    def __init__(self):
        pass

    def download(self, remote_path: str, local_path: str) -> None:
        pass

    def upload(self, local_path: str, remote_path: str) -> None:
        raise NotImplementedError("Upload is not supported for HTTP storage")

    def list(self, remote_path: str, limit: Optional[int] = None) -> list[str]:
        raise NotImplementedError("List is not supported for HTTP storage")
