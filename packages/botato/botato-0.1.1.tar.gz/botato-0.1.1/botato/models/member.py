from typing import Optional, List
from datetime import datetime

from botato.models.base import BotatoBase, Field
from botato.models.snowflake import Snowflake
from botato.models.user import User
from botato.models.user import AvatarDecorationData


class Member(BotatoBase):
    """
    Represents a Discord member.

    Documentation:
    https://discord.com/developers/docs/resources/guild#guild-member-object
    """
    
    user: Optional[User] = None
    nick: Optional[str] = None
    avatar: Optional[str] = None
    banner: Optional[str] = None
    roles: List[Snowflake] = Field(default_factory=list)
    joined_at: datetime
    premium_since: Optional[datetime] = None
    deaf: bool
    mute: bool
    flags: int
    pending: Optional[bool] = None
    permissions: Optional[str] = None
    communication_disabled_until: Optional[datetime] = None
    avatar_decoration_data: Optional[AvatarDecorationData] = None