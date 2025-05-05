"""Tests for the Attachments module."""

import http
import io
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.modules.attachments import AttachmentsModule


@pytest.fixture
def attachments_module():
    """Create an AttachmentsModule instance for testing."""
    session = AsyncMock()
    return AttachmentsModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_upload_attachment(attachments_module):
    """Test the upload_attachment method."""
    # Mock response data
    response_data = {"id": "attachment1", "contentType": "image/jpeg"}

    # Create a context manager mock
    context_manager_mock = MagicMock()
    context_manager_mock.__aenter__.return_value.status = http.HTTPStatus.OK
    context_manager_mock.__aenter__.return_value.json = AsyncMock(
        return_value=response_data
    )

    # Mock the session post method to return the context manager
    attachments_module._module_session.post = MagicMock(
        return_value=context_manager_mock
    )

    # Mock the utils.handle_response function
    handle_response_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.utils.handle_response", handle_response_mock):
        # Call the method
        file_data = b"test file content"
        result = await attachments_module.upload_attachment(
            "+1234567890", file_data, "image/jpeg"
        )

        # Verify the result
        assert result["id"] == "attachment1"
        assert result["contentType"] == "image/jpeg"

        # Verify the session post call
        attachments_module._module_session.post.assert_called_once_with(
            "http://localhost:8080/v1/attachments/+1234567890",
            data=file_data,
            headers={"Content-Type": "image/jpeg"},
        )

        # Verify the handle_response call
        handle_response_mock.assert_called_once_with(
            context_manager_mock.__aenter__.return_value
        )


@pytest.mark.asyncio
async def test_upload_attachment_with_file_object(attachments_module):
    """Test the upload_attachment method with a file-like object."""
    # Mock response data
    response_data = {"id": "attachment1", "contentType": "image/jpeg"}

    # Create a context manager mock
    context_manager_mock = MagicMock()
    context_manager_mock.__aenter__.return_value.status = http.HTTPStatus.OK
    context_manager_mock.__aenter__.return_value.json = AsyncMock(
        return_value=response_data
    )

    # Mock the session post method to return the context manager
    attachments_module._module_session.post = MagicMock(
        return_value=context_manager_mock
    )

    # Mock the utils.handle_response function
    handle_response_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.utils.handle_response", handle_response_mock):
        # Call the method with a file-like object
        file_data = io.BytesIO(b"test file content")
        result = await attachments_module.upload_attachment(
            "+1234567890", file_data, "image/jpeg"
        )

        # Verify the result
        assert result["id"] == "attachment1"
        assert result["contentType"] == "image/jpeg"

        # Verify the session post call
        attachments_module._module_session.post.assert_called_once_with(
            "http://localhost:8080/v1/attachments/+1234567890",
            data=file_data,
            headers={"Content-Type": "image/jpeg"},
        )

        # Verify the handle_response call
        handle_response_mock.assert_called_once_with(
            context_manager_mock.__aenter__.return_value
        )


@pytest.mark.asyncio
async def test_get_attachment(attachments_module):
    """Test the get_attachment method."""
    # Mock response data
    response_data = b"test file content"

    # Create a context manager mock
    context_manager_mock = MagicMock()
    context_manager_mock.__aenter__.return_value.status = http.HTTPStatus.OK
    context_manager_mock.__aenter__.return_value.read = AsyncMock(
        return_value=response_data
    )

    # Mock the session get method to return the context manager
    attachments_module._module_session.get = MagicMock(
        return_value=context_manager_mock
    )

    # Call the method
    result = await attachments_module.get_attachment("+1234567890", "attachment1")

    # Verify the result
    assert result == b"test file content"

    # Verify the session get call
    attachments_module._module_session.get.assert_called_once_with(
        "http://localhost:8080/v1/attachments/+1234567890/attachment1"
    )


@pytest.mark.asyncio
async def test_get_attachment_error(attachments_module):
    """Test the get_attachment method with an error response."""
    # Mock error response
    error_data = {"error": "Attachment not found"}

    # Create a context manager mock
    context_manager_mock = MagicMock()
    context_manager_mock.__aenter__.return_value.status = http.HTTPStatus.NOT_FOUND
    context_manager_mock.__aenter__.return_value.json = AsyncMock(
        return_value=error_data
    )

    # Mock the session get method to return the context manager
    attachments_module._module_session.get = MagicMock(
        return_value=context_manager_mock
    )

    # Call the method and expect an exception
    with pytest.raises(Exception) as excinfo:
        await attachments_module.get_attachment("+1234567890", "attachment1")

    # Verify the exception message
    assert "Failed to get attachment: Attachment not found" in str(excinfo.value)

    # Verify the session get call
    attachments_module._module_session.get.assert_called_once_with(
        "http://localhost:8080/v1/attachments/+1234567890/attachment1"
    )


@pytest.mark.asyncio
async def test_delete_attachment(attachments_module):
    """Test the delete_attachment method."""
    # Mock response data
    response_data = {"success": True, "message": "Attachment deleted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.attachments.make_request", make_request_mock):
        # Call the method
        result = await attachments_module.delete_attachment(
            "+1234567890", "attachment1"
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Attachment deleted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            attachments_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/attachments/+1234567890/attachment1",
        )


@pytest.mark.asyncio
async def test_get_attachment_info(attachments_module):
    """Test the get_attachment_info method."""
    # Mock response data
    response_data = {
        "id": "attachment1",
        "contentType": "image/jpeg",
        "size": 12345,
        "filename": "image.jpg",
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.attachments.make_request", make_request_mock):
        # Call the method
        result = await attachments_module.get_attachment_info(
            "+1234567890", "attachment1"
        )

        # Verify the result
        assert result["id"] == "attachment1"
        assert result["contentType"] == "image/jpeg"
        assert result["size"] == 12345
        assert result["filename"] == "image.jpg"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            attachments_module._module_session,
            "GET",
            "http://localhost:8080/v1/attachments/+1234567890/attachment1/info",
        )


@pytest.mark.asyncio
async def test_get_attachments(attachments_module):
    """Test the get_attachments method."""
    # Mock response data
    response_data = {
        "attachments": [
            {
                "id": "attachment1",
                "contentType": "image/jpeg",
                "size": 12345,
                "filename": "image1.jpg",
            },
            {
                "id": "attachment2",
                "contentType": "image/png",
                "size": 67890,
                "filename": "image2.png",
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.attachments.make_request", return_value=response_data
    ):
        # Call the method
        result = await attachments_module.get_attachments("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "attachment1"
        assert result[0]["contentType"] == "image/jpeg"
        assert result[1]["id"] == "attachment2"
        assert result[1]["contentType"] == "image/png"


@pytest.mark.asyncio
async def test_get_attachments_list_response(attachments_module):
    """Test the get_attachments method with a list response."""
    # Mock response data
    response_data = [
        {
            "id": "attachment1",
            "contentType": "image/jpeg",
            "size": 12345,
            "filename": "image1.jpg",
        },
        {
            "id": "attachment2",
            "contentType": "image/png",
            "size": 67890,
            "filename": "image2.png",
        },
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.attachments.make_request", return_value=response_data
    ):
        # Call the method
        result = await attachments_module.get_attachments("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "attachment1"
        assert result[0]["contentType"] == "image/jpeg"
        assert result[1]["id"] == "attachment2"
        assert result[1]["contentType"] == "image/png"


@pytest.mark.asyncio
async def test_get_attachments_single_response(attachments_module):
    """Test the get_attachments method with a single attachment response."""
    # Mock response data
    response_data = {
        "id": "attachment1",
        "contentType": "image/jpeg",
        "size": 12345,
        "filename": "image1.jpg",
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.attachments.make_request", return_value=response_data
    ):
        # Call the method
        result = await attachments_module.get_attachments("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "attachment1"
        assert result[0]["contentType"] == "image/jpeg"
