"""Groups module for the Signal Messenger Python API."""

from typing import Any, Dict, List, Optional, Union

import aiohttp

from signal_messenger.models import Group, GroupMember, StatusResponse
from signal_messenger.utils import make_request


class GroupsModule:
    """Groups module for the Signal Messenger Python API.

    This module provides access to group management functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Groups module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_groups(self, number: str) -> List[Group]:
        """Get all groups for a phone number.

        Args:
            number: The registered phone number.

        Returns:
            A list of groups.
        """
        url = f"{self.base_url}/v1/groups/{number}"
        response = await make_request(self._module_session, "GET", url)

        groups = []
        if isinstance(response, dict) and "groups" in response:
            groups = response["groups"]
        elif isinstance(response, list):
            groups = response
        else:
            groups = [response]

        # Convert groups to Group objects
        result = []
        for group in groups:
            if isinstance(group, dict):
                # Convert any non-string keys to strings
                group_dict = {str(k): v for k, v in group.items()}
                result.append(Group(**group_dict))
            else:
                # Try to convert to Group as is
                result.append(Group(id=str(group)))

        return result

    async def get_group(self, number: str, group_id: str) -> Group:
        """Get a specific group.

        Args:
            number: The registered phone number.
            group_id: The group ID.

        Returns:
            The group details.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}"
        response = await make_request(self._module_session, "GET", url)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            group_dict = {str(k): v for k, v in response.items()}
            return Group(**group_dict)
        else:
            # Try to convert to Group as is
            return Group(id=group_id)

    async def create_group(
        self,
        number: str,
        name: str,
        members: List[str],
        description: Optional[str] = None,
        avatar: Optional[str] = None,
        expiration_time: Optional[int] = None,
        group_link: Optional[str] = None,
        permissions: Optional[Dict[str, str]] = None,
    ) -> Group:
        """Create a new group.

        Args:
            number: The registered phone number.
            name: The group name.
            members: The list of member phone numbers.
            description: The group description (optional).
            avatar: The avatar URL or base64 data (optional).
            expiration_time: Message expiration time in seconds (optional).
            group_link: Group link setting: 'disabled', 'enabled', 'enabled-with-approval' (optional).
            permissions: Group permissions settings, such as 'add_members' and 'edit_group' with values
                         'only-admins' or 'every-member' (optional).

        Returns:
            The created group.
        """
        url = f"{self.base_url}/v1/groups/{number}"
        data = {"name": name, "members": members}
        if description:
            data["description"] = description
        if avatar:
            data["base64_avatar"] = avatar
        if expiration_time is not None:
            data["expiration_time"] = expiration_time
        if group_link:
            data["group_link"] = group_link
        if permissions:
            data["permissions"] = permissions

        response = await make_request(self._module_session, "POST", url, data=data)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            group_dict = {str(k): v for k, v in response.items()}
            # Add the name and members if not in the response
            if "name" not in group_dict:
                group_dict["name"] = name
            if "members" not in group_dict and members:
                group_dict["members"] = [{"number": m} for m in members]
            return Group(**group_dict)
        else:
            # Try to create a minimal Group object
            return Group(id=str(response), name=name)

    async def update_group(
        self,
        number: str,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        avatar: Optional[str] = None,
        expiration_time: Optional[int] = None,
    ) -> Group:
        """Update a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.
            name: The new group name (optional).
            description: The new group description (optional).
            avatar: The new avatar URL or base64 data (optional).
            expiration_time: The new message expiration time in seconds (optional).

        Returns:
            The updated group.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}"
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if avatar:
            data["base64_avatar"] = avatar
        if expiration_time is not None:
            data["expiration_time"] = expiration_time

        response = await make_request(self._module_session, "PUT", url, data=data)

        if isinstance(response, dict):
            # Convert any non-string keys to strings
            group_dict = {str(k): v for k, v in response.items()}
            # Add the group_id if not in the response
            if "id" not in group_dict:
                group_dict["id"] = group_id
            # Add the updated fields if not in the response
            if name and "name" not in group_dict:
                group_dict["name"] = name
            if description and "description" not in group_dict:
                group_dict["description"] = description
            if avatar and "avatar" not in group_dict:
                group_dict["avatar"] = avatar
            return Group(**group_dict)
        else:
            # Try to create a minimal Group object
            return Group(id=group_id, name=name, description=description, avatar=avatar)

    async def delete_group(self, number: str, group_id: str) -> StatusResponse:
        """Delete a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.

        Returns:
            A status response containing the deletion status, typically {"deleted": true}.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)

    async def add_members(
        self, number: str, group_id: str, members: List[str]
    ) -> StatusResponse:
        """Add members to a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.
            members: The list of member phone numbers to add.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/members"
        data = {"members": members}
        response = await make_request(self._module_session, "POST", url, data=data)
        return StatusResponse(**response)

    async def remove_members(
        self, number: str, group_id: str, members: List[str]
    ) -> StatusResponse:
        """Remove members from a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.
            members: The list of member phone numbers to remove.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/members"
        data = {"members": members}
        response = await make_request(self._module_session, "DELETE", url, data=data)
        return StatusResponse(**response)

    async def add_admins(
        self, number: str, group_id: str, admins: List[str]
    ) -> StatusResponse:
        """Add admins to a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.
            admins: The list of phone numbers to promote to admin.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/admins"
        data = {"admins": admins}
        response = await make_request(self._module_session, "POST", url, data=data)
        return StatusResponse(**response)

    async def remove_admins(
        self, number: str, group_id: str, admins: List[str]
    ) -> StatusResponse:
        """Remove admins from a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.
            admins: The list of phone numbers to demote from admin.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/admins"
        data = {"admins": admins}
        response = await make_request(self._module_session, "DELETE", url, data=data)
        return StatusResponse(**response)

    async def block_group(self, number: str, group_id: str) -> StatusResponse:
        """Block a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/block"
        response = await make_request(self._module_session, "POST", url)
        return StatusResponse(**response)

    async def join_group(self, number: str, group_id: str) -> StatusResponse:
        """Join a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/join"
        response = await make_request(self._module_session, "POST", url)
        return StatusResponse(**response)

    async def quit_group(self, number: str, group_id: str) -> StatusResponse:
        """Quit a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.

        Returns:
            Status response for the operation.
        """
        url = f"{self.base_url}/v1/groups/{number}/{group_id}/quit"
        response = await make_request(self._module_session, "POST", url)
        return StatusResponse(**response)

    # Keeping this for backwards compatibility
    async def leave_group(self, number: str, group_id: str) -> StatusResponse:
        """Leave a group.

        Args:
            number: The registered phone number.
            group_id: The group ID.

        Returns:
            A status response containing the leave status.
        """
        return await self.quit_group(number, group_id)
