"""Messages module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional, Union

import aiohttp

from signal_messenger.models import (
    Message,
    MessageType,
    Reaction,
    Receipt,
    ReceiptType,
    StatusResponse,
)
from signal_messenger.utils import make_request


class MessagesModule:
    """Messages module for the Signal Messenger Python API.

    This module provides access to message sending and receiving functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Messages module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def send_message(
        self,
        number: str,
        message: str,
        recipients: List[str],
        attachments: Optional[List[str]] = None,
        mention_recipients: Optional[List[Dict[str, Any]]] = None,
        quote: Optional[Dict[str, Any]] = None,
        text_mode: Optional[str] = None,
        link_preview: Optional[Dict[str, Any]] = None,
        sticker: Optional[str] = None,
    ) -> Message:
        """Send a message to one or more recipients.

        Args:
            number: The sender's phone number.
            message: The message text.
            recipients: The list of recipient phone numbers.
            attachments: The list of attachment IDs or base64 encoded data (optional).
            mention_recipients: The list of mention recipients (optional).
            quote: The quote information (optional).
            text_mode: The text mode, 'normal' or 'styled' (optional).
            link_preview: Link preview information (optional).
            sticker: Sticker ID (optional).

        Returns:
            The sent message object.
        """
        url = f"{self.base_url}/v2/send"
        data = {
            "number": number,
            "message": message,
            "recipients": recipients,
        }
        if attachments:
            data["base64_attachments"] = attachments
        if mention_recipients:
            data["mentions"] = mention_recipients
        if quote:
            if "author" in quote:
                data["quote_author"] = quote["author"]
            if "message" in quote:
                data["quote_message"] = quote["message"]
            if "timestamp" in quote:
                data["quote_timestamp"] = quote["timestamp"]
            if "mentions" in quote:
                data["quote_mentions"] = quote["mentions"]
        if text_mode:
            data["text_mode"] = text_mode
        if link_preview:
            data["link_preview"] = link_preview
        if sticker:
            data["sticker"] = sticker

        response = await make_request(self._module_session, "POST", url, data=data)

        # Create a Message object from the response
        msg_data = {
            "message": message,
            "source": number,
            "type": MessageType.OUTGOING,
        }

        # Add any additional data from the response
        if isinstance(response, dict):
            msg_data.update({str(k): v for k, v in response.items()})

        return Message(**msg_data)

    async def show_typing_indicator(
        self, number: str, recipient: str
    ) -> StatusResponse:
        """Show a typing indicator to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.

        Returns:
            A status response containing the typing indicator status.
        """
        url = f"{self.base_url}/v1/typing-indicator/{number}"
        data = {"recipient": recipient}
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)

    async def hide_typing_indicator(
        self, number: str, recipient: str
    ) -> StatusResponse:
        """Hide a typing indicator from a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.

        Returns:
            A status response containing the typing indicator status.
        """
        url = f"{self.base_url}/v1/typing-indicator/{number}"
        data = {"recipient": recipient}
        response = await make_request(self._module_session, "DELETE", url, data=data)
        return StatusResponse(**response)

    # Keeping this for backwards compatibility
    async def send_typing_indicator(
        self, number: str, recipient: str, stop: bool = False
    ) -> StatusResponse:
        """Send a typing indicator to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            stop: Whether to stop the typing indicator (default: False).

        Returns:
            A status response containing the typing indicator status, typically {"sent": true}.
        """
        if stop:
            return await self.hide_typing_indicator(number, recipient)
        else:
            return await self.show_typing_indicator(number, recipient)

    async def send_read_receipt(
        self, number: str, recipient: str, timestamps: List[int]
    ) -> Receipt:
        """Send a read receipt to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            timestamps: The list of message timestamps to mark as read.

        Returns:
            The receipt object.
        """
        url = f"{self.base_url}/v1/receipts/{number}"
        data = {
            "receipt_type": "read",
            "recipient": recipient,
            "timestamp": timestamps[0] if timestamps else None,
        }
        response = await make_request(self._module_session, "POST", url, data=data)
        return Receipt(
            type=ReceiptType.READ,
            sender=number,
            sender_uuid=None,
            sender_device=None,
            timestamp=timestamps[0] if timestamps else None,
            when=None,
            **response,
        )

    async def send_viewed_receipt(
        self, number: str, recipient: str, timestamps: List[int]
    ) -> Receipt:
        """Send a viewed receipt to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            timestamps: The list of message timestamps to mark as viewed.

        Returns:
            The receipt object.
        """
        url = f"{self.base_url}/v1/receipts/{number}"
        data = {
            "receipt_type": "viewed",
            "recipient": recipient,
            "timestamp": timestamps[0] if timestamps else None,
        }
        response = await make_request(self._module_session, "POST", url, data=data)
        return Receipt(
            type=ReceiptType.VIEWED,
            sender=number,
            sender_uuid=None,
            sender_device=None,
            timestamp=timestamps[0] if timestamps else None,
            when=None,
            **response,
        )

    async def send_delivery_receipt(
        self, number: str, recipient: str, timestamps: List[int]
    ) -> Receipt:
        """Send a delivery receipt to a recipient.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            timestamps: The list of message timestamps to mark as delivered.

        Returns:
            The receipt object.
        """
        url = f"{self.base_url}/v1/receipts/{number}/{recipient}/delivery"
        data = {"timestamps": timestamps}
        response = await make_request(self._module_session, "PUT", url, data=data)
        return Receipt(
            type=ReceiptType.DELIVERY,
            sender=number,
            sender_uuid=None,
            sender_device=None,
            timestamp=timestamps[0] if timestamps else None,
            when=None,
            **response,
        )

    async def get_messages(
        self, number: str, limit: Optional[int] = None
    ) -> List[Message]:
        """Get messages for a phone number.

        Args:
            number: The registered phone number.
            limit: The maximum number of messages to return (optional).

        Returns:
            A list of messages.
        """
        url = f"{self.base_url}/v1/receive/{number}"
        params = {}
        if limit is not None:
            params["limit"] = limit
        response = await make_request(self._module_session, "GET", url, params=params)

        messages = []
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
        elif isinstance(response, list):
            messages = response
        else:
            messages = [response]

        # Convert messages to Message objects
        result = []
        for msg in messages:
            if isinstance(msg, dict):
                # Convert any non-string keys to strings
                msg_dict = {str(k): v for k, v in msg.items()}
                result.append(Message(**msg_dict))
            elif isinstance(msg, str):
                # Handle case where message is a string
                result.append(Message(message=msg))
            else:
                # Try to convert to Message as is
                result.append(Message(**{"message": str(msg)}))

        return result

    async def delete_message(self, number: str, message_id: str) -> StatusResponse:
        """Delete a message.

        Args:
            number: The registered phone number.
            message_id: The message ID.

        Returns:
            A status response containing the deletion status, typically {"deleted": true}.
        """
        url = f"{self.base_url}/v1/messages/{number}/{message_id}"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)
