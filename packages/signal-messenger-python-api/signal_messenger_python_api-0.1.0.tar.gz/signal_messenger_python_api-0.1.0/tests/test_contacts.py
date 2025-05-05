"""Tests for the Contacts module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.models import Contact, StatusResponse
from signal_messenger.modules.contacts import ContactsModule


@pytest.fixture
def contacts_module():
    """Create a ContactsModule instance for testing."""
    session = AsyncMock()
    return ContactsModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_get_contacts(contacts_module):
    """Test the get_contacts method."""
    # Mock response data
    response_data = {
        "contacts": [
            {
                "number": "+0987654321",
                "name": "John Doe",
                "expiration": "604800",
                "blocked": False,
            },
            {
                "number": "+5555555555",
                "name": "Jane Smith",
                "expiration": "0",
                "blocked": True,
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.contacts.make_request", return_value=response_data
    ):
        # Call the method
        result = await contacts_module.get_contacts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Contact)
        assert result[0].number == "+0987654321"
        assert result[0].name == "John Doe"
        assert isinstance(result[1], Contact)
        assert result[1].number == "+5555555555"
        assert result[1].name == "Jane Smith"


@pytest.mark.asyncio
async def test_get_contacts_list_response(contacts_module):
    """Test the get_contacts method with a list response."""
    # Mock response data
    response_data = [
        {
            "number": "+0987654321",
            "name": "John Doe",
            "expiration": "604800",
            "blocked": False,
        },
        {
            "number": "+5555555555",
            "name": "Jane Smith",
            "expiration": "0",
            "blocked": True,
        },
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.contacts.make_request", return_value=response_data
    ):
        # Call the method
        result = await contacts_module.get_contacts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Contact)
        assert result[0].number == "+0987654321"
        assert result[0].name == "John Doe"
        assert isinstance(result[1], Contact)
        assert result[1].number == "+5555555555"
        assert result[1].name == "Jane Smith"


@pytest.mark.asyncio
async def test_get_contacts_single_response(contacts_module):
    """Test the get_contacts method with a single contact response."""
    # Mock response data
    response_data = {
        "number": "+0987654321",
        "name": "John Doe",
        "expiration": "604800",
        "blocked": False,
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.contacts.make_request", return_value=response_data
    ):
        # Call the method
        result = await contacts_module.get_contacts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Contact)
        assert result[0].number == "+0987654321"
        assert result[0].name == "John Doe"


@pytest.mark.asyncio
async def test_get_contact(contacts_module):
    """Test the get_contact method."""
    # Mock response data
    response_data = {
        "number": "+0987654321",
        "name": "John Doe",
        "expiration": "604800",
        "blocked": False,
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.get_contact("+1234567890", "+0987654321")

        # Verify the result
        assert isinstance(result, Contact)
        assert result.number == "+0987654321"
        assert result.name == "John Doe"
        assert result.expiration == 604800  # Changed from "604800" to 604800
        assert result.blocked is False

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "GET",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321",
        )


@pytest.mark.asyncio
async def test_add_contact(contacts_module):
    """Test the add_contact method."""
    # Mock response data
    response_data = {"success": True, "message": "Contact added"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.add_contact(
            "+1234567890", "+0987654321", "John Doe"
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact added"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "POST",
            "http://localhost:8080/v1/contacts/+1234567890",
            data={"contact": "+0987654321", "name": "John Doe"},
        )


@pytest.mark.asyncio
async def test_add_contact_with_expiration(contacts_module):
    """Test the add_contact method with expiration."""
    # Mock response data
    response_data = {"success": True, "message": "Contact added"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.add_contact(
            "+1234567890", "+0987654321", "John Doe", 604800
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact added"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "POST",
            "http://localhost:8080/v1/contacts/+1234567890",
            data={"contact": "+0987654321", "name": "John Doe", "expiration": "604800"},
        )


@pytest.mark.asyncio
async def test_update_contact(contacts_module):
    """Test the update_contact method."""
    # Mock response data
    response_data = {"success": True, "message": "Contact updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.update_contact(
            "+1234567890", "+0987654321", name="John Smith"
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321",
            data={"name": "John Smith"},
        )


@pytest.mark.asyncio
async def test_update_contact_with_expiration(contacts_module):
    """Test the update_contact method with expiration."""
    # Mock response data
    response_data = {"success": True, "message": "Contact updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.update_contact(
            "+1234567890", "+0987654321", expiration=604800
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321",
            data={"expiration": "604800"},
        )


@pytest.mark.asyncio
async def test_update_contact_with_blocked(contacts_module):
    """Test the update_contact method with blocked."""
    # Mock response data
    response_data = {"success": True, "message": "Contact updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.update_contact(
            "+1234567890", "+0987654321", blocked=True
        )

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321",
            data={"blocked": True},
        )


@pytest.mark.asyncio
async def test_delete_contact(contacts_module):
    """Test the delete_contact method."""
    # Mock response data
    response_data = {"success": True, "message": "Contact deleted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.delete_contact("+1234567890", "+0987654321")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact deleted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321",
        )


@pytest.mark.asyncio
async def test_block_contact(contacts_module):
    """Test the block_contact method."""
    # Mock response data
    response_data = {"success": True, "message": "Contact blocked"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.block_contact("+1234567890", "+0987654321")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact blocked"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321/block",
        )


@pytest.mark.asyncio
async def test_unblock_contact(contacts_module):
    """Test the unblock_contact method."""
    # Mock response data
    response_data = {"success": True, "message": "Contact unblocked"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.unblock_contact("+1234567890", "+0987654321")

        # Verify the result
        assert isinstance(result, StatusResponse)
        assert result.success is True
        assert result.message == "Contact unblocked"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/contacts/+1234567890/+0987654321/unblock",
        )


@pytest.mark.asyncio
async def test_get_blocked_contacts(contacts_module):
    """Test the get_blocked_contacts method."""
    # Mock response data
    response_data = {
        "contacts": [
            {
                "number": "+0987654321",
                "name": "John Doe",
                "expiration": "604800",
                "blocked": True,
            },
            {
                "number": "+5555555555",
                "name": "Jane Smith",
                "expiration": "0",
                "blocked": True,
            },
        ]
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.contacts.make_request", make_request_mock):
        # Call the method
        result = await contacts_module.get_blocked_contacts("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Contact)
        assert result[0].number == "+0987654321"
        assert result[0].blocked is True
        assert isinstance(result[1], Contact)
        assert result[1].number == "+5555555555"
        assert result[1].blocked is True

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            contacts_module._module_session,
            "GET",
            "http://localhost:8080/v1/contacts/+1234567890/blocked",
        )
