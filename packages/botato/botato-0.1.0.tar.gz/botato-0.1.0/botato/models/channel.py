from botato.models.base import BotatoBase
from typing import Optional, List
from botato.models.user import User


class Channel(BotatoBase):
    """
    Represents a Discord channel.

    Documentation:
    https://discord.com/developers/docs/resources/channel#channels-resource
    """
    
    id: str
    type: int
    guild_id: Optional[str] = None
    position: Optional[int] = None
    permission_overwrites: Optional[list] = None # TODO: Define PermissionOverwrite model
    name: Optional[str] = None
    topic: Optional[str] = None
    nsfw: Optional[bool] = None
    last_message_id: Optional[str] = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    rate_limit_per_user: Optional[int] = None
    recipients: Optional[List[User]] = None
    icon: Optional[str] = None
    owner_id: Optional[str] = None
    application_id: Optional[str] = None
    managed: Optional[bool] = None
    parent_id: Optional[str] = None
    last_pin_timestamp: Optional[str] = None
    rtc_region: Optional[str] = None
    video_quality_mode: Optional[int] = None
    message_count: Optional[int] = None
    member_count: Optional[int] = None
    thread_metadata: Optional[dict] = None  # TODO: Define ThreadMetadata model
    member: Optional[dict] = None # TODO: Define ThreadMember model
    default_auto_archive_duration: Optional[int] = None
    permissions: Optional[str] = None
    flags: Optional[int] = None
    total_message_sent: Optional[int] = None
    available_tags: Optional[List[dict]] = None  # TODO: Define Tag model
    applied_tags: Optional[List[str]] = None
    default_reaction_emoji: Optional[dict] = None  # TODO: Define DefaultReaction model
    default_thread_rate_limit_per_user: Optional[int] = None
    default_sort_order: Optional[int] = None
    default_forum_layout: Optional[int] = None
        
class ChannelMention(BotatoBase):
    """
    Represents a mention of a channel in a Discord message.

    Documentation:
    https://discord.com/developers/docs/resources/message#channel-mention-object
    """
    
    id: str
    guild_id: str
    type: int
    name: str