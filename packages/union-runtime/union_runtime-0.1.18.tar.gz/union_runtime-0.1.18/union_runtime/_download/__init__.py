"""Entrypoint for downloading files."""

import logging
import os

from .._lib.constants import INTERNAL_APP_ENDPOINT_PATTERN_ENV_VAR

logger = logging.getLogger(__name__)


def _generate_url_query_name(app_name: str) -> str:
    pattern = os.getenv(INTERNAL_APP_ENDPOINT_PATTERN_ENV_VAR, "")
    return pattern.replace("{app_fqdn}", app_name)


# Dispatch here to keep dispatching logic simple
_BYOC_PROTOCOLS = ["s3://", "gs://", "abfs://"]
_SERVERLESS_PROTOCOLS = ["union://", "ufs://", "unionmeta://", "ums://"]


def _dispatch_call(method_name: str, uri: str, **kwargs):
    # Dispatch here to keep it simple
    if any(uri.startswith(protocol) for protocol in _BYOC_PROTOCOLS):
        from . import byoc

        return getattr(byoc, method_name)(uri=uri, **kwargs)
    elif any(uri.startswith(protocol) for protocol in _SERVERLESS_PROTOCOLS):
        from . import serverless

        return getattr(serverless, method_name)(uri=uri, **kwargs)
    else:
        raise RuntimeError(f"protocol in {uri} is not supported")


def download_code(uri: str, dest: str):
    logger.debug(f"Downloading code from {uri} to {dest}")
    _dispatch_call("download_code", uri=uri, dest=dest)


def download_single_file(uri: str, dest: str) -> str:
    logger.info(f"Downloading file from {uri} to {dest}")
    return _dispatch_call("download_single_file", uri=uri, dest=dest)


def download_directory(uri: str, dest: str, ignore_patterns: str) -> str:
    logger.info(f"Downloading directory from {uri} to {dest}")
    return _dispatch_call("download_directory", uri=uri, dest=dest, ignore_patterns=ignore_patterns)


def download_inputs(user_inputs: list[dict], dest: str) -> tuple[dict, dict]:
    logger.debug(f"Downloading inputs for {user_inputs}")

    output = {}
    env_vars = {}
    for user_input in user_inputs:
        # Support both download and auto_download to be backward compatible with
        # older union sdk versions
        ignore_patterns = user_input.get("ignore_patterns", [])
        if user_input.get("download", False) or user_input.get("auto_download", False):
            user_dest = user_input["dest"] or dest
            user_dest = os.path.abspath(user_dest)
            if user_input["type"] == "file":
                value = download_single_file(user_input["value"], user_dest)
            elif user_input["type"] == "directory":
                value = download_directory(user_input["value"], user_dest, ignore_patterns)
            else:
                raise ValueError("Can only download files or directories")
        else:
            # Resolve url query
            value = user_input["value"]
            if user_input["type"] == "url_query":
                value = _generate_url_query_name(value)

        output[user_input["name"]] = value

        # Support env_name just to be backward compatible for now
        if user_input.get("env_name", None) is not None:
            env_vars[user_input["env_name"]] = value

        if user_input.get("env_var", None) is not None:
            env_vars[user_input["env_var"]] = value

    return output, env_vars
