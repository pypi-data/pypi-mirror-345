import asyncio
from contextlib import asynccontextmanager
from functools import partial


@asynccontextmanager
async def async_open(file, *args, **kwargs):
    loop = asyncio.get_running_loop()
    cb = partial(open, file, *args, **kwargs)
    f = await loop.run_in_executor(None, cb)

    try:
        yield f
    finally:
        loop.run_in_executor(None, f.close)
