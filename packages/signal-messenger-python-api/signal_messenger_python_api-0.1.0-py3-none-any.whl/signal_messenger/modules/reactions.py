"""Reactions module for the Signal Messenger Python API."""

from typing import Any, List, Optional

import aiohttp

from signal_messenger.models import Reaction, StatusResponse
from signal_messenger.utils import make_request


class ReactionsModule:
    """Reactions module for the Signal Messenger Python API.

    This module provides access to message reaction functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Reactions module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def send_reaction(
        self,
        number: str,
        recipient: str,
        emoji: str,
        target_author: str,
        target_timestamp: int,
        remove: bool = False,
    ) -> StatusResponse:
        """Send a reaction to a message.

        Args:
            number: The sender's phone number.
            recipient: The recipient's phone number.
            emoji: The reaction emoji.
            target_author: The author of the message being reacted to.
            target_timestamp: The timestamp of the message being reacted to.
            remove: Whether to remove the reaction (default: False).

        Returns:
            The response containing the reaction information.
        """
        url = f"{self.base_url}/v1/reactions/{number}/{recipient}"
        data = {
            "emoji": emoji,
            "targetAuthor": target_author,
            "targetTimestamp": target_timestamp,
            "remove": remove,
        }
        response = await make_request(self._module_session, "PUT", url, data=data)
        return StatusResponse(**response)

    async def get_reactions(
        self, number: str, limit: Optional[int] = None
    ) -> List[Reaction]:
        """Get reactions for a phone number.

        Args:
            number: The registered phone number.
            limit: The maximum number of reactions to return (optional).

        Returns:
            A list of reactions.
        """
        url = f"{self.base_url}/v1/reactions/{number}"
        params = {}
        if limit is not None:
            params["limit"] = limit
        response = await make_request(self._module_session, "GET", url, params=params)

        if isinstance(response, dict) and "reactions" in response:
            return [Reaction(**reaction) for reaction in response["reactions"]]
        elif isinstance(response, list):
            return [Reaction(**reaction) for reaction in response]
        return [Reaction(**response)]

    async def get_message_reactions(
        self, number: str, message_id: str
    ) -> List[Reaction]:
        """Get reactions for a specific message.

        Args:
            number: The registered phone number.
            message_id: The message ID.

        Returns:
            A list of reactions for the message.
        """
        url = f"{self.base_url}/v1/reactions/{number}/messages/{message_id}"
        response = await make_request(self._module_session, "GET", url)

        if isinstance(response, dict) and "reactions" in response:
            return [Reaction(**reaction) for reaction in response["reactions"]]
        elif isinstance(response, list):
            return [Reaction(**reaction) for reaction in response]
        return [Reaction(**response)]

    async def delete_reaction(self, number: str, reaction_id: str) -> StatusResponse:
        """Delete a reaction.

        Args:
            number: The registered phone number.
            reaction_id: The reaction ID.

        Returns:
            The response containing the reaction deletion information.
        """
        url = f"{self.base_url}/v1/reactions/{number}/{reaction_id}"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)
