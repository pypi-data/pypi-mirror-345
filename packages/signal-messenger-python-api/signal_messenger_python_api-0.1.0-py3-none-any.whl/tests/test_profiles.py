"""Tests for the Profiles module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.modules.profiles import ProfilesModule


@pytest.fixture
def profiles_module():
    """Create a ProfilesModule instance for testing."""
    session = AsyncMock()
    return ProfilesModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_get_profile(profiles_module):
    """Test the get_profile method."""
    # Mock response data
    response_data = {
        "name": "John Doe",
        "about": "Signal user",
        "avatar": "avatar_url",
        "emoji": "👋",
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.profiles.make_request", make_request_mock):
        # Call the method
        result = await profiles_module.get_profile("+1234567890")

        # Verify the result
        assert result["name"] == "John Doe"
        assert result["about"] == "Signal user"
        assert result["avatar"] == "avatar_url"
        assert result["emoji"] == "👋"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            profiles_module._module_session,
            "GET",
            "http://localhost:8080/v1/profiles/+1234567890",
        )


@pytest.mark.asyncio
async def test_update_profile(profiles_module):
    """Test the update_profile method."""
    # Mock response data
    response_data = {"success": True, "message": "Profile updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.profiles.make_request", make_request_mock):
        # Call the method
        result = await profiles_module.update_profile(
            "+1234567890",
            name="John Smith",
            about="Updated profile",
            avatar="new_avatar_url",
            emoji="🚀",
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Profile updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            profiles_module._module_session,
            "PUT",
            "http://localhost:8080/v1/profiles/+1234567890",
            data={
                "name": "John Smith",
                "about": "Updated profile",
                "avatar": "new_avatar_url",
                "emoji": "🚀",
            },
        )


@pytest.mark.asyncio
async def test_update_profile_partial(profiles_module):
    """Test the update_profile method with partial data."""
    # Mock response data
    response_data = {"success": True, "message": "Profile updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.profiles.make_request", make_request_mock):
        # Call the method with only name
        result = await profiles_module.update_profile("+1234567890", name="John Smith")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Profile updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            profiles_module._module_session,
            "PUT",
            "http://localhost:8080/v1/profiles/+1234567890",
            data={"name": "John Smith"},
        )


@pytest.mark.asyncio
async def test_get_contact_profile(profiles_module):
    """Test the get_contact_profile method."""
    # Mock response data
    response_data = {
        "name": "Jane Doe",
        "about": "Contact profile",
        "avatar": "contact_avatar_url",
        "emoji": "👩‍💻",
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.profiles.make_request", make_request_mock):
        # Call the method
        result = await profiles_module.get_contact_profile("+1234567890", "+0987654321")

        # Verify the result
        assert result["name"] == "Jane Doe"
        assert result["about"] == "Contact profile"
        assert result["avatar"] == "contact_avatar_url"
        assert result["emoji"] == "👩‍💻"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            profiles_module._module_session,
            "GET",
            "http://localhost:8080/v1/profiles/+1234567890/contacts/+0987654321",
        )


@pytest.mark.asyncio
async def test_get_contacts_profiles(profiles_module):
    """Test the get_contacts_profiles method."""
    # Mock response data
    response_data = {
        "contacts": [
            {
                "number": "+0987654321",
                "name": "Jane Doe",
                "about": "Contact 1",
                "avatar": "avatar1_url",
            },
            {
                "number": "+5555555555",
                "name": "Bob Smith",
                "about": "Contact 2",
                "avatar": "avatar2_url",
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.profiles.make_request", return_value=response_data
    ):
        # Call the method
        result = await profiles_module.get_contacts_profiles("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["number"] == "+0987654321"
        assert result[0]["name"] == "Jane Doe"
        assert result[1]["number"] == "+5555555555"
        assert result[1]["name"] == "Bob Smith"


@pytest.mark.asyncio
async def test_get_contacts_profiles_list_response(profiles_module):
    """Test the get_contacts_profiles method with a list response."""
    # Mock response data
    response_data = [
        {
            "number": "+0987654321",
            "name": "Jane Doe",
            "about": "Contact 1",
            "avatar": "avatar1_url",
        },
        {
            "number": "+5555555555",
            "name": "Bob Smith",
            "about": "Contact 2",
            "avatar": "avatar2_url",
        },
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.profiles.make_request", return_value=response_data
    ):
        # Call the method
        result = await profiles_module.get_contacts_profiles("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["number"] == "+0987654321"
        assert result[0]["name"] == "Jane Doe"
        assert result[1]["number"] == "+5555555555"
        assert result[1]["name"] == "Bob Smith"


@pytest.mark.asyncio
async def test_get_contacts_profiles_single_response(profiles_module):
    """Test the get_contacts_profiles method with a single contact response."""
    # Mock response data
    response_data = {
        "number": "+0987654321",
        "name": "Jane Doe",
        "about": "Contact 1",
        "avatar": "avatar1_url",
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.profiles.make_request", return_value=response_data
    ):
        # Call the method
        result = await profiles_module.get_contacts_profiles("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["number"] == "+0987654321"
        assert result[0]["name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_set_profile_sharing(profiles_module):
    """Test the set_profile_sharing method."""
    # Mock response data
    response_data = {"success": True, "message": "Profile sharing updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.profiles.make_request", make_request_mock):
        # Call the method
        result = await profiles_module.set_profile_sharing(
            "+1234567890", "+0987654321", True
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Profile sharing updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            profiles_module._module_session,
            "PUT",
            "http://localhost:8080/v1/profiles/+1234567890/contacts/+0987654321/sharing",
            data={"enabled": True},
        )


@pytest.mark.asyncio
async def test_set_profile_sharing_disabled(profiles_module):
    """Test the set_profile_sharing method with sharing disabled."""
    # Mock response data
    response_data = {"success": True, "message": "Profile sharing updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.profiles.make_request", make_request_mock):
        # Call the method
        result = await profiles_module.set_profile_sharing(
            "+1234567890", "+0987654321", False
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Profile sharing updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            profiles_module._module_session,
            "PUT",
            "http://localhost:8080/v1/profiles/+1234567890/contacts/+0987654321/sharing",
            data={"enabled": False},
        )
