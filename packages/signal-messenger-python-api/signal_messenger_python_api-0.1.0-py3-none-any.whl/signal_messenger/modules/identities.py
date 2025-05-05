"""Identities module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional

import aiohttp

from signal_messenger.models import Identity, TrustLevel
from signal_messenger.utils import make_request


class IdentitiesModule:
    """Identities module for the Signal Messenger Python API.

    This module provides access to identity management functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Identities module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_identities(self, number: str) -> List[Identity]:
        """Get all identities for a phone number.

        Args:
            number: The registered phone number.

        Returns:
            A list of identities.
        """
        url = f"{self.base_url}/v1/identities/{number}"
        response = await make_request(self._module_session, "GET", url)

        identities = []
        if isinstance(response, dict) and "identities" in response:
            identities = response["identities"]
        elif isinstance(response, list):
            identities = response
        else:
            identities = [response]

        # Convert identities to Identity objects
        result = []
        for identity in identities:
            if isinstance(identity, dict):
                # Convert any non-string keys to strings
                identity_dict = {str(k): v for k, v in identity.items()}
                # Map API fields to model fields if needed
                if "trustLevel" in identity_dict and "trust_level" not in identity_dict:
                    identity_dict["trust_level"] = identity_dict["trustLevel"]
                if (
                    "safetyNumber" in identity_dict
                    and "safety_number" not in identity_dict
                ):
                    identity_dict["safety_number"] = identity_dict["safetyNumber"]
                result.append(Identity(**identity_dict))
            else:
                # Try to create a minimal Identity object
                result.append(Identity(number=str(identity)))

        return result

    async def get_identity(self, number: str, recipient: str) -> Identity:
        """Get the identity for a specific recipient.

        Args:
            number: The registered phone number.
            recipient: The recipient's phone number.

        Returns:
            The identity information.
        """
        url = f"{self.base_url}/v1/identities/{number}/{recipient}"
        response = await make_request(self._module_session, "GET", url)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            identity_dict = {str(k): v for k, v in response.items()}
            # Add the recipient number if not in the response
            if "number" not in identity_dict:
                identity_dict["number"] = recipient
            # Map API fields to model fields if needed
            if "trustLevel" in identity_dict and "trust_level" not in identity_dict:
                identity_dict["trust_level"] = identity_dict["trustLevel"]
            if "safetyNumber" in identity_dict and "safety_number" not in identity_dict:
                identity_dict["safety_number"] = identity_dict["safetyNumber"]
            return Identity(**identity_dict)
        else:
            # Try to create a minimal Identity object
            return Identity(number=recipient)

    async def trust_identity(
        self,
        number: str,
        recipient: str,
        trust_level: str,
        verified_safety_number: Optional[str] = None,
    ) -> Identity:
        """Trust an identity.

        Args:
            number: The registered phone number.
            recipient: The recipient's phone number.
            trust_level: The trust level (TRUSTED_VERIFIED, TRUSTED_UNVERIFIED, UNTRUSTED).
            verified_safety_number: The verified safety number (optional).

        Returns:
            The updated identity.
        """
        url = f"{self.base_url}/v1/identities/{number}/{recipient}"
        data = {"trustLevel": trust_level}
        if verified_safety_number:
            data["verifiedSafetyNumber"] = verified_safety_number
        response = await make_request(self._module_session, "PUT", url, data=data)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            identity_dict = {str(k): v for k, v in response.items()}
            # Add the recipient number if not in the response
            if "number" not in identity_dict:
                identity_dict["number"] = recipient
            # Add the trust_level if not in the response
            if "trust_level" not in identity_dict:
                # Convert string trust_level to TrustLevel enum if possible
                try:
                    identity_dict["trust_level"] = TrustLevel(trust_level)
                except ValueError:
                    identity_dict["trust_level"] = trust_level
            # Map API fields to model fields if needed
            if "trustLevel" in identity_dict and "trust_level" not in identity_dict:
                identity_dict["trust_level"] = identity_dict["trustLevel"]
            if "safetyNumber" in identity_dict and "safety_number" not in identity_dict:
                identity_dict["safety_number"] = identity_dict["safetyNumber"]
            if verified_safety_number and "scanned_safety_number" not in identity_dict:
                identity_dict["scanned_safety_number"] = verified_safety_number
            return Identity(**identity_dict)
        else:
            # Try to create a minimal Identity object
            try:
                return Identity(number=recipient, trust_level=TrustLevel(trust_level))
            except ValueError:
                return Identity(number=recipient, trust_level=trust_level)

    async def verify_identity(
        self, number: str, recipient: str, safety_number: str
    ) -> Identity:
        """Verify an identity.

        Args:
            number: The registered phone number.
            recipient: The recipient's phone number.
            safety_number: The safety number to verify.

        Returns:
            The verified identity.
        """
        url = f"{self.base_url}/v1/identities/{number}/{recipient}/verify"
        data = {"safetyNumber": safety_number}
        response = await make_request(self._module_session, "PUT", url, data=data)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            identity_dict = {str(k): v for k, v in response.items()}
            # Add the recipient number if not in the response
            if "number" not in identity_dict:
                identity_dict["number"] = recipient
            # Add the safety_number if not in the response
            if "safety_number" not in identity_dict:
                identity_dict["safety_number"] = safety_number
            # Add the scanned_safety_number if not in the response
            if "scanned_safety_number" not in identity_dict:
                identity_dict["scanned_safety_number"] = safety_number
            # Map API fields to model fields if needed
            if "trustLevel" in identity_dict and "trust_level" not in identity_dict:
                identity_dict["trust_level"] = identity_dict["trustLevel"]
            if "safetyNumber" in identity_dict and "safety_number" not in identity_dict:
                identity_dict["safety_number"] = identity_dict["safetyNumber"]
            return Identity(**identity_dict)
        else:
            # Try to create a minimal Identity object
            return Identity(
                number=recipient,
                safety_number=safety_number,
                scanned_safety_number=safety_number,
                trust_level=TrustLevel.TRUSTED_VERIFIED,
            )

    async def reset_identity_session(self, number: str, recipient: str) -> Identity:
        """Reset an identity session.

        Args:
            number: The registered phone number.
            recipient: The recipient's phone number.

        Returns:
            The identity with reset session.
        """
        url = f"{self.base_url}/v1/identities/{number}/{recipient}/session"
        response = await make_request(self._module_session, "DELETE", url)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            identity_dict = {str(k): v for k, v in response.items()}
            # Add the recipient number if not in the response
            if "number" not in identity_dict:
                identity_dict["number"] = recipient
            # Map API fields to model fields if needed
            if "trustLevel" in identity_dict and "trust_level" not in identity_dict:
                identity_dict["trust_level"] = identity_dict["trustLevel"]
            if "safetyNumber" in identity_dict and "safety_number" not in identity_dict:
                identity_dict["safety_number"] = identity_dict["safetyNumber"]
            return Identity(**identity_dict)
        else:
            # Try to create a minimal Identity object
            return Identity(number=recipient)
