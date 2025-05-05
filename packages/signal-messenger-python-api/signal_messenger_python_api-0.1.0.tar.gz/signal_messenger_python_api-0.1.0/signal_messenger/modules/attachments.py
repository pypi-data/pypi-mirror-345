"""Attachments module for the Signal Messenger Python API."""

import http
from typing import Any, BinaryIO, Dict, List, Optional, Union

import aiohttp

from signal_messenger.models import Attachment, StatusResponse
from signal_messenger.utils import make_request


class AttachmentsModule:
    """Attachments module for the Signal Messenger Python API.

    This module provides access to attachment management functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Attachments module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def upload_attachment(
        self, number: str, file_data: Union[bytes, BinaryIO], content_type: str
    ) -> Attachment:
        """Upload an attachment.

        Args:
            number: The registered phone number.
            file_data: The file data as bytes or a file-like object.
            content_type: The content type of the file.

        Returns:
            The uploaded attachment.
        """
        url = f"{self.base_url}/v1/attachments/{number}"
        headers = {"Content-Type": content_type}

        # Use the session directly for binary data
        async with self._module_session.post(
            url, data=file_data, headers=headers
        ) as response:
            from signal_messenger.utils import handle_response

            response_data = await handle_response(response)

            # Create an Attachment object from the response
            if isinstance(response_data, dict):
                # Convert any non-string keys to strings
                attachment_dict = {str(k): v for k, v in response_data.items()}
                # Add content_type if not in the response
                if "content_type" not in attachment_dict:
                    attachment_dict["content_type"] = content_type
                return Attachment(**attachment_dict)
            else:
                # Try to create a minimal Attachment object
                return Attachment(id=str(response_data), content_type=content_type)

    async def get_attachment(self, number: str, attachment_id: str) -> bytes:
        """Get an attachment.

        Args:
            number: The registered phone number.
            attachment_id: The attachment ID.

        Returns:
            The attachment data as bytes.
        """
        url = f"{self.base_url}/v1/attachments/{number}/{attachment_id}"
        async with self._module_session.get(url) as response:
            if response.status != http.HTTPStatus.OK:
                # Handle error response
                error_data = await response.json()
                error_message = error_data.get("error", "Unknown error")
                raise Exception(f"Failed to get attachment: {error_message}")
            return await response.read()

    async def delete_attachment(
        self, number: str, attachment_id: str
    ) -> StatusResponse:
        """Delete an attachment.

        Args:
            number: The registered phone number.
            attachment_id: The attachment ID.

        Returns:
            A status response containing the attachment deletion information.
        """
        url = f"{self.base_url}/v1/attachments/{number}/{attachment_id}"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)

    async def get_attachment_info(self, number: str, attachment_id: str) -> Attachment:
        """Get information about an attachment.

        Args:
            number: The registered phone number.
            attachment_id: The attachment ID.

        Returns:
            The attachment information.
        """
        url = f"{self.base_url}/v1/attachments/{number}/{attachment_id}/info"
        response = await make_request(self._module_session, "GET", url)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            attachment_dict = {str(k): v for k, v in response.items()}
            # Add the attachment_id if not in the response
            if "id" not in attachment_dict:
                attachment_dict["id"] = attachment_id
            return Attachment(**attachment_dict)
        else:
            # Try to create a minimal Attachment object
            return Attachment(id=attachment_id)

    async def get_attachments(self, number: str) -> List[Attachment]:
        """Get all attachments for a phone number.

        Args:
            number: The registered phone number.

        Returns:
            A list of attachments.
        """
        url = f"{self.base_url}/v1/attachments/{number}"
        response = await make_request(self._module_session, "GET", url)

        attachments = []
        if isinstance(response, dict) and "attachments" in response:
            attachments = response["attachments"]
        elif isinstance(response, list):
            attachments = response
        else:
            attachments = [response]

        # Convert attachments to Attachment objects
        result = []
        for attachment in attachments:
            if isinstance(attachment, dict):
                # Convert any non-string keys to strings
                attachment_dict = {str(k): v for k, v in attachment.items()}
                result.append(Attachment(**attachment_dict))
            else:
                # Try to create a minimal Attachment object
                result.append(Attachment(id=str(attachment)))

        return result
