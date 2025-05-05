"""Stickers module for the Signal Messenger Python API."""

from typing import Any, BinaryIO, List, Optional, Union

import aiohttp

from signal_messenger.models import StatusResponse, Sticker, StickerPack
from signal_messenger.utils import make_request


class StickersModule:
    """Stickers module for the Signal Messenger Python API.

    This module provides access to sticker pack management functionality.
    """

    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        """Initialize the Stickers module.

        Args:
            base_url: The base URL of the API.
            session: The aiohttp session.
        """
        self.base_url = base_url
        self._module_session = session

    async def get_sticker_packs(self, number: str) -> List[StickerPack]:
        """Get all sticker packs for a phone number.

        Args:
            number: The registered phone number.

        Returns:
            A list of sticker packs.
        """
        url = f"{self.base_url}/v1/stickers/{number}"
        response = await make_request(self._module_session, "GET", url)

        # Handle different response formats
        if isinstance(response, dict):
            if "stickers" in response:
                # Response contains a list of sticker packs in the "stickers" field
                sticker_packs = response["stickers"]
            else:
                # Response is a single sticker pack
                # For a single sticker pack, we'll directly create and return a StickerPack object
                try:
                    # Ensure ID is a string as required by the model
                    if "id" in response and not isinstance(response["id"], str):
                        response["id"] = str(response["id"])

                    # Add key if missing
                    if "key" not in response:
                        response["key"] = f"key-{response['id']}"

                    # Create sticker objects if needed
                    if "stickers" in response and isinstance(
                        response["stickers"], list
                    ):
                        processed_stickers = []
                        for s in response["stickers"]:
                            if isinstance(s, dict):
                                sticker_data = s.copy()
                                # Ensure sticker ID is integer as required by the model
                                if "id" in sticker_data and not isinstance(
                                    sticker_data["id"], int
                                ):
                                    try:
                                        sticker_data["id"] = int(sticker_data["id"])
                                    except (ValueError, TypeError):
                                        pass
                                processed_stickers.append(Sticker(**sticker_data))
                        response["stickers"] = processed_stickers

                    # Create the StickerPack object with explicit fields
                    pack = StickerPack(
                        id=str(response["id"]),
                        key=response.get("key", f"key-{response['id']}"),
                        title=response.get("title"),
                        author=response.get("author"),
                        stickers=[
                            Sticker(**s)
                            for s in response.get("stickers", [])
                            if isinstance(s, dict)
                        ],
                    )
                    return [pack]
                except Exception as e:
                    # Log error and return empty list
                    print(f"Error creating StickerPack from single response: {e}")
                    return []
        elif isinstance(response, list):
            # Response is a list of sticker packs
            sticker_packs = response
        else:
            # Unexpected response type
            return []

        # Convert all packs to StickerPack objects
        result = []
        for pack in sticker_packs:
            if not isinstance(pack, dict):
                continue

            # Make a deep copy to avoid modifying the original data
            pack_data = pack.copy()

            # Process the pack ID
            # No special handling needed here

            # Create sticker objects from stickers in the pack
            if "stickers" in pack_data and isinstance(pack_data["stickers"], list):
                processed_stickers = []
                for s in pack_data["stickers"]:
                    if isinstance(s, dict):
                        sticker_data = s.copy()
                        # Ensure sticker ID is integer as required by the model
                        if "id" in sticker_data and not isinstance(
                            sticker_data["id"], int
                        ):
                            try:
                                sticker_data["id"] = int(sticker_data["id"])
                            except (ValueError, TypeError):
                                # If conversion fails, keep the original ID
                                pass
                        processed_stickers.append(sticker_data)
                pack_data["stickers"] = processed_stickers

            # Ensure required fields exist with correct types
            if "id" in pack_data:
                # Ensure pack ID is string as required by model
                # Only convert to string if it's not already a string
                # This preserves the original string value like "pack1" instead of converting it to "1"
                if not isinstance(pack_data["id"], str):
                    pack_data["id"] = str(pack_data["id"])

                # Add key if missing
                if "key" not in pack_data:
                    pack_data["key"] = f"key-{pack_data['id']}"

                try:
                    # Pass the fixed pack data to the model constructor
                    result.append(StickerPack(**pack_data))
                except Exception as e:
                    # Log error and continue with next pack
                    print(f"Error creating StickerPack: {e}, data: {pack_data}")

        return result

    async def get_sticker_pack(self, number: str, pack_id: str) -> StickerPack:
        """Get a specific sticker pack.

        Args:
            number: The registered phone number.
            pack_id: The sticker pack ID.

        Returns:
            The sticker pack details.
        """
        url = f"{self.base_url}/v1/stickers/{number}/{pack_id}"
        response = await make_request(self._module_session, "GET", url)
        return StickerPack(**response)

    async def install_sticker_pack(
        self, number: str, pack_id: str, pack_key: str
    ) -> StickerPack:
        """Install a sticker pack.

        Args:
            number: The registered phone number.
            pack_id: The sticker pack ID.
            pack_key: The sticker pack key.

        Returns:
            The installed sticker pack.
        """
        url = f"{self.base_url}/v1/stickers/{number}"
        data = {"packId": pack_id, "packKey": pack_key}
        response = await make_request(self._module_session, "POST", url, data=data)
        return StickerPack(**response)

    async def uninstall_sticker_pack(self, number: str, pack_id: str) -> StatusResponse:
        """Uninstall a sticker pack.

        Args:
            number: The registered phone number.
            pack_id: The sticker pack ID.

        Returns:
            The response containing the sticker pack uninstallation information.
        """
        url = f"{self.base_url}/v1/stickers/{number}/{pack_id}"
        response = await make_request(self._module_session, "DELETE", url)
        return StatusResponse(**response)

    async def upload_sticker_pack(
        self,
        number: str,
        title: str,
        author: str,
        cover: Union[bytes, BinaryIO],
        stickers: List[dict],
    ) -> StickerPack:
        """Upload a new sticker pack.

        Args:
            number: The registered phone number.
            title: The sticker pack title.
            author: The sticker pack author.
            cover: The cover image data as bytes or a file-like object.
            stickers: The list of stickers, each with 'image' and 'emoji' keys.

        Returns:
            The uploaded sticker pack information.
        """
        url = f"{self.base_url}/v1/stickers/{number}/upload"

        # Use aiohttp's FormData to build a multipart request
        from aiohttp import FormData

        data = FormData()
        data.add_field("title", title)
        data.add_field("author", author)
        data.add_field("cover", cover)

        for i, sticker in enumerate(stickers):
            data.add_field(f"sticker_{i}", sticker["image"])
            data.add_field(f"emoji_{i}", sticker["emoji"])

        # Use the session directly for multipart data
        async with self._module_session.post(url, data=data) as response:
            from signal_messenger.utils import handle_response

            response_data = await handle_response(response)
            return StickerPack(**response_data)
