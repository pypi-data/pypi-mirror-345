import asyncio
import os

import grpc

from ._middleware import (
    StreamStreamClientServiceAccountMetadataInterceptor,
    StreamUnaryClientServiceAccountMetadataInterceptor,
    UnaryStreamClientServiceAccountMetadataInterceptor,
    UnaryUnaryClientServiceAccountMetadataInterceptor,
)

OBJECT_STORE_ENDPOINT_ENV_VAR = "OBJECT_STORE_ENDPOINT"
MAX_MESSAGE_LENGTH = 100 * 1024 * 1024
COMMON_GRPC_OPTIONS = [
    ("grpc.max_message_length", MAX_MESSAGE_LENGTH),
    ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
    ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
]


def _get_endpoint() -> str:
    env_vars = [OBJECT_STORE_ENDPOINT_ENV_VAR, OBJECT_STORE_ENDPOINT_ENV_VAR.lower()]
    for env_var in env_vars:
        endpoint = os.getenv(env_var)
        if endpoint is not None and endpoint != "":
            return endpoint

    raise ValueError("Unable to find OBJECT_STORE_ENDPOINT")


def _create_channel() -> grpc.aio.Channel:
    endpoint = _get_endpoint()

    interceptors = [
        UnaryUnaryClientServiceAccountMetadataInterceptor(),
        UnaryStreamClientServiceAccountMetadataInterceptor(),
        StreamUnaryClientServiceAccountMetadataInterceptor(),
        StreamStreamClientServiceAccountMetadataInterceptor(),
    ]

    return grpc.aio.insecure_channel(endpoint, options=COMMON_GRPC_OPTIONS, interceptors=interceptors)


def exception_handler(loop: asyncio.AbstractEventLoop, context: dict) -> None:
    """Used by patch_exception_handler to patch BlockingIOError."""
    if (
        "exception" in context
        and type(context["exception"]).__name__ == "BlockingIOError"
        and str(context["exception"]).startswith("[Errno")
    ):
        return
    loop.default_exception_handler(context)


def patch_exception_handler(loop: asyncio.AbstractEventLoop) -> None:
    """Patch exception handler to ignore the `BlockingIOError: [Errno 11] ...` error.

    This is emitted by `aio.grpc` when multiple event loops are used in separate threads.
    This is an issue with grpc's cython implementation of `aio.Channel.__init__` where
    `socket.recv(1)` call only works on the first call. All subsequent calls result in
    an error, but this does not have any impact.

    For more info:
        - https://github.com/grpc/grpc/issues/25364
        - https://github.com/grpc/grpc/pull/36096
    """
    loop.set_exception_handler(exception_handler)


def _get_loop():
    loop = asyncio.new_event_loop()
    patch_exception_handler(loop)
    return loop
