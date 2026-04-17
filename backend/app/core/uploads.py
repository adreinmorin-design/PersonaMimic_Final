import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import aiofiles
import aiofiles.os
import aiofiles.ospath


@asynccontextmanager
async def uploaded_file(upload, prefix: str = "upload", suffix: str = ".wav"):
    temp_path = Path(tempfile.gettempdir()) / f"{prefix}_{uuid.uuid4()}{suffix}"
    path_text = str(temp_path)
    try:
        async with aiofiles.open(path_text, "wb") as handle:
            await handle.write(await upload.read())
        yield path_text
    finally:
        if await aiofiles.ospath.exists(path_text):
            await aiofiles.os.remove(path_text)
