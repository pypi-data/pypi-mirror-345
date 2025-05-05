"""Profiles module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional

import aiohttp

from signal_messenger.models import Profile
from signal_messenger.utils import make_request


class ProfilesModule:
    """Profiles module for the Signal Messenger Python API.

    This module provides access to profile management functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Profiles module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_profile(self, number: str) -> Profile:
        """Get the profile for a phone number.

        Args:
            number: The registered phone number.

        Returns:
            The profile information.
        """
        url = f"{self.base_url}/v1/profiles/{number}"
        response = await make_request(self._module_session, "GET", url)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            profile_dict = {str(k): v for k, v in response.items()}
            # Add the number if not in the response
            if "number" not in profile_dict:
                profile_dict["number"] = number
            return Profile(**profile_dict)
        else:
            # Try to create a minimal Profile object
            return Profile(number=number)

    async def update_profile(
        self,
        number: str,
        name: Optional[str] = None,
        about: Optional[str] = None,
        avatar: Optional[str] = None,
        emoji: Optional[str] = None,
    ) -> Profile:
        """Update a profile.

        Args:
            number: The registered phone number.
            name: The new profile name (optional).
            about: The new profile about text (optional).
            avatar: The new avatar URL (optional).
            emoji: The new profile emoji (optional).

        Returns:
            The updated profile.
        """
        url = f"{self.base_url}/v1/profiles/{number}"
        data = {}
        if name is not None:
            data["name"] = name
        if about is not None:
            data["about"] = about
        if avatar is not None:
            data["avatar"] = avatar
        if emoji is not None:
            data["emoji"] = emoji  # Use emoji in the API request

        response = await make_request(self._module_session, "PUT", url, data=data)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            profile_dict = {str(k): v for k, v in response.items()}
            # Add the number if not in the response
            if "number" not in profile_dict:
                profile_dict["number"] = number
            # Add the updated fields if not in the response
            if name is not None and "name" not in profile_dict:
                profile_dict["name"] = name
            if about is not None and "about" not in profile_dict:
                profile_dict["about"] = about
            if avatar is not None and "avatar" not in profile_dict:
                profile_dict["avatar"] = avatar
            if emoji is not None and "about_emoji" not in profile_dict:
                profile_dict["about_emoji"] = emoji
            return Profile(**profile_dict)
        else:
            # Try to create a minimal Profile object with the updated fields
            return Profile(
                number=number, name=name, about=about, avatar=avatar, about_emoji=emoji
            )

    async def get_contact_profile(self, number: str, contact: str) -> Profile:
        """Get the profile of a contact.

        Args:
            number: The registered phone number.
            contact: The contact's phone number.

        Returns:
            The contact's profile information.
        """
        url = f"{self.base_url}/v1/profiles/{number}/contacts/{contact}"
        response = await make_request(self._module_session, "GET", url)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            profile_dict = {str(k): v for k, v in response.items()}
            # Add the contact number if not in the response
            if "number" not in profile_dict:
                profile_dict["number"] = contact
            return Profile(**profile_dict)
        else:
            # Try to create a minimal Profile object
            return Profile(number=contact)

    async def get_contacts_profiles(self, number: str) -> List[Profile]:
        """Get the profiles of all contacts.

        Args:
            number: The registered phone number.

        Returns:
            A list of contact profiles.
        """
        url = f"{self.base_url}/v1/profiles/{number}/contacts"
        response = await make_request(self._module_session, "GET", url)

        contacts = []
        if isinstance(response, dict) and "contacts" in response:
            contacts = response["contacts"]
        elif isinstance(response, list):
            contacts = response
        else:
            contacts = [response]

        # Convert contacts to Profile objects
        result = []
        for contact in contacts:
            if isinstance(contact, dict):
                # Convert any non-string keys to strings
                profile_dict = {str(k): v for k, v in contact.items()}
                result.append(Profile(**profile_dict))
            else:
                # Try to create a minimal Profile object
                result.append(Profile(number=str(contact)))

        return result

    async def set_profile_sharing(
        self, number: str, contact: str, enabled: bool
    ) -> Profile:
        """Set profile sharing with a contact.

        Args:
            number: The registered phone number.
            contact: The contact's phone number.
            enabled: Whether to enable profile sharing.

        Returns:
            The updated contact profile.
        """
        url = f"{self.base_url}/v1/profiles/{number}/contacts/{contact}/sharing"
        data = {"enabled": enabled}
        response = await make_request(self._module_session, "PUT", url, data=data)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            profile_dict = {str(k): v for k, v in response.items()}
            # Add the contact number if not in the response
            if "number" not in profile_dict:
                profile_dict["number"] = contact
            # Add the profile_sharing field if not in the response
            if "profile_sharing" not in profile_dict:
                profile_dict["profile_sharing"] = enabled
            return Profile(**profile_dict)
        else:
            # Try to create a minimal Profile object
            return Profile(number=contact, profile_sharing=enabled)
