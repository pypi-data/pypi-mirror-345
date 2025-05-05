"""Utility functions for the Signal Messenger Python API."""

import http
import json
from typing import Any, Dict, Optional, Union

import aiohttp
from aiohttp import ClientResponse

from signal_messenger.exceptions import (
    SignalAPIError,
    SignalAuthenticationError,
    SignalBadRequestError,
    SignalConnectionError,
    SignalNotFoundError,
    SignalServerError,
    SignalTimeoutError,
)


async def handle_response(response: ClientResponse) -> Dict[str, Any]:
    """Handle the API response.

    Args:
        response: The response from the API.

    Returns:
        The response data as a dictionary.

    Raises:
        SignalBadRequestError: If the request is malformed.
        SignalAuthenticationError: If there is an authentication error.
        SignalNotFoundError: If the resource is not found.
        SignalServerError: If there is a server error.
        SignalAPIError: If there is another API error.
    """
    try:
        if response.content_type == "application/json":
            data = await response.json()
        else:
            text = await response.text()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = {"text": text}
    except Exception as e:
        raise SignalAPIError(f"Failed to parse response: {str(e)}", response.status)

    if http.HTTPStatus.OK <= response.status < http.HTTPStatus.MULTIPLE_CHOICES:
        return data

    error_message = data.get("error", "Unknown error")

    if response.status == http.HTTPStatus.BAD_REQUEST:
        raise SignalBadRequestError(error_message, response.status, data)
    elif response.status == http.HTTPStatus.UNAUTHORIZED:
        raise SignalAuthenticationError(error_message, response.status, data)
    elif response.status == http.HTTPStatus.NOT_FOUND:
        raise SignalNotFoundError(error_message, response.status, data)
    elif http.HTTPStatus.INTERNAL_SERVER_ERROR <= response.status < 600:
        raise SignalServerError(error_message, response.status, data)
    else:
        raise SignalAPIError(error_message, response.status, data)


async def make_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Make a request to the API.

    Args:
        session: The aiohttp session.
        method: The HTTP method.
        url: The URL to request.
        params: The query parameters.
        data: The request body.
        headers: The request headers.

    Returns:
        The response data as a dictionary.

    Raises:
        SignalConnectionError: If there is a connection error.
        SignalTimeoutError: If the request times out.
        SignalAPIError: If there is another API error.
    """
    if headers is None:
        headers = {}

    if isinstance(data, dict):
        headers["Content-Type"] = "application/json"
        data = json.dumps(data)

    try:
        async with session.request(
            method, url, params=params, data=data, headers=headers
        ) as response:
            return await handle_response(response)
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            raise SignalConnectionError(f"Connection error: {str(e)}")
        elif isinstance(e, aiohttp.ClientResponseError):
            if hasattr(e, "status") and e.status == http.HTTPStatus.REQUEST_TIMEOUT:
                raise SignalTimeoutError(f"Request timed out: {str(e)}")
            else:
                raise SignalAPIError(f"Request failed: {str(e)}")
        elif isinstance(e, aiohttp.ClientError):
            raise SignalAPIError(f"Request failed: {str(e)}")
        else:
            raise
