import asyncio
import logging
import math
import os
import tarfile
from dataclasses import dataclass
from fnmatch import fnmatch
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

from ..._internal.common.list_pb2 import Filter, ListRequest
from ..._internal.objectstore.definition_pb2 import Key, Metadata
from ..._internal.objectstore.metadata_service_pb2_grpc import MetadataStoreServiceStub
from ..._internal.objectstore.objectstore_service_pb2_grpc import ObjectStoreServiceStub
from ..._internal.objectstore.payload_pb2 import (
    DownloadPartRequest,
    GetRequest,
    GetResponse,
    HeadRequest,
    HeadResponse,
    ListResponse,
    MetadataResponse,
)
from ..._internal.objectstore.payload_pb2 import (
    ListRequest as ObjListRequest,
)
from ..._lib.constants import FILES_TAR_FILE_NAME
from ._async_files import async_open
from ._channel import _create_channel, _get_loop

UNIONFS_META_PROTOCOLS = ["unionmeta://", "ums://"]
UNIONFS_PROTOCOLS = ["union://", "ufs://"]
SUPPORTED_PROTOCOLS = UNIONFS_META_PROTOCOLS + UNIONFS_PROTOCOLS

logger = logging.getLogger(__name__)


async def _download_unionfs_meta_file(uri: str, dest: str, channel):
    client = MetadataStoreServiceStub(channel)
    req = GetRequest(key=Key(key=uri))
    resp = await client.Get(req)

    loop = asyncio.get_running_loop()
    async with async_open(dest, "wb") as f:
        await loop.run_in_executor(None, f.write, resp.object.contents)


async def _download_unionfs_file(uri: str, dest: str, channel):
    """Copy from UnionFS implementation."""
    client = ObjectStoreServiceStub(channel)

    metadata: MetadataResponse = await client.Metadata(Metadata())
    head_resp: HeadResponse = await client.Head(HeadRequest(key=Key(key=uri)))

    loop = asyncio.get_running_loop()
    if head_resp.size_bytes <= metadata.max_single_part_object_size_bytes:
        # Download the whole file
        resp: GetResponse = await client.Get(GetRequest(key=Key(key=uri)))
        async with async_open(dest, "wb") as f:
            await loop.run_in_executor(None, f.write, resp.object.contents)
        return

    num_chunks = math.ceil(head_resp.size_bytes / metadata.max_part_size_bytes)

    async def _download_chunks(start_pos: int = 0, size_bytes: int = -1):
        offset = 0
        async for resp in client.DownloadPart(
            DownloadPartRequest(key=Key(key=uri), start_pos=start_pos, size_bytes=size_bytes)
        ):
            yield (resp.object.contents, offset)
            offset += len(resp.object.contents)

    async def _download_part(dest: str, part_number: int = 0):
        start_pos = part_number * metadata.max_part_size_bytes
        async for chunk, offset in _download_chunks(
            start_pos=start_pos,
            size_bytes=metadata.max_part_size_bytes,
        ):
            async with async_open(dest, "r+b") as file:
                total_offset = start_pos + offset
                await loop.run_in_executor(None, file.seek, total_offset)
                await loop.run_in_executor(None, file.write, chunk)

    await loop.run_in_executor(None, lambda: Path(dest).touch())
    await loop.run_in_executor(None, os.truncate, dest, head_resp.size_bytes)
    out = []
    for chunk_id in range(0, num_chunks):
        out.append(_download_part(dest, part_number=chunk_id))

    await asyncio.gather(*out)


async def _download_file(uri: str, dest: str, channel=None):
    if channel is None:
        channel = _create_channel()
    if any(uri.startswith(p) for p in UNIONFS_META_PROTOCOLS):
        await _download_unionfs_meta_file(uri, dest, channel=channel)
    elif any(uri.startswith(p) for p in UNIONFS_PROTOCOLS):
        await _download_unionfs_file(uri, dest, channel=channel)
    else:
        raise RuntimeError(f"protocol in {uri} is not supported")


@dataclass
class RemoteObject:
    uri: str
    is_file: bool


async def _list_obj(remote_obj: RemoteObject, channel):
    client = ObjectStoreServiceStub(channel)

    uri = remote_obj.uri
    req = ObjListRequest(
        request=ListRequest(filters=[Filter(field="prefix", function=Filter.GREATER_THAN_OR_EQUAL, values=[uri])])
    )

    while True:
        res: ListResponse = await client.List(req)
        for k in res.keys:
            yield RemoteObject(uri=k.key, is_file=True)
        for d in res.directories:
            async for remote_obj in _list_obj(RemoteObject(uri=d.key, is_file=False), channel=channel):
                yield remote_obj

        if not res.next_token or res.next_token == "":
            break


async def _download_directory(directory_uri: str, dest: str, ignore_patterns: list[str]):
    if not directory_uri.endswith("/"):
        directory_uri = directory_uri + "/"
    prefix_len = len(directory_uri)

    loop = asyncio.get_running_loop()
    channel = _create_channel()
    results = _list_obj(RemoteObject(uri=directory_uri, is_file=False), channel=channel)

    async for result in results:
        uri = result.uri

        found_ignore_pattern = any(fnmatch(uri, pattern) for pattern in ignore_patterns)
        if found_ignore_pattern:
            continue

        assert uri.startswith(directory_uri)
        rel_path = uri[prefix_len:]
        dest_path = os.path.join(dest, rel_path)

        dirname = os.path.dirname(dest_path)
        mkdir = partial(os.makedirs, dirname, exist_ok=True)
        await loop.run_in_executor(None, mkdir)

        logger.info(f"Downloading file from {uri} to {dest_path}")
        await _download_file(uri, dest_path, channel=channel)


def _extract_path(uri: str) -> str:
    for supported_protocol in SUPPORTED_PROTOCOLS:
        if uri.startswith(supported_protocol):
            n_supported_protocol = len(supported_protocol)
            return uri[n_supported_protocol:]

    raise ValueError(f"{uri} has an unsupported protocol")


def download_code(uri: str, dest: str):
    # Simplify when Python 3.12+ only, by always setting the `extract_kwargs`
    # https://docs.python.org/3.12/library/tarfile.html#extraction-filters
    extract_kwargs = {}
    if hasattr(tarfile, "data_filter"):
        extract_kwargs["filter"] = "data"

    loop = _get_loop()

    with TemporaryDirectory() as temp_dir:
        temp_dest = os.path.join(temp_dir, FILES_TAR_FILE_NAME)
        loop.run_until_complete(_download_file(uri, temp_dest))

        with tarfile.open(temp_dest, "r:gz") as tar:
            tar.extractall(path=dest, **extract_kwargs)


def download_single_file(uri: str, dest: str) -> str:
    path_name = _extract_path(uri)
    os.makedirs(dest, exist_ok=True)
    basename = os.path.basename(path_name)
    dest_path = os.path.join(dest, basename)

    loop = _get_loop()
    loop.run_until_complete(_download_file(uri, dest_path))
    return dest_path


def download_directory(uri: str, dest: str, ignore_patterns: list[str]) -> str:
    loop = _get_loop()
    loop.run_until_complete(_download_directory(uri, dest, ignore_patterns))
    return dest
