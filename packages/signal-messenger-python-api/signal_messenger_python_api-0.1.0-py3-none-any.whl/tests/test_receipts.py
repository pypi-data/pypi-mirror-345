"""Tests for the Receipts module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.models import Receipt, ReceiptType, StatusResponse
from signal_messenger.modules.receipts import ReceiptsModule


@pytest.fixture
def receipts_module():
    """Create a ReceiptsModule instance for testing."""
    session = AsyncMock()
    return ReceiptsModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_get_receipts(receipts_module):
    """Test the get_receipts method."""
    # Mock response data
    response_data = {
        "receipts": [
            {
                "id": "receipt1",
                "type": "read",
                "sender": "+0987654321",
                "timestamp": 1234567890,
                "targetTimestamp": 1234567889,
            },
            {
                "id": "receipt2",
                "type": "delivery",
                "sender": "+5555555555",
                "timestamp": 1234567891,
                "targetTimestamp": 1234567889,
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.receipts.make_request", return_value=response_data
    ):
        # Call the method
        result = await receipts_module.get_receipts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Receipt)
        assert result[0].type == ReceiptType.READ
        assert result[0].sender == "+0987654321"
        assert isinstance(result[1], Receipt)
        assert result[1].type == ReceiptType.DELIVERY
        assert result[1].sender == "+5555555555"


@pytest.mark.asyncio
async def test_get_receipts_with_limit(receipts_module):
    """Test the get_receipts method with limit."""
    # Mock response data
    response_data = {
        "receipts": [
            {
                "id": "receipt1",
                "type": "read",
                "sender": "+0987654321",
                "timestamp": 1234567890,
                "targetTimestamp": 1234567889,
            }
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.receipts.make_request", make_request_mock):
        # Call the method
        result = await receipts_module.get_receipts("+1234567890", limit=1)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Receipt)
        assert result[0].type == ReceiptType.READ
        assert result[0].sender == "+0987654321"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            receipts_module._module_session,
            "GET",
            "http://localhost:8080/v1/receipts/+1234567890",
            params={"limit": 1},
        )


@pytest.mark.asyncio
async def test_get_receipts_list_response(receipts_module):
    """Test the get_receipts method with a list response."""
    # Mock response data
    response_data = [
        {
            "id": "receipt1",
            "type": "read",
            "sender": "+0987654321",
            "timestamp": 1234567890,
            "targetTimestamp": 1234567889,
        },
        {
            "id": "receipt2",
            "type": "delivery",
            "sender": "+5555555555",
            "timestamp": 1234567891,
            "targetTimestamp": 1234567889,
        },
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.receipts.make_request", return_value=response_data
    ):
        # Call the method
        result = await receipts_module.get_receipts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Receipt)
        assert result[0].type == ReceiptType.READ
        assert result[0].sender == "+0987654321"
        assert isinstance(result[1], Receipt)
        assert result[1].type == ReceiptType.DELIVERY
        assert result[1].sender == "+5555555555"


@pytest.mark.asyncio
async def test_get_receipts_single_response(receipts_module):
    """Test the get_receipts method with a single receipt response."""
    # Mock response data
    response_data = {
        "id": "receipt1",
        "type": "read",
        "sender": "+0987654321",
        "timestamp": 1234567890,
        "targetTimestamp": 1234567889,
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.receipts.make_request", return_value=response_data
    ):
        # Call the method
        result = await receipts_module.get_receipts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Receipt)
        assert result[0].type == ReceiptType.READ
        assert result[0].sender == "+0987654321"


@pytest.mark.asyncio
async def test_get_message_receipts(receipts_module):
    """Test the get_message_receipts method."""
    # Mock response data
    response_data = {
        "receipts": [
            {
                "id": "receipt1",
                "type": "read",
                "sender": "+0987654321",
                "timestamp": 1234567890,
                "targetTimestamp": 1234567889,
            },
            {
                "id": "receipt2",
                "type": "delivery",
                "sender": "+5555555555",
                "timestamp": 1234567891,
                "targetTimestamp": 1234567889,
            },
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.receipts.make_request", make_request_mock):
        # Call the method
        result = await receipts_module.get_message_receipts("+1234567890", "message1")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Receipt)
        assert result[0].type == ReceiptType.READ
        assert result[0].sender == "+0987654321"
        assert isinstance(result[1], Receipt)
        assert result[1].type == ReceiptType.DELIVERY
        assert result[1].sender == "+5555555555"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            receipts_module._module_session,
            "GET",
            "http://localhost:8080/v1/receipts/+1234567890/messages/message1",
        )


@pytest.mark.asyncio
async def test_send_read_receipt(receipts_module):
    """Test the send_read_receipt method."""
    # Mock response data
    response_data = {"success": True, "message": "Read receipt sent"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.receipts.make_request", make_request_mock):
        # Call the method
        result = await receipts_module.send_read_receipt(
            "+1234567890", "+0987654321", [1234567890, 1234567891]
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Read receipt sent"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            receipts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/receipts/+1234567890/+0987654321/read",
            data={"timestamps": [1234567890, 1234567891]},
        )


@pytest.mark.asyncio
async def test_send_viewed_receipt(receipts_module):
    """Test the send_viewed_receipt method."""
    # Mock response data
    response_data = {"success": True, "message": "Viewed receipt sent"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.receipts.make_request", make_request_mock):
        # Call the method
        result = await receipts_module.send_viewed_receipt(
            "+1234567890", "+0987654321", [1234567890]
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Viewed receipt sent"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            receipts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/receipts/+1234567890/+0987654321/viewed",
            data={"timestamps": [1234567890]},
        )


@pytest.mark.asyncio
async def test_send_delivery_receipt(receipts_module):
    """Test the send_delivery_receipt method."""
    # Mock response data
    response_data = {"success": True, "message": "Delivery receipt sent"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.receipts.make_request", make_request_mock):
        # Call the method
        result = await receipts_module.send_delivery_receipt(
            "+1234567890", "+0987654321", [1234567890]
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Delivery receipt sent"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            receipts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/receipts/+1234567890/+0987654321/delivery",
            data={"timestamps": [1234567890]},
        )
