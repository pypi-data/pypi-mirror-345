"""Data models for the Signal Messenger Python API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class BaseModelWithDictAccess(BaseModel):
    """Base model with dictionary-style access for backward compatibility."""

    def __getitem__(self, key):
        """Allow dictionary-style access to model attributes."""
        return getattr(self, key)


class LoggingConfig(BaseModelWithDictAccess):
    """Logging configuration model."""

    level: str = ""
    Level: str = ""

    def __init__(self, **data):
        """Initialize the logging configuration model.

        This handles both 'level' and 'Level' fields from the API.
        """
        super().__init__(**data)
        if not self.level and self.Level:
            self.level = self.Level


class Configuration(BaseModelWithDictAccess):
    """API configuration model."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    Logging: Optional[LoggingConfig] = None

    def __init__(self, **data):
        """Initialize the configuration model.

        This handles both 'logging' and 'Logging' fields from the API.
        """
        super().__init__(**data)
        if not self.logging.level and self.Logging:
            self.logging = self.Logging


class Capabilities(BaseModelWithDictAccess):
    """API capabilities model."""

    model_config = ConfigDict(extra="allow")


class About(BaseModelWithDictAccess):
    """API information model."""

    build: int
    capabilities: Dict[str, List[str]] = Field(default_factory=dict)
    mode: str
    version: str
    versions: List[str]


class AccountSettings(BaseModelWithDictAccess):
    """Account settings model."""

    trust_mode: str


# Account Models
class AccountRegistrationResponse(BaseModelWithDictAccess):
    """Account registration response model."""

    model_config = ConfigDict(extra="allow")

    captcha_required: Optional[bool] = None
    verification_required: Optional[bool] = None


class AccountVerificationResponse(BaseModelWithDictAccess):
    """Account verification response model."""

    model_config = ConfigDict(extra="allow")

    uuid: Optional[str] = None
    number: Optional[str] = None
    registered: Optional[bool] = None


class AccountDetails(BaseModelWithDictAccess):
    """Account details model."""

    model_config = ConfigDict(extra="allow")

    uuid: Optional[str] = None
    number: Optional[str] = None
    registered: Optional[bool] = None


class UsernameResponse(BaseModelWithDictAccess):
    """Username response model."""

    username: str
    username_link: Optional[str] = None


class AccountSettingsRequest(BaseModelWithDictAccess):
    """Account settings request model."""

    discoverable_by_number: Optional[bool] = None
    share_number: Optional[bool] = None


class RateLimitChallengeRequest(BaseModelWithDictAccess):
    """Rate limit challenge request model."""

    captcha: str
    challenge_token: str


# Device Models
class DeviceType(str, Enum):
    """Device type enum."""

    MOBILE = "mobile"
    DESKTOP = "desktop"
    UNKNOWN = "unknown"


class Device(BaseModelWithDictAccess):
    """Device model."""

    model_config = ConfigDict(extra="allow")

    id: int
    name: Optional[str] = None
    created: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    type: Optional[DeviceType] = DeviceType.UNKNOWN


class LinkedDevice(Device):
    """Linked device model."""

    linked: bool = True


# Message Models
class MessageType(str, Enum):
    """Message type enum."""

    INCOMING = "incoming"
    OUTGOING = "outgoing"
    SYNC = "sync"


class MessageAttachment(BaseModelWithDictAccess):
    """Message attachment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    content_type: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None


class MessageMention(BaseModelWithDictAccess):
    """Message mention model."""

    model_config = ConfigDict(extra="allow")

    uuid: str
    start: int
    length: int


class MessageQuote(BaseModelWithDictAccess):
    """Message quote model."""

    model_config = ConfigDict(extra="allow")

    id: int
    author: str
    text: str
    attachments: List[MessageAttachment] = Field(default_factory=list)


class Message(BaseModelWithDictAccess):
    """Message model."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    type: Optional[MessageType] = None
    source: Optional[str] = None
    source_uuid: Optional[str] = None
    source_device: Optional[int] = None
    timestamp: Optional[int] = None
    server_timestamp: Optional[int] = None
    server_delivered_timestamp: Optional[int] = None
    has_legacy_message: Optional[bool] = None
    unidentified_sender: Optional[bool] = None
    message: Optional[str] = None
    expiration: Optional[int] = None
    is_view_once: Optional[bool] = None
    is_story: Optional[bool] = None
    attachments: List[MessageAttachment] = Field(default_factory=list)
    mentions: List[MessageMention] = Field(default_factory=list)
    quote: Optional[MessageQuote] = None
    reactions: List["Reaction"] = Field(default_factory=list)
    sticker: Optional["Sticker"] = None
    group_info: Optional["GroupInfo"] = None


# Group Models
class GroupRole(str, Enum):
    """Group role enum."""

    ADMINISTRATOR = "ADMINISTRATOR"
    DEFAULT = "DEFAULT"


class GroupMember(BaseModelWithDictAccess):
    """Group member model."""

    model_config = ConfigDict(extra="allow")

    uuid: Optional[str] = None
    number: Optional[str] = None
    role: Optional[GroupRole] = GroupRole.DEFAULT


class GroupInfo(BaseModelWithDictAccess):
    """Group info model."""

    model_config = ConfigDict(extra="allow")

    group_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    members: List[GroupMember] = Field(default_factory=list)
    pending_members: List[GroupMember] = Field(default_factory=list)
    requesting_members: List[GroupMember] = Field(default_factory=list)
    admins: List[GroupMember] = Field(default_factory=list)
    active: Optional[bool] = None
    blocked: Optional[bool] = None
    permission_add_member: Optional[str] = None
    permission_edit_details: Optional[str] = None
    permission_send_message: Optional[str] = None
    link: Optional[str] = None
    message_expiration_time: Optional[int] = None


class Group(BaseModelWithDictAccess):
    """Group model."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    internal_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    members: List[Union[GroupMember, str]] = Field(default_factory=list)
    pending_members: List[Union[GroupMember, str]] = Field(default_factory=list)
    requesting_members: List[Union[GroupMember, str]] = Field(default_factory=list)
    admins: List[Union[GroupMember, str]] = Field(default_factory=list)
    active: Optional[bool] = None
    blocked: Optional[bool] = None
    permission_add_member: Optional[str] = None
    permission_edit_details: Optional[str] = None
    permission_send_message: Optional[str] = None
    link: Optional[str] = None
    message_expiration_time: Optional[int] = None

    # For backward compatibility
    success: Optional[bool] = None
    message: Optional[str] = None
    groupId: Optional[str] = None

    def __init__(self, **data):
        """Initialize the group model.

        This handles converting string members to GroupMember objects and mapping fields.
        """
        # Map groupId to id if id is not present
        if "groupId" in data and "id" not in data:
            data["id"] = data["groupId"]

        # Convert string members to GroupMember objects
        for field in ["members", "pending_members", "requesting_members", "admins"]:
            if field in data and isinstance(data[field], list):
                processed_members = []
                for member in data[field]:
                    if isinstance(member, str):
                        processed_members.append(GroupMember(number=member))
                    else:
                        processed_members.append(member)
                data[field] = processed_members

        super().__init__(**data)

    def __getitem__(self, key):
        """Allow dictionary-style access to model attributes with special handling for members."""
        if key == "members" and hasattr(self, "members"):
            # For backward compatibility, return the original string members if requested
            result = []
            for m in self.members:
                if isinstance(m, GroupMember) and m.number:
                    result.append(m.number)
                elif isinstance(m, str):
                    result.append(m)
            return result
        return super().__getitem__(key)


# Attachment Models
class Attachment(BaseModelWithDictAccess):
    """Attachment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    content_type: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    stored_filename: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    voice_note: Optional[bool] = None
    caption: Optional[str] = None
    preview: Optional[Dict[str, Any]] = None


# Profile Models
class Profile(BaseModelWithDictAccess):
    """Profile model."""

    model_config = ConfigDict(extra="allow")

    uuid: Optional[str] = None
    number: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    about: Optional[str] = None
    about_emoji: Optional[str] = None
    avatar: Optional[str] = None
    color: Optional[str] = None
    profile_sharing: Optional[bool] = None
    capabilities: List[str] = Field(default_factory=list)


# Identity Models
class TrustLevel(str, Enum):
    """Trust level enum."""

    TRUSTED_UNVERIFIED = "TRUSTED_UNVERIFIED"
    TRUSTED_VERIFIED = "TRUSTED_VERIFIED"
    UNTRUSTED = "UNTRUSTED"
    TRUSTED = "TRUSTED"  # For backward compatibility


class Identity(BaseModelWithDictAccess):
    """Identity model."""

    model_config = ConfigDict(extra="allow")

    uuid: Optional[str] = None
    number: Optional[str] = None
    trust_level: Optional[TrustLevel] = None
    added: Optional[datetime] = None
    fingerprint: Optional[str] = None
    safety_number: Optional[str] = None
    scanned_safety_number: Optional[str] = None


# Reaction Models
class Reaction(BaseModelWithDictAccess):
    """Reaction model."""

    model_config = ConfigDict(extra="allow")

    emoji: str
    author: Optional[str] = None
    author_uuid: Optional[str] = None
    target_author: Optional[str] = None
    target_author_uuid: Optional[str] = None
    timestamp: Optional[int] = None
    received_timestamp: Optional[int] = None


# Receipt Models
class ReceiptType(str, Enum):
    """Receipt type enum."""

    READ = "read"
    VIEWED = "viewed"
    DELIVERY = "delivery"


class Receipt(BaseModelWithDictAccess):
    """Receipt model."""

    model_config = ConfigDict(extra="allow")

    type: ReceiptType
    sender: Optional[str] = None
    sender_uuid: Optional[str] = None
    sender_device: Optional[int] = None
    timestamp: Optional[int] = None
    when: Optional[int] = None


# Search Models
class SearchResult(BaseModelWithDictAccess):
    """Search result model."""

    model_config = ConfigDict(extra="allow")

    results: List[Any] = Field(default_factory=list)
    query: Optional[str] = None


# Sticker Models
class Sticker(BaseModelWithDictAccess):
    """Sticker model."""

    model_config = ConfigDict(extra="allow")

    id: int
    emoji: Optional[str] = None
    pack_id: Optional[str] = None
    pack_key: Optional[str] = None
    attachment: Optional[Attachment] = None


class StickerPack(BaseModelWithDictAccess):
    """Sticker pack model."""

    model_config = ConfigDict(extra="allow")

    id: str
    key: str
    title: Optional[str] = None
    author: Optional[str] = None
    stickers: List[Sticker] = Field(default_factory=list)
    cover: Optional[Sticker] = None
    installed: Optional[bool] = None


# Contact Models
class Contact(BaseModelWithDictAccess):
    """Contact model."""

    model_config = ConfigDict(extra="allow")

    uuid: Optional[str] = None
    number: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    color: Optional[str] = None
    profile_key: Optional[str] = None
    blocked: Optional[bool] = None
    expiration: Optional[int] = None


# Status Response Model
class StatusResponse(BaseModelWithDictAccess):
    """Status response model for action methods."""

    model_config = ConfigDict(extra="allow")

    # Common status fields
    success: Optional[bool] = None
    message: Optional[str] = None

    # Delete operation fields
    deleted: Optional[bool] = None

    # Send operation fields
    sent: Optional[bool] = None

    # Group operation fields
    left: Optional[bool] = None

    # Typing indicator fields
    typing: Optional[bool] = None

    # PIN operation fields
    pin_set: Optional[bool] = None
    pin_removed: Optional[bool] = None
