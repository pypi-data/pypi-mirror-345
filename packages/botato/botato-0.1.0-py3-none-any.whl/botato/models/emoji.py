from typing import Optional, List

from botato.models.base import BotatoBase, Field
from botato.models.snowflake import Snowflake
from botato.models.user import User


class Emoji(BotatoBase):
    """
    Represents a Discord emoji.
    
    Documentation:
    https://discord.com/developers/docs/resources/emoji#emoji-object
    """
    
    id: Optional[Snowflake] = None
    name: Optional[str] = None
    roles: List[Snowflake] = Field(default_factory=list)
    user: User
    require_colons: bool = False
    managed: bool = False
    animated: bool = False
    available: bool = True