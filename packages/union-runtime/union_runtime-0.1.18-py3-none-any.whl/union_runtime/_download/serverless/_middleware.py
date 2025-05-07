from functools import cache
from logging import getLogger
from typing import Any, AsyncIterable, AsyncIterator, Callable, Optional

import grpc

logger = getLogger(__name__)

DEFAULT_KUBERNETES_TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"


@cache
def read_service_account_token() -> Optional[str]:
    try:
        with open(DEFAULT_KUBERNETES_TOKEN_PATH, "r") as token_file:
            return token_file.read()
    except Exception as e:
        logger.debug(f"Error reading service account token: {e}, not adding to request")
        return None


def _inject_default_metadata(
    client_call_details: grpc.aio.ClientCallDetails,
) -> grpc.aio.ClientCallDetails:
    service_account_toekn = read_service_account_token()
    if service_account_toekn is None:
        return client_call_details

    old_metadata = client_call_details.metadata or []
    new_metadata = old_metadata + [("authorization", f"Bearer {service_account_toekn}")]

    new_details = grpc.aio.ClientCallDetails(
        method=client_call_details.method,
        timeout=client_call_details.timeout,
        metadata=new_metadata,
        credentials=client_call_details.credentials,
        wait_for_ready=client_call_details.wait_for_ready,
    )
    return new_details


class UnaryUnaryClientServiceAccountMetadataInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request: Any,
    ) -> Any:
        new_client_call_details = _inject_default_metadata(client_call_details)
        return await continuation(new_client_call_details, request)


class UnaryStreamClientServiceAccountMetadataInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    async def intercept_unary_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request: any,
    ) -> AsyncIterable:
        new_client_call_details = _inject_default_metadata(client_call_details)
        return await continuation(new_client_call_details, request)


class StreamUnaryClientServiceAccountMetadataInterceptor(grpc.aio.StreamUnaryClientInterceptor):
    async def intercept_stream_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: any,
    ) -> grpc.aio.StreamUnaryCall:
        new_client_call_details = _inject_default_metadata(client_call_details)
        return await continuation(new_client_call_details, request_iterator)


class StreamStreamClientServiceAccountMetadataInterceptor(grpc.aio.StreamStreamClientInterceptor):
    async def intercept_stream_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: AsyncIterator,
    ) -> grpc.aio.Call:
        new_client_call_details = _inject_default_metadata(client_call_details)
        return await continuation(new_client_call_details, request_iterator)
