import logging
import os
import tarfile
from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from urllib.parse import urlparse

import obstore

from .._lib.constants import FILES_TAR_FILE_NAME

DEFAULT_CHUNK_SIZE = 10 * 1024 * 1024

logger = logging.getLogger(__name__)


def _extract_bucket_and_path(uri: str) -> tuple[str, str]:
    parsed_uri = urlparse(uri)
    bucket_uri = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
    path_name = parsed_uri.path.lstrip("/")

    return bucket_uri, path_name


def _download_chunk(store, path_name: str, start: int, end: int):
    failed_reads = 0
    while True:
        try:
            return obstore.get_range(store, path_name, start=start, end=end)
        except Exception:
            failed_reads += 1
            sleep(min(1.7**failed_reads * 0.1, 15))
            continue


def _download_chunk_and_write(store, file, path_name: str, start: int, end: int):
    data = _download_chunk(store, path_name, start, end)
    with open(file, "r+b") as f:
        f.seek(start)
        f.write(data)


def _download_file(store, path_name: str, dest: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
    """Download a single file from path_name to dest."""
    meta = obstore.head(store, path_name)
    size = meta["size"]

    n_chunks = size // chunk_size

    Path(dest).touch()
    # Allocate space to write file into memory
    os.truncate(dest, size)

    with ThreadPoolExecutor() as executor:
        for n_chunk in range(n_chunks):
            start = n_chunk * chunk_size
            end = start + chunk_size
            executor.submit(_download_chunk_and_write, store, dest, path_name, start, end)

        # This is a remainder
        remainder = size % chunk_size
        if remainder > 0:
            start = n_chunks * chunk_size
            end = start + remainder
            executor.submit(_download_chunk_and_write, store, dest, path_name, start, end)


@cache
def get_store(url):
    for maybe_store in (
        obstore.store.S3Store,
        obstore.store.GCSStore,
        obstore.store.AzureStore,
    ):
        try:
            return maybe_store.from_url(url)
        except obstore.exceptions.ObstoreError:
            pass
    raise ValueError(f"Could not find valid store for URL: {url}. Must be an S3, GCS, or Azure URI")


def download_code(uri: str, dest: str):
    bucket_uri, path_name = _extract_bucket_and_path(uri)

    store = get_store(bucket_uri)

    # Simplify when Python 3.12+ only, by always setting the `extract_kwargs`
    # https://docs.python.org/3.12/library/tarfile.html#extraction-filters
    extract_kwargs = {}
    if hasattr(tarfile, "data_filter"):
        extract_kwargs["filter"] = "data"

    with TemporaryDirectory() as temp_dir:
        temp_dest = os.path.join(temp_dir, FILES_TAR_FILE_NAME)
        _download_file(store, path_name, temp_dest)

        with tarfile.open(temp_dest, "r:gz") as tar:
            tar.extractall(path=dest, **extract_kwargs)


def download_single_file(uri: str, dest: str) -> str:
    bucket_uri, path_name = _extract_bucket_and_path(uri)

    os.makedirs(dest, exist_ok=True)
    basename = os.path.basename(path_name)
    dest_path = os.path.join(dest, basename)

    store = get_store(bucket_uri)

    _download_file(store, path_name, dest_path)
    return dest_path


def download_directory(uri: str, dest: str, ignore_patterns: list[str]) -> str:
    bucket_uri, path_name = _extract_bucket_and_path(uri)

    store = get_store(bucket_uri)
    all_records = obstore.list(store, prefix=path_name)
    for records in all_records:
        for record in records:
            src = record["path"]

            found_ignore_pattern = any(fnmatch(src, pattern) for pattern in ignore_patterns)
            if found_ignore_pattern:
                continue
            rel_dest_path = os.path.relpath(src, path_name)
            dest_path = os.path.join(dest, rel_dest_path)

            dirname = os.path.dirname(dest_path)
            os.makedirs(dirname, exist_ok=True)

            logger.info(f"Downloading file from {bucket_uri}/{src} to {dest_path}")
            _download_file(store, src, dest_path)

    return dest
