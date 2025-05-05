from botato.models.base import BotatoBase
from botato.models.snowflake import Snowflake


class Role(BotatoBase):
    """
    Represents a Discord role.
    """
    
    id: Snowflake
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool