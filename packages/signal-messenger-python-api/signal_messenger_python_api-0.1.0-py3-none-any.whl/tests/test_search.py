"""Tests for the Search module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.models import Contact, Group, Message, SearchResult
from signal_messenger.modules.search import SearchModule


@pytest.fixture
def search_module():
    """Create a SearchModule instance for testing."""
    session = AsyncMock()
    return SearchModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_search_messages(search_module):
    """Test the search_messages method."""
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
                "message": "Hello, Signal!",
            },
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_messages("+1234567890", "Hello")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Message)
        assert result[0].id == "msg1"
        assert result[0].message == "Hello, world!"
        assert isinstance(result[1], Message)
        assert result[1].id == "msg2"
        assert result[1].message == "Hello, Signal!"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890/messages",
            params={"query": "Hello"},
        )


@pytest.mark.asyncio
async def test_search_messages_with_limit(search_module):
    """Test the search_messages method with limit."""
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
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_messages("+1234567890", "Hello", limit=1)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Message)
        assert result[0].id == "msg1"
        assert result[0].message == "Hello, world!"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890/messages",
            params={"query": "Hello", "limit": "1"},
        )


@pytest.mark.asyncio
async def test_search_contacts(search_module):
    """Test the search_contacts method."""
    # Mock response data
    response_data = {
        "contacts": [
            {
                "number": "+0987654321",
                "name": "John Doe",
                "about": "Signal user",
            },
            {
                "number": "+5555555555",
                "name": "John Smith",
                "about": "Another Signal user",
            },
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_contacts("+1234567890", "John")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Contact)
        assert result[0].number == "+0987654321"
        assert result[0].name == "John Doe"
        assert isinstance(result[1], Contact)
        assert result[1].number == "+5555555555"
        assert result[1].name == "John Smith"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890/contacts",
            params={"query": "John"},
        )


@pytest.mark.asyncio
async def test_search_contacts_with_limit(search_module):
    """Test the search_contacts method with limit."""
    # Mock response data
    response_data = {
        "contacts": [
            {
                "number": "+0987654321",
                "name": "John Doe",
                "about": "Signal user",
            }
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_contacts("+1234567890", "John", limit=1)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Contact)
        assert result[0].number == "+0987654321"
        assert result[0].name == "John Doe"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890/contacts",
            params={"query": "John", "limit": "1"},
        )


@pytest.mark.asyncio
async def test_search_groups(search_module):
    """Test the search_groups method."""
    # Mock response data
    response_data = {
        "groups": [
            {
                "id": "group1",
                "name": "Signal Group",
                "members": ["+1234567890", "+0987654321"],
            },
            {
                "id": "group2",
                "name": "Another Signal Group",
                "members": ["+1234567890", "+5555555555"],
            },
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_groups("+1234567890", "Signal")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Group)
        assert result[0].id == "group1"
        assert result[0].name == "Signal Group"
        assert isinstance(result[1], Group)
        assert result[1].id == "group2"
        assert result[1].name == "Another Signal Group"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890/groups",
            params={"query": "Signal"},
        )


@pytest.mark.asyncio
async def test_search_groups_with_limit(search_module):
    """Test the search_groups method with limit."""
    # Mock response data
    response_data = {
        "groups": [
            {
                "id": "group1",
                "name": "Signal Group",
                "members": ["+1234567890", "+0987654321"],
            }
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_groups("+1234567890", "Signal", limit=1)

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Group)
        assert result[0].id == "group1"
        assert result[0].name == "Signal Group"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890/groups",
            params={"query": "Signal", "limit": "1"},
        )


@pytest.mark.asyncio
async def test_search_all(search_module):
    """Test the search_all method."""
    # Mock response data
    response_data = {
        "messages": [
            {
                "id": "msg1",
                "source": "+0987654321",
                "timestamp": 1234567890,
                "message": "Hello, Signal!",
            }
        ],
        "contacts": [
            {
                "number": "+0987654321",
                "name": "John Doe",
                "about": "Signal user",
            }
        ],
        "groups": [
            {
                "id": "group1",
                "name": "Signal Group",
                "members": ["+1234567890", "+0987654321"],
            }
        ],
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_all("+1234567890", "Signal")

        # Verify the result
        assert isinstance(result, SearchResult)
        assert hasattr(result, "messages")
        assert hasattr(result, "contacts")
        assert hasattr(result, "groups")
        assert result.query == "Signal"

        # Check messages
        assert len(result.messages) == 1
        assert isinstance(result.messages[0], Message)
        assert result.messages[0].id == "msg1"

        # Check contacts
        assert len(result.contacts) == 1
        assert isinstance(result.contacts[0], Contact)
        assert result.contacts[0].number == "+0987654321"

        # Check groups
        assert len(result.groups) == 1
        assert isinstance(result.groups[0], Group)
        assert result.groups[0].id == "group1"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890",
            params={"query": "Signal"},
        )


@pytest.mark.asyncio
async def test_search_all_with_limit(search_module):
    """Test the search_all method with limit."""
    # Mock response data
    response_data = {
        "messages": [
            {
                "id": "msg1",
                "source": "+0987654321",
                "timestamp": 1234567890,
                "message": "Hello, Signal!",
            }
        ],
        "contacts": [
            {
                "number": "+0987654321",
                "name": "John Doe",
                "about": "Signal user",
            }
        ],
        "groups": [
            {
                "id": "group1",
                "name": "Signal Group",
                "members": ["+1234567890", "+0987654321"],
            }
        ],
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_all("+1234567890", "Signal", limit=1)

        # Verify the result
        assert isinstance(result, SearchResult)
        assert hasattr(result, "messages")
        assert hasattr(result, "contacts")
        assert hasattr(result, "groups")
        assert len(result.messages) == 1
        assert len(result.contacts) == 1
        assert len(result.groups) == 1

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890",
            params={"query": "Signal", "limit": "1"},
        )


@pytest.mark.asyncio
async def test_search_all_empty_response(search_module):
    """Test the search_all method with an empty response."""
    # Mock response data
    response_data = {}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.search.make_request", make_request_mock):
        # Call the method
        result = await search_module.search_all("+1234567890", "Signal")

        # Verify the result
        assert isinstance(result, SearchResult)
        assert hasattr(result, "query")
        assert result.query == "Signal"
        assert not hasattr(result, "messages") or len(result.messages) == 0
        assert not hasattr(result, "contacts") or len(result.contacts) == 0
        assert not hasattr(result, "groups") or len(result.groups) == 0

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            search_module._module_session,
            "GET",
            "http://localhost:8080/v1/search/+1234567890",
            params={"query": "Signal"},
        )
