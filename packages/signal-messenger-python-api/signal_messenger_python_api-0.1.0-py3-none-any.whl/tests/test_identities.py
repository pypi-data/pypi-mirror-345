"""Tests for the Identities module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.modules.identities import IdentitiesModule


@pytest.fixture
def identities_module():
    """Create an IdentitiesModule instance for testing."""
    session = AsyncMock()
    return IdentitiesModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_get_identities(identities_module):
    """Test the get_identities method."""
    # Mock response data
    response_data = {
        "identities": [
            {
                "recipient": "+0987654321",
                "trustLevel": "TRUSTED",
                "safetyNumber": "1234567890",
                "timestamp": 1234567890,
            },
            {
                "recipient": "+5555555555",
                "trustLevel": "UNTRUSTED",
                "safetyNumber": "0987654321",
                "timestamp": 1234567891,
            },
        ]
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.identities.make_request", return_value=response_data
    ):
        # Call the method
        result = await identities_module.get_identities("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["recipient"] == "+0987654321"
        assert result[0]["trustLevel"] == "TRUSTED"
        assert result[1]["recipient"] == "+5555555555"
        assert result[1]["trustLevel"] == "UNTRUSTED"


@pytest.mark.asyncio
async def test_get_identities_list_response(identities_module):
    """Test the get_identities method with a list response."""
    # Mock response data
    response_data = [
        {
            "recipient": "+0987654321",
            "trustLevel": "TRUSTED",
            "safetyNumber": "1234567890",
            "timestamp": 1234567890,
        },
        {
            "recipient": "+5555555555",
            "trustLevel": "UNTRUSTED",
            "safetyNumber": "0987654321",
            "timestamp": 1234567891,
        },
    ]

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.identities.make_request", return_value=response_data
    ):
        # Call the method
        result = await identities_module.get_identities("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["recipient"] == "+0987654321"
        assert result[0]["trustLevel"] == "TRUSTED"
        assert result[1]["recipient"] == "+5555555555"
        assert result[1]["trustLevel"] == "UNTRUSTED"


@pytest.mark.asyncio
async def test_get_identities_single_response(identities_module):
    """Test the get_identities method with a single identity response."""
    # Mock response data
    response_data = {
        "recipient": "+0987654321",
        "trustLevel": "TRUSTED",
        "safetyNumber": "1234567890",
        "timestamp": 1234567890,
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.identities.make_request", return_value=response_data
    ):
        # Call the method
        result = await identities_module.get_identities("+1234567890")

        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["recipient"] == "+0987654321"
        assert result[0]["trustLevel"] == "TRUSTED"


@pytest.mark.asyncio
async def test_get_identity(identities_module):
    """Test the get_identity method."""
    # Mock response data
    response_data = {
        "recipient": "+0987654321",
        "trustLevel": "TRUSTED",
        "safetyNumber": "1234567890",
        "timestamp": 1234567890,
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.identities.make_request", make_request_mock):
        # Call the method
        result = await identities_module.get_identity("+1234567890", "+0987654321")

        # Verify the result
        assert result["recipient"] == "+0987654321"
        assert result["trustLevel"] == "TRUSTED"
        assert result["safetyNumber"] == "1234567890"
        assert result["timestamp"] == 1234567890

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            identities_module._module_session,
            "GET",
            "http://localhost:8080/v1/identities/+1234567890/+0987654321",
        )


@pytest.mark.asyncio
async def test_trust_identity(identities_module):
    """Test the trust_identity method."""
    # Mock response data
    response_data = {"success": True, "message": "Identity trusted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.identities.make_request", make_request_mock):
        # Call the method
        result = await identities_module.trust_identity(
            "+1234567890", "+0987654321", "TRUSTED"
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Identity trusted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            identities_module._module_session,
            "PUT",
            "http://localhost:8080/v1/identities/+1234567890/+0987654321",
            data={"trustLevel": "TRUSTED"},
        )


@pytest.mark.asyncio
async def test_trust_identity_with_safety_number(identities_module):
    """Test the trust_identity method with a verified safety number."""
    # Mock response data
    response_data = {"success": True, "message": "Identity trusted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.identities.make_request", make_request_mock):
        # Call the method
        result = await identities_module.trust_identity(
            "+1234567890", "+0987654321", "TRUSTED", "1234567890"
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Identity trusted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            identities_module._module_session,
            "PUT",
            "http://localhost:8080/v1/identities/+1234567890/+0987654321",
            data={"trustLevel": "TRUSTED", "verifiedSafetyNumber": "1234567890"},
        )


@pytest.mark.asyncio
async def test_verify_identity(identities_module):
    """Test the verify_identity method."""
    # Mock response data
    response_data = {"success": True, "message": "Identity verified"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.identities.make_request", make_request_mock):
        # Call the method
        result = await identities_module.verify_identity(
            "+1234567890", "+0987654321", "1234567890"
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Identity verified"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            identities_module._module_session,
            "PUT",
            "http://localhost:8080/v1/identities/+1234567890/+0987654321/verify",
            data={"safetyNumber": "1234567890"},
        )


@pytest.mark.asyncio
async def test_reset_identity_session(identities_module):
    """Test the reset_identity_session method."""
    # Mock response data
    response_data = {"success": True, "message": "Session reset"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.identities.make_request", make_request_mock):
        # Call the method
        result = await identities_module.reset_identity_session(
            "+1234567890", "+0987654321"
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Session reset"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            identities_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/identities/+1234567890/+0987654321/session",
        )
