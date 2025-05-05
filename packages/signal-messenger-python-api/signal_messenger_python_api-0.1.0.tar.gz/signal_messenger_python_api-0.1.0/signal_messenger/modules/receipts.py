"""Receipts module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional

import aiohttp

from signal_messenger.models import Receipt, StatusResponse
from signal_messenger.utils import make_request


class ReceiptsModule:
    """Receipts module for the Signal Messenger Python API.

    This module provides access to message receipt functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Receipts module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_receipts(
        self, number: str, limit: Optional[int] = None
    ) -> List[Receipt]:
        """Get receipts for a phone number.

        Args:
            number: The registered phone number.
            limit: The maximum number of receipts to return (optional).

        Returns:
            A list of Receipt objects.
        """
        url = f"{self.base_url}/v1/receipts/{number}"
        params = {}
        if limit is not None:
            params["limit"] = limit
        response = await make_request(self._module_session, "GET", url, params=params)

        receipts = []
        if isinstance(response, dict) and "receipts" in response:
            receipts = [Receipt(**receipt) for receipt in response["receipts"]]
        elif isinstance(response, list):
            receipts = [Receipt(**receipt) for receipt in response]
        else:
            receipts = [Receipt(**response)]
        return receipts

    async def get_message_receipts(self, number: str, message_id: str) -> List[Receipt]:
        """Get receipts for a specific message.

        Args:
            number: The registered phone number.
            message_id: The message ID.

        Returns:
            A list of Receipt objects for the message.
        """
        url = f"{self.base_url}/v1/receipts/{number}/messages/{message_id}"
        response = await make_request(self._module_session, "GET", url)

        receipts = []
        if isinstance(response, dict) and "receipts" in response:
            receipts = [Receipt(**receipt) for receipt in response["receipts"]]
        elif isinstance(response, list):
            receipts = [Receipt(**receipt) for receipt in response]
        else:
            receipts = [Receipt(**response)]
        return receipts

    async def send_read_receipt(
        self, number: str, recipient: str, timestamps: List[int]
    ) -> StatusResponse:
        """Send a read receipt to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            timestamps: The list of message timestamps to mark as read.

        Returns:
            A StatusResponse object containing the read receipt information.
        """
        url = f"{self.base_url}/v1/receipts/{number}/{recipient}/read"
        data = {"timestamps": timestamps}
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)

    async def send_viewed_receipt(
        self, number: str, recipient: str, timestamps: List[int]
    ) -> StatusResponse:
        """Send a viewed receipt to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            timestamps: The list of message timestamps to mark as viewed.

        Returns:
            A StatusResponse object containing the viewed receipt information.
        """
        url = f"{self.base_url}/v1/receipts/{number}/{recipient}/viewed"
        data = {"timestamps": timestamps}
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)

    async def send_delivery_receipt(
        self, number: str, recipient: str, timestamps: List[int]
    ) -> StatusResponse:
        """Send a delivery receipt to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            timestamps: The list of message timestamps to mark as delivered.

        Returns:
            A StatusResponse object containing the delivery receipt information.
        """
        url = f"{self.base_url}/v1/receipts/{number}/{recipient}/delivery"
        data = {"timestamps": timestamps}
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)
