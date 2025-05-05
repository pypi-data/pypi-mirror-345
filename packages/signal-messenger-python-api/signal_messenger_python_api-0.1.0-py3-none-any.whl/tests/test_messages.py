"""Tests for the Messages module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.modules.messages import MessagesModule


@pytest.fixture
def messages_module():
    """Create a MessagesModule instance for testing."""
    session = AsyncMock()
    return MessagesModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_send_message(messages_module):
    """Test the send_message method."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_message(
            "+1234567890", "Hello, world!", ["+0987654321"]
        )

        # Verify the result
        assert result["success"] is True
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v2/send",
            data={
                "number": "+1234567890",
                "message": "Hello, world!",
                "recipients": ["+0987654321"],
            },
        )


@pytest.mark.asyncio
async def test_send_message_with_attachments(messages_module):
    """Test the send_message method with attachments."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_message(
            "+1234567890",
            "Hello, world!",
            ["+0987654321"],
            attachments=["attachment1", "attachment2"],
        )

        # Verify the result
        assert result["success"] is True
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v2/send",
            data={
                "number": "+1234567890",
                "message": "Hello, world!",
                "recipients": ["+0987654321"],
                "base64_attachments": ["attachment1", "attachment2"],
            },
        )


@pytest.mark.asyncio
async def test_send_message_with_mentions(messages_module):
    """Test the send_message method with mentions."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        mentions = [{"name": "John", "number": "+0987654321", "start": 0, "length": 4}]
        result = await messages_module.send_message(
            "+1234567890",
            "Hello, world!",
            ["+0987654321"],
            mention_recipients=mentions,
        )

        # Verify the result
        assert result["success"] is True
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v2/send",
            data={
                "number": "+1234567890",
                "message": "Hello, world!",
                "recipients": ["+0987654321"],
                "mentions": mentions,
            },
        )


@pytest.mark.asyncio
async def test_send_message_with_quote(messages_module):
    """Test the send_message method with quote."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        quote = {
            "id": 1234567890,
            "author": "+0987654321",
            "text": "Original message",
        }
        result = await messages_module.send_message(
            "+1234567890", "Hello, world!", ["+0987654321"], quote=quote
        )

        # Verify the result
        assert result["success"] is True
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v2/send",
            data={
                "number": "+1234567890",
                "message": "Hello, world!",
                "recipients": ["+0987654321"],
                "quote_author": "+0987654321",
            },
        )


@pytest.mark.asyncio
async def test_send_typing_indicator(messages_module):
    """Test the send_typing_indicator method."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_typing_indicator(
            "+1234567890", "+0987654321"
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call - should use the new show_typing_indicator method
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "PUT",
            "http://localhost:8080/v1/typing-indicator/+1234567890",
            data={"recipient": "+0987654321"},
        )


@pytest.mark.asyncio
async def test_send_typing_indicator_stop(messages_module):
    """Test the send_typing_indicator method with stop=True."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_typing_indicator(
            "+1234567890", "+0987654321", stop=True
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call - should use the new hide_typing_indicator method
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/typing-indicator/+1234567890",
            data={"recipient": "+0987654321"},
        )


@pytest.mark.asyncio
async def test_send_read_receipt(messages_module):
    """Test the send_read_receipt method."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_read_receipt(
            "+1234567890", "+0987654321", [1234567890, 1234567891]
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call - should use the new API format
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v1/receipts/+1234567890",
            data={
                "receipt_type": "read",
                "recipient": "+0987654321",
                "timestamp": 1234567890,
            },
        )


@pytest.mark.asyncio
async def test_send_viewed_receipt(messages_module):
    """Test the send_viewed_receipt method."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_viewed_receipt(
            "+1234567890", "+0987654321", [1234567890]
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call - should use the new API format
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v1/receipts/+1234567890",
            data={
                "receipt_type": "viewed",
                "recipient": "+0987654321",
                "timestamp": 1234567890,
            },
        )


@pytest.mark.asyncio
async def test_send_delivery_receipt(messages_module):
    """Test the send_delivery_receipt method."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_delivery_receipt(
            "+1234567890", "+0987654321", [1234567890]
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "PUT",
            "http://localhost:8080/v1/receipts/+1234567890/+0987654321/delivery",
            data={"timestamps": [1234567890]},
        )


@pytest.mark.asyncio
async def test_get_messages(messages_module):
    """Test the get_messages method."""
    # Mock response data
    response_data = {
        "messages": [
            {
                "id": "msg1",
                "source": "+0987654321",
                "timestamp": 1234567890,
                "message": "Hello, world!",
            },
            {
                "id": "msg2",
                "source": "+0987654321",
                "timestamp": 1234567891,
                "message": "How are you?",
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.messages.make_request", return_value=response_data
    ):
        # Call the method
        result = await messages_module.get_messages("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "msg1"
        assert result[0]["message"] == "Hello, world!"
        assert result[1]["id"] == "msg2"
        assert result[1]["message"] == "How are you?"


@pytest.mark.asyncio
async def test_get_messages_with_limit(messages_module):
    """Test the get_messages method with limit."""
    # Mock response data
    response_data = {
        "messages": [
            {
                "id": "msg1",
                "source": "+0987654321",
                "timestamp": 1234567890,
                "message": "Hello, world!",
            }
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.get_messages("+1234567890", limit=1)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "msg1"
        assert result[0]["message"] == "Hello, world!"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "GET",
            "http://localhost:8080/v1/receive/+1234567890",
            params={"limit": 1},
        )


@pytest.mark.asyncio
async def test_delete_message(messages_module):
    """Test the delete_message method."""
    # Mock response data
    response_data = {"success": True, "message": "Message deleted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.delete_message("+1234567890", "msg1")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Message deleted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/messages/+1234567890/msg1",
        )


@pytest.mark.asyncio
async def test_show_typing_indicator(messages_module):
    """Test the show_typing_indicator method."""
    # Mock response data
    response_data = {"success": True, "typing": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.show_typing_indicator(
            "+1234567890", "+0987654321"
        )

        # Verify the result
        assert result["success"] is True
        assert result["typing"] is True

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "PUT",
            "http://localhost:8080/v1/typing-indicator/+1234567890",
            data={"recipient": "+0987654321"},
        )


@pytest.mark.asyncio
async def test_hide_typing_indicator(messages_module):
    """Test the hide_typing_indicator method."""
    # Mock response data
    response_data = {"success": True, "typing": False}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.hide_typing_indicator(
            "+1234567890", "+0987654321"
        )

        # Verify the result
        assert result["success"] is True
        assert result["typing"] is False

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/typing-indicator/+1234567890",
            data={"recipient": "+0987654321"},
        )


@pytest.mark.asyncio
async def test_send_enhanced_message(messages_module):
    """Test the send_message method with enhanced features."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method with all new parameters
        link_preview = {
            "url": "https://example.com",
            "title": "Example Website",
            "description": "This is an example website",
        }

        result = await messages_module.send_message(
            "+1234567890",
            "Hello, world!",
            ["+0987654321"],
            attachments=["attachment1"],
            text_mode="styled",
            link_preview=link_preview,
            sticker="sticker123",
        )

        # Verify the result
        assert result["success"] is True
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v2/send",
            data={
                "number": "+1234567890",
                "message": "Hello, world!",
                "recipients": ["+0987654321"],
                "base64_attachments": ["attachment1"],
                "text_mode": "styled",
                "link_preview": link_preview,
                "sticker": "sticker123",
            },
        )


@pytest.mark.asyncio
async def test_send_message_with_quote_split_params(messages_module):
    """Test the send_message method with quote parameters split out."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        quote = {
            "author": "+0987654321",
            "message": "Original message",
            "timestamp": 1234567880,
            "mentions": [{"uuid": "uuid1", "start": 0, "length": 8}],
        }

        result = await messages_module.send_message(
            "+1234567890", "Hello, world!", ["+0987654321"], quote=quote
        )

        # Verify the result
        assert result["success"] is True
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v2/send",
            data={
                "number": "+1234567890",
                "message": "Hello, world!",
                "recipients": ["+0987654321"],
                "quote_author": "+0987654321",
                "quote_message": "Original message",
                "quote_timestamp": 1234567880,
                "quote_mentions": [{"uuid": "uuid1", "start": 0, "length": 8}],
            },
        )


@pytest.mark.asyncio
async def test_send_read_receipt_new_format(messages_module):
    """Test the send_read_receipt method with new API format."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_read_receipt(
            "+1234567890", "+0987654321", [1234567890]
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v1/receipts/+1234567890",
            data={
                "receipt_type": "read",
                "recipient": "+0987654321",
                "timestamp": 1234567890,
            },
        )


@pytest.mark.asyncio
async def test_send_viewed_receipt_new_format(messages_module):
    """Test the send_viewed_receipt method with new API format."""
    # Mock response data
    response_data = {"success": True}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.messages.make_request", make_request_mock):
        # Call the method
        result = await messages_module.send_viewed_receipt(
            "+1234567890", "+0987654321", [1234567890]
        )

        # Verify the result
        assert result["success"] is True

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            messages_module._module_session,
            "POST",
            "http://localhost:8080/v1/receipts/+1234567890",
            data={
                "receipt_type": "viewed",
                "recipient": "+0987654321",
                "timestamp": 1234567890,
            },
        )
