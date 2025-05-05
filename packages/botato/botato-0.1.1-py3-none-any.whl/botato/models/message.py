from typing import Optional, List
from datetime import datetime

from botato.models.base import BotatoBase, Field
from botato.models.snowflake import Snowflake
from botato.models.user import User
from botato.models.role import Role
from botato.models.channel import Channel
from botato.models.channel import ChannelMention
from botato.models.embed import Embed
from botato.models.reaction import Reaction
    

class Attachment(BotatoBase):
    """
    Represents an attachment in a Discord message.
    """
    
    id: Snowflake
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    size: int
    url: str
    proxy_url: str
    height: Optional[int] = None
    width: Optional[int] = None
    ephemeral: Optional[bool] = None
    duration_secs: Optional[float] = None
    waveform: Optional[str] = None
    flags: Optional[int] = None


class Message(BotatoBase):
    """
    Represents a Discord message object.

    Documentation:
    https://discord.com/developers/docs/resources/message#messages-resource
    """
    
    id: Snowflake
    channel_id: Snowflake
    author: User
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime] = None
    tts: bool
    mention_everyone: bool
    mentions: List[User] = Field(default_factory=list)
    mention_roles: List[Snowflake] = Field(default_factory=list)
    mention_channels: Optional[List[ChannelMention]] = Field(default_factory=list)
    attachments: List[Attachment] = Field(default_factory=list)
    embeds: List[Embed] = Field(default_factory=list)
    reactions: Optional[List[Reaction]] = Field(default_factory=list)
    nonce: Optional[str | int] = None
    pinned: bool
    webhook_id: Optional[Snowflake] = None
    type: int
    application_id: Optional[str] = None
    flags: Optional[int] = None
    referenced_message: Optional["Message"] = None
    thread: Optional[Channel] = None
    position: Optional[int] = None

    # TODO: Create models for these fields
    activity: Optional[dict] = None
    application: Optional[dict] = None
    message_reference: Optional[dict] = None
    message_snapshots: Optional[List[dict]] = None
    interaction_metadata: Optional[dict] = None
    interaction: Optional[dict] = None
    components: Optional[List[dict]] = None
    sticker_items: Optional[List[dict]] = None
    stickers: Optional[List[dict]] = None
    role_subscription_data: Optional[dict] = None
    resolved: Optional[dict] = None
    poll: Optional[dict] = None
    call: Optional[dict] = None