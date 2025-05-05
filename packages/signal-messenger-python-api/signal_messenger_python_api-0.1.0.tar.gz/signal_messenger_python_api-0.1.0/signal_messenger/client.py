"""Signal Messenger Python API client."""

import asyncio
from typing import Optional

import aiohttp

from signal_messenger.modules.accounts import AccountsModule
from signal_messenger.modules.attachments import AttachmentsModule
from signal_messenger.modules.contacts import ContactsModule
from signal_messenger.modules.devices import DevicesModule
from signal_messenger.modules.general import GeneralModule
from signal_messenger.modules.groups import GroupsModule
from signal_messenger.modules.identities import IdentitiesModule
from signal_messenger.modules.messages import MessagesModule
from signal_messenger.modules.profiles import ProfilesModule
from signal_messenger.modules.reactions import ReactionsModule
from signal_messenger.modules.receipts import ReceiptsModule
from signal_messenger.modules.search import SearchModule
from signal_messenger.modules.stickers import StickersModule


class SignalClient(
    GeneralModule,
    DevicesModule,
    AccountsModule,
    GroupsModule,
    MessagesModule,
    AttachmentsModule,
    ProfilesModule,
    IdentitiesModule,
    ReactionsModule,
    ReceiptsModule,
    SearchModule,
    StickersModule,
    ContactsModule,
):
    """Signal Messenger Python API client.

    This client provides access to the Signal CLI REST API.
    It inherits from all module classes to provide a unified interface.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Initialize the Signal client.

        Args:
            base_url: The base URL of the API.
            timeout: The request timeout in seconds.
            session: An existing aiohttp session to use.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session
        self._owned_session = False

        # Initialize modules after session is created
        self._modules_initialized = False

    async def __aenter__(self):
        """Enter the async context manager."""
        await self._ensure_session()
        await self._init_modules()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        await self.close()

    async def _ensure_session(self):
        """Ensure that a session exists."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            self._owned_session = True

    async def _init_modules(self):
        """Initialize all modules."""
        if not self._modules_initialized:
            # Get the session
            session_obj = await self.session

            # Store the session object as an instance variable for modules to use
            self._session_obj = session_obj

            # Initialize modules with the base_url and session object
            GeneralModule.__init__(self, self.base_url, self._session_obj)
            DevicesModule.__init__(self, self.base_url, self._session_obj)
            AccountsModule.__init__(self, self.base_url, self._session_obj)
            GroupsModule.__init__(self, self.base_url, self._session_obj)
            MessagesModule.__init__(self, self.base_url, self._session_obj)
            AttachmentsModule.__init__(self, self.base_url, self._session_obj)
            ProfilesModule.__init__(self, self.base_url, self._session_obj)
            IdentitiesModule.__init__(self, self.base_url, self._session_obj)
            ReactionsModule.__init__(self, self.base_url, self._session_obj)
            ReceiptsModule.__init__(self, self.base_url, self._session_obj)
            SearchModule.__init__(self, self.base_url, self._session_obj)
            StickersModule.__init__(self, self.base_url, self._session_obj)
            ContactsModule.__init__(self, self.base_url, self._session_obj)

            # Mark modules as initialized
            self._modules_initialized = True

    async def close(self):
        """Close the client session."""
        if self._owned_session and self._session is not None:
            await self._session.close()
            self._session = None
            self._owned_session = False

    @property
    async def session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session.

        Returns:
            The aiohttp session.
        """
        await self._ensure_session()
        return self._session
