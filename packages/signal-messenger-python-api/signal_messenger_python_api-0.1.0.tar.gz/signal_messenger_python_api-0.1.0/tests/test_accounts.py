"""Tests for the Accounts module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.modules.accounts import AccountsModule


@pytest.fixture
def accounts_module():
    """Create an AccountsModule instance for testing."""
    session = AsyncMock()
    return AccountsModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_register_account(accounts_module):
    """Test the register_account method."""
    # Mock response data
    response_data = {"success": True, "message": "Registration initiated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.register_account("+1234567890")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Registration initiated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "POST",
            "http://localhost:8080/v1/accounts/+1234567890",
            data={},
        )


@pytest.mark.asyncio
async def test_register_account_with_captcha(accounts_module):
    """Test the register_account method with captcha."""
    # Mock response data
    response_data = {"success": True, "message": "Registration initiated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.register_account("+1234567890", "captcha_token")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Registration initiated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "POST",
            "http://localhost:8080/v1/accounts/+1234567890",
            data={"captcha": "captcha_token"},
        )


@pytest.mark.asyncio
async def test_verify_account(accounts_module):
    """Test the verify_account method."""
    # Mock response data
    response_data = {"success": True, "message": "Verification successful"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.verify_account("+1234567890", "123456")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Verification successful"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "POST",
            "http://localhost:8080/v1/accounts/+1234567890/verify/123456",
        )


@pytest.mark.asyncio
async def test_get_account_details(accounts_module):
    """Test the get_account_details method."""
    # Mock response data
    response_data = {
        "number": "+1234567890",
        "registered": True,
        "uuid": "12345678-1234-1234-1234-123456789012",
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.get_account_details("+1234567890")

        # Verify the result
        assert result["number"] == "+1234567890"
        assert result["registered"] is True
        assert result["uuid"] == "12345678-1234-1234-1234-123456789012"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "GET",
            "http://localhost:8080/v1/accounts/+1234567890",
        )


@pytest.mark.asyncio
async def test_update_account(accounts_module):
    """Test the update_account method."""
    # Mock response data
    response_data = {"success": True, "message": "Account updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.update_account(
            "+1234567890", registration_id=1234, pni_registration_id=5678
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Account updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/accounts/+1234567890",
            data={"registrationId": 1234, "pniRegistrationId": 5678},
        )


@pytest.mark.asyncio
async def test_update_account_partial(accounts_module):
    """Test the update_account method with partial data."""
    # Mock response data
    response_data = {"success": True, "message": "Account updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method with only registration_id
        result = await accounts_module.update_account(
            "+1234567890", registration_id=1234
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Account updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/accounts/+1234567890",
            data={"registrationId": 1234},
        )


@pytest.mark.asyncio
async def test_delete_account(accounts_module):
    """Test the delete_account method."""
    # Mock response data
    response_data = {"success": True, "message": "Account deleted"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.delete_account("+1234567890")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Account deleted"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/accounts/+1234567890",
        )


@pytest.mark.asyncio
async def test_set_pin(accounts_module):
    """Test the set_pin method."""
    # Mock response data
    response_data = {"success": True, "message": "PIN set"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.set_pin("+1234567890", "1234")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "PIN set"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/accounts/+1234567890/pin",
            data={"pin": "1234"},
        )


@pytest.mark.asyncio
async def test_remove_pin(accounts_module):
    """Test the remove_pin method."""
    # Mock response data
    response_data = {"success": True, "message": "PIN removed"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.remove_pin("+1234567890")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "PIN removed"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/accounts/+1234567890/pin",
        )


@pytest.mark.asyncio
async def test_set_username(accounts_module):
    """Test the set_username method."""
    # Mock response data
    response_data = {
        "username": "user.123",
        "username_link": "https://signal.me/#eu/user.123",
    }

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.set_username("+1234567890", "user")

        # Verify the result
        assert result["username"] == "user.123"
        assert result["username_link"] == "https://signal.me/#eu/user.123"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "POST",
            "http://localhost:8080/v1/accounts/+1234567890/username",
            data={"username": "user"},
        )


@pytest.mark.asyncio
async def test_remove_username(accounts_module):
    """Test the remove_username method."""
    # Mock response data
    response_data = {"success": True, "message": "Username removed"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.remove_username("+1234567890")

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Username removed"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "DELETE",
            "http://localhost:8080/v1/accounts/+1234567890/username",
        )


@pytest.mark.asyncio
async def test_solve_rate_limit_challenge(accounts_module):
    """Test the solve_rate_limit_challenge method."""
    # Mock response data
    response_data = {"success": True, "message": "Challenge completed"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.solve_rate_limit_challenge(
            "+1234567890", "signalcaptcha://captcha-token-value", "challenge-token-123"
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Challenge completed"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "POST",
            "http://localhost:8080/v1/accounts/+1234567890/rate-limit-challenge",
            data={
                "captcha": "signalcaptcha://captcha-token-value",
                "challenge_token": "challenge-token-123",
            },
        )


@pytest.mark.asyncio
async def test_update_account_settings(accounts_module):
    """Test the update_account_settings method."""
    # Mock response data
    response_data = {"success": True, "message": "Account settings updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method
        result = await accounts_module.update_account_settings(
            "+1234567890", discoverable_by_number=True, share_number=False
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Account settings updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/accounts/+1234567890/settings",
            data={"discoverable_by_number": True, "share_number": False},
        )


@pytest.mark.asyncio
async def test_update_account_settings_partial(accounts_module):
    """Test the update_account_settings method with partial data."""
    # Mock response data
    response_data = {"success": True, "message": "Account settings updated"}

    # Mock the make_request function
    make_request_mock = AsyncMock(return_value=response_data)
    with patch("signal_messenger.modules.accounts.make_request", make_request_mock):
        # Call the method with only one parameter
        result = await accounts_module.update_account_settings(
            "+1234567890", discoverable_by_number=True
        )

        # Verify the result
        assert result["success"] is True
        assert result["message"] == "Account settings updated"

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            accounts_module._module_session,
            "PUT",
            "http://localhost:8080/v1/accounts/+1234567890/settings",
            data={"discoverable_by_number": True},
        )
