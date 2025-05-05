"""Accounts module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional

import aiohttp

from signal_messenger.models import (
    AccountDetails,
    AccountRegistrationResponse,
    AccountSettingsRequest,
    AccountVerificationResponse,
    RateLimitChallengeRequest,
    StatusResponse,
    UsernameResponse,
)
from signal_messenger.utils import make_request


class AccountsModule:
    """Accounts module for the Signal Messenger Python API.

    This module provides access to account management functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Accounts module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def register_account(
        self, number: str, captcha: Optional[str] = None
    ) -> AccountRegistrationResponse:
        """Register a new Signal account.

        Args:
            number: The phone number to register.
            captcha: The captcha token (if required).

        Returns:
            The response containing the registration information.
        """
        url = f"{self.base_url}/v1/accounts/{number}"
        data = {}
        if captcha:
            data["captcha"] = captcha
        response = await make_request(self._module_session, "POST", url, data=data)
        return AccountRegistrationResponse(**response)

    async def verify_account(
        self, number: str, verification_code: str
    ) -> AccountVerificationResponse:
        """Verify a registered Signal account.

        Args:
            number: The registered phone number.
            verification_code: The verification code.

        Returns:
            The response containing the verification information.
        """
        url = f"{self.base_url}/v1/accounts/{number}/verify/{verification_code}"
        response = await make_request(self._module_session, "POST", url)
        return AccountVerificationResponse(**response)

    async def get_account_details(self, number: str) -> AccountDetails:
        """Get details about a registered Signal account.

        Args:
            number: The registered phone number.

        Returns:
            The response containing the account details.
        """
        url = f"{self.base_url}/v1/accounts/{number}"
        response = await make_request(self._module_session, "GET", url)
        return AccountDetails(**response)

    async def update_account(
        self,
        number: str,
        registration_id: Optional[int] = None,
        pni_registration_id: Optional[int] = None,
    ) -> StatusResponse:
        """Update a registered Signal account.

        Args:
            number: The registered phone number.
            registration_id: The registration ID.
            pni_registration_id: The PNI registration ID.

        Returns:
            A status response containing the update information.
        """
        url = f"{self.base_url}/v1/accounts/{number}"
        data = {}
        if registration_id is not None:
            data["registrationId"] = registration_id
        if pni_registration_id is not None:
            data["pniRegistrationId"] = pni_registration_id
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)

    async def delete_account(self, number: str) -> StatusResponse:
        """Delete a registered Signal account.

        Args:
            number: The registered phone number.

        Returns:
            A status response containing the deletion information.
        """
        url = f"{self.base_url}/v1/accounts/{number}"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)

    async def set_pin(self, number: str, pin: str) -> StatusResponse:
        """Set a PIN for a registered Signal account.

        Args:
            number: The registered phone number.
            pin: The PIN to set.

        Returns:
            A status response containing the PIN setting information.
        """
        url = f"{self.base_url}/v1/accounts/{number}/pin"
        data = {"pin": pin}
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)

    async def remove_pin(self, number: str) -> StatusResponse:
        """Remove the PIN from a registered Signal account.

        Args:
            number: The registered phone number.

        Returns:
            A status response containing the PIN removal information.
        """
        url = f"{self.base_url}/v1/accounts/{number}/pin"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)

    async def set_username(self, number: str, username: str) -> UsernameResponse:
        """Set a username for a registered Signal account.

        This can either be just the nickname (e.g. test) or the complete username
        with discriminator (e.g. test.123).

        Args:
            number: The registered phone number.
            username: The username to set.

        Returns:
            A response containing the username with discriminator and username link.
        """
        url = f"{self.base_url}/v1/accounts/{number}/username"
        data = {"username": username}
        response = await make_request(self._module_session, "POST", url, data=data)
        return UsernameResponse(**response)

    async def remove_username(self, number: str) -> StatusResponse:
        """Remove the username from a registered Signal account.

        Args:
            number: The registered phone number.

        Returns:
            A status response about the operation.
        """
        url = f"{self.base_url}/v1/accounts/{number}/username"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)

    async def solve_rate_limit_challenge(
        self, number: str, captcha: str, challenge_token: str
    ) -> StatusResponse:
        """Lift rate limit restrictions by solving a CAPTCHA.

        When running into rate limits, the limit can be lifted by solving a CAPTCHA.
        To get the captcha token, go to https://signalcaptchas.org/challenge/generate.html
        For the staging environment, use:
        https://signalcaptchas.org/staging/registration/generate.html

        Args:
            number: The registered phone number.
            captcha: The captcha result, starting with signalcaptcha://
            challenge_token: The token from the failed send attempt.

        Returns:
            A status response about the operation.
        """
        url = f"{self.base_url}/v1/accounts/{number}/rate-limit-challenge"
        data = {"captcha": captcha, "challenge_token": challenge_token}
        response = await make_request(self._module_session, "POST", url, data=data)
        return StatusResponse(**response)

    async def update_account_settings(
        self,
        number: str,
        discoverable_by_number: Optional[bool] = None,
        share_number: Optional[bool] = None,
    ) -> StatusResponse:
        """Update the account attributes on the signal server.

        Args:
            number: The registered phone number.
            discoverable_by_number: Whether the account should be discoverable by phone number.
            share_number: Whether to allow number sharing.

        Returns:
            A status response about the operation.
        """
        url = f"{self.base_url}/v1/accounts/{number}/settings"
        data = {}
        if discoverable_by_number is not None:
            data["discoverable_by_number"] = discoverable_by_number
        if share_number is not None:
            data["share_number"] = share_number
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)
