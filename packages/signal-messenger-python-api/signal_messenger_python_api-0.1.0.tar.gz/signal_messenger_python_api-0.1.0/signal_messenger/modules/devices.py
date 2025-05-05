"""Devices module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional

import aiohttp

from signal_messenger.models import Device, LinkedDevice, StatusResponse
from signal_messenger.utils import make_request


class DevicesModule:
    """Devices module for the Signal Messenger Python API.

    This module provides access to device registration and linking functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Devices module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_linked_devices(self, number: str) -> List[LinkedDevice]:
        """Get linked devices for a phone number.

        Args:
            number: The registered phone number.

        Returns:
            A list of linked devices.
        """
        url = f"{self.base_url}/v1/devices/{number}"
        response = await make_request(self._module_session, "GET", url)
        devices = []
        if isinstance(response, dict) and "devices" in response:
            devices = [LinkedDevice(**device) for device in response["devices"]]
        elif isinstance(response, list):
            devices = [LinkedDevice(**device) for device in response]
        else:
            devices = [LinkedDevice(**response)]
        return devices

    async def link_device(self, number: str, device_name: str) -> StatusResponse:
        """Link another device to this device.

        Args:
            number: The registered phone number.
            device_name: The name of the device to link.

        Returns:
            The response containing the linking information.
        """
        url = f"{self.base_url}/v1/devices/{number}"
        data = {"name": device_name}
        response = await make_request(self._module_session, "POST", url, data=data)
        return StatusResponse(**response)

    async def get_qr_code_link(self, device_name: str = "") -> Dict[str, Any]:
        """Get a QR code link for device linking.

        Args:
            device_name: The name of the device to link.

        Returns:
            The response containing the QR code link.
        """
        url = f"{self.base_url}/v1/qrcodelink"
        params = {}
        if device_name:
            params["name"] = device_name
        response = await make_request(self._module_session, "GET", url, params=params)
        return response  # Keep as Dict since there's no specific model for QR code response

    async def register_device(self, number: str) -> StatusResponse:
        """Register a phone number.

        Args:
            number: The phone number to register.

        Returns:
            The response containing the registration information.
        """
        url = f"{self.base_url}/v1/register/{number}"
        response = await make_request(self._module_session, "POST", url)
        return StatusResponse(**response)

    async def verify_device(self, number: str, token: str) -> StatusResponse:
        """Verify a registered phone number.

        Args:
            number: The registered phone number.
            token: The verification token.

        Returns:
            The response containing the verification information.
        """
        url = f"{self.base_url}/v1/register/{number}/verify/{token}"
        response = await make_request(self._module_session, "POST", url)
        return StatusResponse(**response)
