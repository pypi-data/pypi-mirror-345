"""Tests for the Devices module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.models import LinkedDevice, StatusResponse
from signal_messenger.modules.devices import DevicesModule


@pytest.fixture
def devices_module():
    """Create a DevicesModule instance for testing."""
    session = AsyncMock()
    return DevicesModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_get_linked_devices(devices_module):
    """Test the get_linked_devices method."""
    # Mock response data
    response_data = {
        "devices": [
            {"id": 1, "name": "Primary Device", "created": "2023-01-01T00:00:00Z"},
            {"id": 2, "name": "Secondary Device", "created": "2023-01-02T00:00:00Z"},
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.devices.make_request", return_value=response_data
    ):
        # Call the method
        result = await devices_module.get_linked_devices("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], LinkedDevice)
        assert result[0].id == 1
        assert result[0].name == "Primary Device"
        assert isinstance(result[1], LinkedDevice)
        assert result[1].id == 2
        assert result[1].name == "Secondary Device"


@pytest.mark.asyncio
async def test_get_linked_devices_list_response(devices_module):
    """Test the get_linked_devices method with a list response."""
    # Mock response data
    response_data = [
        {"id": 1, "name": "Primary Device", "created": "2023-01-01T00:00:00Z"},
        {"id": 2, "name": "Secondary Device", "created": "2023-01-02T00:00:00Z"},
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.devices.make_request", return_value=response_data
    ):
        # Call the method
        result = await devices_module.get_linked_devices("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], LinkedDevice)
        assert result[0].id == 1
        assert result[0].name == "Primary Device"
        assert isinstance(result[1], LinkedDevice)
        assert result[1].id == 2
        assert result[1].name == "Secondary Device"


@pytest.mark.asyncio
async def test_get_linked_devices_single_response(devices_module):
    """Test the get_linked_devices method with a single device response."""
    # Mock response data
    response_data = {
        "id": 1,
        "name": "Primary Device",
        "created": "2023-01-01T00:00:00Z",
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.devices.make_request", return_value=response_data
    ):
        # Call the method
        result = await devices_module.get_linked_devices("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], LinkedDevice)
        assert result[0].id == 1
        assert result[0].name == "Primary Device"


@pytest.mark.asyncio
async def test_link_device(devices_module):
    """Test the link_device method."""
    # Mock response data
    response_data = {"success": True, "message": "Device linked successfully"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.devices.make_request", make_request_mock):
        # Call the method
        result = await devices_module.link_device("+1234567890", "New Device")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Device linked successfully"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            devices_module._module_session,
            "POST",
            "http://localhost:8080/v1/devices/+1234567890",
            data={"name": "New Device"},
        )


@pytest.mark.asyncio
async def test_get_qr_code_link(devices_module):
    """Test the get_qr_code_link method."""
    # Mock response data
    response_data = {"url": "https://example.com/qrcode"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.devices.make_request", make_request_mock):
        # Call the method with a device name
        result = await devices_module.get_qr_code_link("Test Device")

        # Verify the result
        assert isinstance(result, dict)
        assert result["url"] == "https://example.com/qrcode"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            devices_module._module_session,
            "GET",
            "http://localhost:8080/v1/qrcodelink",
            params={"name": "Test Device"},
        )


@pytest.mark.asyncio
async def test_get_qr_code_link_no_name(devices_module):
    """Test the get_qr_code_link method without a device name."""
    # Mock response data
    response_data = {"url": "https://example.com/qrcode"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.devices.make_request", make_request_mock):
        # Call the method without a device name
        result = await devices_module.get_qr_code_link()

        # Verify the result
        assert isinstance(result, dict)
        assert result["url"] == "https://example.com/qrcode"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            devices_module._module_session,
            "GET",
            "http://localhost:8080/v1/qrcodelink",
            params={},
        )


@pytest.mark.asyncio
async def test_register_device(devices_module):
    """Test the register_device method."""
    # Mock response data
    response_data = {"success": True, "message": "Registration initiated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.devices.make_request", make_request_mock):
        # Call the method
        result = await devices_module.register_device("+1234567890")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Registration initiated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            devices_module._module_session,
            "POST",
            "http://localhost:8080/v1/register/+1234567890",
        )


@pytest.mark.asyncio
async def test_verify_device(devices_module):
    """Test the verify_device method."""
    # Mock response data
    response_data = {"success": True, "message": "Verification successful"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.devices.make_request", make_request_mock):
        # Call the method
        result = await devices_module.verify_device("+1234567890", "123456")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Verification successful"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            devices_module._module_session,
            "POST",
            "http://localhost:8080/v1/register/+1234567890/verify/123456",
        )
