"""Tests for the General module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from signal_messenger.models import About, AccountSettings, Configuration, LoggingConfig
from signal_messenger.modules.general import GeneralModule


@pytest.fixture
def general_module():
    """Create a GeneralModule instance for testing."""
    session = AsyncMock()
    return GeneralModule("http://localhost:8080", session)


@pytest.mark.asyncio
async def test_get_about(general_module):
    """Test the get_about method."""
    # Mock response data
    response_data = {
        "build": 123,
        "capabilities": {
            "additionalProp1": ["feature1", "feature2"],
            "additionalProp2": ["feature3"],
        },
        "mode": "normal",
        "version": "1.0.0",
        "versions": ["1.0.0", "0.9.0"],
    }

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.general.make_request", return_value=response_data
    ):
        # Call the method
        result = await general_module.get_about()

        # Verify the result
        assert isinstance(result, About)
        assert result.build == 123
        assert result.mode == "normal"
        assert result.version == "1.0.0"
        assert result.versions == ["1.0.0", "0.9.0"]
        assert result.capabilities["additionalProp1"] == [
            "feature1",
            "feature2",
        ]
        assert result.capabilities["additionalProp2"] == ["feature3"]


@pytest.mark.asyncio
async def test_get_configuration(general_module):
    """Test the get_configuration method."""
    # Mock response data
    response_data = {"logging": {"level": "INFO"}}

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.general.make_request", return_value=response_data
    ):
        # Call the method
        result = await general_module.get_configuration()

        # Verify the result
        assert isinstance(result, Configuration)
        assert isinstance(result.logging, LoggingConfig)
        assert result.logging.level == "INFO"


@pytest.mark.asyncio
async def test_set_configuration(general_module):
    """Test the set_configuration method."""
    # Mock the make_request function
    make_request_mock = AsyncMock()
    with patch("signal_messenger.modules.general.make_request", make_request_mock):
        # Call the method
        await general_module.set_configuration("DEBUG")

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            general_module._module_session,
            "POST",
            "http://localhost:8080/v1/configuration",
            data={"logging": {"level": "DEBUG"}},
        )


@pytest.mark.asyncio
async def test_get_account_settings(general_module):
    """Test the get_account_settings method."""
    # Mock response data
    response_data = {"trust_mode": "ALWAYS"}

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.general.make_request", return_value=response_data
    ):
        # Call the method
        result = await general_module.get_account_settings("+1234567890")

        # Verify the result
        assert isinstance(result, AccountSettings)
        assert result.trust_mode == "ALWAYS"


@pytest.mark.asyncio
async def test_set_account_settings(general_module):
    """Test the set_account_settings method."""
    # Mock the make_request function
    make_request_mock = AsyncMock()
    with patch("signal_messenger.modules.general.make_request", make_request_mock):
        # Call the method
        await general_module.set_account_settings("+1234567890", "ALWAYS")

        # Verify the make_request call
        make_request_mock.assert_called_once_with(
            general_module._module_session,
            "POST",
            "http://localhost:8080/v1/configuration/+1234567890/settings",
            data={"trust_mode": "ALWAYS"},
        )


@pytest.mark.asyncio
async def test_health_check(general_module):
    """Test the health_check method."""
    # Mock response data
    response_data = {"status": "ok"}

    # Mock the make_request function
    with patch(
        "signal_messenger.modules.general.make_request", return_value=response_data
    ):
        # Call the method
        result = await general_module.health_check()

        # Verify the result
        assert result == {"status": "ok"}
