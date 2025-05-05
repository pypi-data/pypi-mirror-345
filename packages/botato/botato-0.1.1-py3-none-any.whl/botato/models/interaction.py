from typing import Optional, List, Literal, Union

from botato.models.base import BotatoBase
from botato.models.snowflake import Snowflake
from botato.models.user import User
from botato.models.member import Member
from botato.models.message import Message


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5
    

class InteractionOption(BotatoBase):
    name: str
    type: int
    value: Optional[Union[str, int, float, bool]] = None
    options: Optional[List["InteractionOption"]] = None
    focused: Optional[bool] = False
    
    
class InteractionData(BotatoBase):
    id: Snowflake
    name: str
    type: int
    options: Optional[List[InteractionOption]] = None
    custom_id: Optional[str] = None
    component_type: Optional[int] = None
    
    
class Interaction(BotatoBase):
    id: Snowflake
    application_id: Snowflake
    type: int
    data: Optional[InteractionData] = None
    guild_id: Optional[Snowflake] = None
    channel_id: Optional[Snowflake] = None
    member: Optional[Member] = None
    user: Optional[User] = None
    token: str
    version: int
    message: Optional[Message] = None