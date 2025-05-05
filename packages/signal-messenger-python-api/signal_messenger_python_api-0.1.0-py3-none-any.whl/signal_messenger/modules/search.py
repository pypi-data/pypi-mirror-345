"""Search module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional, Union

import aiohttp

from signal_messenger.models import Contact, Group, Message, SearchResult
from signal_messenger.utils import make_request


class SearchModule:
    """Search module for the Signal Messenger Python API.

    This module provides access to search functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Search module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def search_messages(
        self, number: str, query: str, limit: Optional[int] = None
    ) -> List[Message]:
        """Search messages for a phone number.

        Args:
            number: The registered phone number.
            query: The search query.
            limit: The maximum number of messages to return (optional).

        Returns:
            A list of matching Message objects.
        """
        url = f"{self.base_url}/v1/search/{number}/messages"
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        response = await make_request(self._module_session, "GET", url, params=params)

        messages = []
        if isinstance(response, dict) and "messages" in response:
            messages = [Message(**message) for message in response["messages"]]
        elif isinstance(response, list):
            messages = [Message(**message) for message in response]
        else:
            messages = [Message(**response)]
        return messages

    async def search_contacts(
        self, number: str, query: str, limit: Optional[int] = None
    ) -> List[Contact]:
        """Search contacts for a phone number.

        Args:
            number: The registered phone number.
            query: The search query.
            limit: The maximum number of contacts to return (optional).

        Returns:
            A list of matching Contact objects.
        """
        url = f"{self.base_url}/v1/search/{number}/contacts"
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        response = await make_request(self._module_session, "GET", url, params=params)

        contacts = []
        if isinstance(response, dict) and "contacts" in response:
            contacts = [Contact(**contact) for contact in response["contacts"]]
        elif isinstance(response, list):
            contacts = [Contact(**contact) for contact in response]
        else:
            contacts = [Contact(**response)]
        return contacts

    async def search_groups(
        self, number: str, query: str, limit: Optional[int] = None
    ) -> List[Group]:
        """Search groups for a phone number.

        Args:
            number: The registered phone number.
            query: The search query.
            limit: The maximum number of groups to return (optional).

        Returns:
            A list of matching Group objects.
        """
        url = f"{self.base_url}/v1/search/{number}/groups"
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        response = await make_request(self._module_session, "GET", url, params=params)

        groups = []
        if isinstance(response, dict) and "groups" in response:
            groups = [Group(**group) for group in response["groups"]]
        elif isinstance(response, list):
            groups = [Group(**group) for group in response]
        else:
            groups = [Group(**response)]
        return groups

    async def search_all(
        self, number: str, query: str, limit: Optional[int] = None
    ) -> SearchResult:
        """Search all entities for a phone number.

        Args:
            number: The registered phone number.
            query: The search query.
            limit: The maximum number of results to return per entity type (optional).

        Returns:
            A SearchResult object containing lists of matching messages, contacts, and groups.
        """
        url = f"{self.base_url}/v1/search/{number}"
        params = {"query": query}
        if limit is not None:
            params["limit"] = str(limit)
        response = await make_request(self._module_session, "GET", url, params=params)

        result = {"query": query, "results": []}

        # Process messages
        messages = []
        if isinstance(response, dict) and "messages" in response:
            messages = [Message(**message) for message in response["messages"]]
            result["messages"] = messages

        # Process contacts
        contacts = []
        if isinstance(response, dict) and "contacts" in response:
            contacts = [Contact(**contact) for contact in response["contacts"]]
            result["contacts"] = contacts

        # Process groups
        groups = []
        if isinstance(response, dict) and "groups" in response:
            groups = [Group(**group) for group in response["groups"]]
            result["groups"] = groups

        return SearchResult(**result)
