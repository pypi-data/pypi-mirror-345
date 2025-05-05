"""Tests for the Reactions module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.models import Reaction, StatusResponse
from signal_messenger.modules.reactions import ReactionsModule


@pytest.fixture
def reactions_module():
    """Create a ReactionsModule instance for testing."""
    session = AsyncMock()
    return ReactionsModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_send_reaction(reactions_module):
    """Test the send_reaction method."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.reactions.make_request", make_request_mock):
        # Call the method
        result = await reactions_module.send_reaction(
            "+1234567890", "+0987654321", "👍", "+0987654321", 1234567890
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.timestamp == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            reactions_module._module_session,
            "PUT",
            "http://localhost:8080/v1/reactions/+1234567890/+0987654321",
            data={
                "emoji": "👍",
                "targetAuthor": "+0987654321",
                "targetTimestamp": 1234567890,
                "remove": False,
            },
        )


@pytest.mark.asyncio
async def test_send_reaction_remove(reactions_module):
    """Test the send_reaction method with remove=True."""
    # Mock response data
    response_data = {"success": True, "timestamp": 1234567890}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.reactions.make_request", make_request_mock):
        # Call the method
        result = await reactions_module.send_reaction(
            "+1234567890", "+0987654321", "👍", "+0987654321", 1234567890, True
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.timestamp == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            reactions_module._module_session,
            "PUT",
            "http://localhost:8080/v1/reactions/+1234567890/+0987654321",
            data={
                "emoji": "👍",
                "targetAuthor": "+0987654321",
                "targetTimestamp": 1234567890,
                "remove": True,
            },
        )


@pytest.mark.asyncio
async def test_get_reactions(reactions_module):
    """Test the get_reactions method."""
    # Mock response data
    response_data = {
        "reactions": [
            {
                "id": "reaction1",
                "emoji": "👍",
                "author": "+0987654321",
                "target_author": "+1234567890",
                "timestamp": 1234567890,
                "received_timestamp": 1234567891,
            },
            {
                "id": "reaction2",
                "emoji": "❤️",
                "author": "+5555555555",
                "target_author": "+1234567890",
                "timestamp": 1234567892,
                "received_timestamp": 1234567893,
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.reactions.make_request", return_value=response_data
    ):
        # Call the method
        result = await reactions_module.get_reactions("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Reaction)
        assert result[0].emoji == "👍"
        assert result[0].author == "+0987654321"
        assert isinstance(result[1], Reaction)
        assert result[1].emoji == "❤️"
        assert result[1].author == "+5555555555"


@pytest.mark.asyncio
async def test_get_reactions_with_limit(reactions_module):
    """Test the get_reactions method with limit."""
    # Mock response data
    response_data = {
        "reactions": [
            {
                "id": "reaction1",
                "emoji": "👍",
                "author": "+0987654321",
                "target_author": "+1234567890",
                "timestamp": 1234567890,
                "received_timestamp": 1234567891,
            }
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.reactions.make_request", make_request_mock):
        # Call the method
        result = await reactions_module.get_reactions("+1234567890", limit=1)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Reaction)
        assert result[0].emoji == "👍"
        assert result[0].author == "+0987654321"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            reactions_module._module_session,
            "GET",
            "http://localhost:8080/v1/reactions/+1234567890",
            params={"limit": 1},
        )


@pytest.mark.asyncio
async def test_get_reactions_list_response(reactions_module):
    """Test the get_reactions method with a list response."""
    # Mock response data
    response_data = [
        {
            "id": "reaction1",
            "emoji": "👍",
            "author": "+0987654321",
            "target_author": "+1234567890",
            "timestamp": 1234567890,
            "received_timestamp": 1234567891,
        },
        {
            "id": "reaction2",
            "emoji": "❤️",
            "author": "+5555555555",
            "target_author": "+1234567890",
            "timestamp": 1234567892,
            "received_timestamp": 1234567893,
        },
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.reactions.make_request", return_value=response_data
    ):
        # Call the method
        result = await reactions_module.get_reactions("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Reaction)
        assert result[0].emoji == "👍"
        assert result[0].author == "+0987654321"
        assert isinstance(result[1], Reaction)
        assert result[1].emoji == "❤️"
        assert result[1].author == "+5555555555"


@pytest.mark.asyncio
async def test_get_reactions_single_response(reactions_module):
    """Test the get_reactions method with a single reaction response."""
    # Mock response data
    response_data = {
        "id": "reaction1",
        "emoji": "👍",
        "author": "+0987654321",
        "target_author": "+1234567890",
        "timestamp": 1234567890,
        "received_timestamp": 1234567891,
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.reactions.make_request", return_value=response_data
    ):
        # Call the method
        result = await reactions_module.get_reactions("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Reaction)
        assert result[0].emoji == "👍"
        assert result[0].author == "+0987654321"


@pytest.mark.asyncio
async def test_get_message_reactions(reactions_module):
    """Test the get_message_reactions method."""
    # Mock response data
    response_data = {
        "reactions": [
            {
                "id": "reaction1",
                "emoji": "👍",
                "author": "+0987654321",
                "target_author": "+1234567890",
                "timestamp": 1234567890,
                "received_timestamp": 1234567891,
            },
            {
                "id": "reaction2",
                "emoji": "❤️",
                "author": "+5555555555",
                "target_author": "+1234567890",
                "timestamp": 1234567892,
                "received_timestamp": 1234567893,
            },
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.reactions.make_request", make_request_mock):
        # Call the method
        result = await reactions_module.get_message_reactions("+1234567890", "message1")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Reaction)
        assert result[0].emoji == "👍"
        assert result[0].author == "+0987654321"
        assert isinstance(result[1], Reaction)
        assert result[1].emoji == "❤️"
        assert result[1].author == "+5555555555"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            reactions_module._module_session,
            "GET",
            "http://localhost:8080/v1/reactions/+1234567890/messages/message1",
        )


@pytest.mark.asyncio
async def test_delete_reaction(reactions_module):
    """Test the delete_reaction method."""
    # Mock response data
    response_data = {"success": True, "message": "Reaction deleted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.reactions.make_request", make_request_mock):
        # Call the method
        result = await reactions_module.delete_reaction("+1234567890", "reaction1")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Reaction deleted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            reactions_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/reactions/+1234567890/reaction1",
        )
