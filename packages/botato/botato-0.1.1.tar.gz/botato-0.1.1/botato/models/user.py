from botato.models.base import BotatoBase
from botato.models.snowflake import Snowflake
from typing import Optional


class AvatarDecorationData(BotatoBase):
    """
    Represents the avatar decoration data for a Discord user.
    """
    
    asset: str
    sku_id: str


class User(BotatoBase):
    """
    Represents a Discord user.

    Documentation:
    https://discord.com/developers/docs/resources/user#user-object
    """
    
    id: Snowflake
    username: str
    discriminator: str # Note: not used for users anymore, only for bots
    global_name: str | None = None
    avatar: str | None = None
    bot: Optional[bool] = False
    system: Optional[bool] = False
    mfa_enabled: Optional[bool] = False
    banner: Optional[str] = None
    accent_color: Optional[int] = None
    locale: Optional[str] = None
    verified: Optional[bool] = False
    email: Optional[str] = None
    flags: Optional[int] = None
    premium_type: Optional[int] = None
    public_flags: Optional[int] = None
    avatar_decoration_data: Optional[AvatarDecorationData] = None