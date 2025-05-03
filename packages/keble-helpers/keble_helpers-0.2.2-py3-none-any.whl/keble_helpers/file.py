import logging
import os.path
from pathlib import Path

import aiohttp
import keble_exceptions
from tenacity import retry, stop_after_attempt

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), reraise=True)
async def adownload_file(*, url: str, folder: Path, filename: str) -> Path:
    """Downloads an file from a URL and saves it to the specified folder."""
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / filename
    if os.path.exists(filepath):
        # file already loaded and existed
        return filepath
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filepath, "wb") as f:
                    f.write(await response.read())
                return filepath
            else:
                raise keble_exceptions.RequestFailure(
                    admin_note={
                        "url": url,
                        "folder": str(folder),
                        "filename": filename,
                    },
                    alert_admin=True,
                    function_identifier="keble_helpers.download_file",
                )
                # raise Exception(
                #     f"[Helpers] Failed to download {url}: HTTP {response.status}"
                # )
