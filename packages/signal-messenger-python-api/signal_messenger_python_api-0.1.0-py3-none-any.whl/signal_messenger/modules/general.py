"""General module for the Signal Messenger Python API."""

from typing import Any, Dict, Optional

import aiohttp

from signal_messenger.models import About, AccountSettings, Configuration
from signal_messenger.utils import make_request


class GeneralModule:
    """General module for the Signal Messenger Python API.

    This module provides access to general API information and configuration.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the General module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_about(self) -> About:
        """Get information about the API.

        Returns:
            Information about the API.
        """
        url = f"{self.base_url}/v1/about"
        response = await make_request(self._module_session, "GET", url)
        return About(**response)

    async def get_configuration(self) -> Configuration:
        """Get the API configuration.

        Returns:
            The API configuration.
        """
        url = f"{self.base_url}/v1/configuration"
        response = await make_request(self._module_session, "GET", url)
        return Configuration(**response)

    async def set_configuration(self, logging_level: str) -> None:
        """Set the API configuration.

        Args:
            logging_level: The logging level to set.
        """
        url = f"{self.base_url}/v1/configuration"
        data = {"logging": {"level": logging_level}}
        await make_request(self._module_session, "POST", url, data=data)

    async def get_account_settings(self, number: str) -> AccountSettings:
        """Get account specific settings.

        Args:
            number: The registered phone number.

        Returns:
            The account settings.
        """
        url = f"{self.base_url}/v1/configuration/{number}/settings"
        response = await make_request(self._module_session, "GET", url)
        return AccountSettings(**response)

    async def set_account_settings(self, number: str, trust_mode: str) -> None:
        """Set account specific settings.

        Args:
            number: The registered phone number.
            trust_mode: The trust mode to set.
        """
        url = f"{self.base_url}/v1/configuration/{number}/settings"
        data = {"trust_mode": trust_mode}
        await make_request(self._module_session, "POST", url, data=data)

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check.

        Returns:
            The health check response.
        """
        url = f"{self.base_url}/v1/health"
        return await make_request(self._module_session, "GET", url)
