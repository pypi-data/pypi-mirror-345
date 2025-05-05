from botato.models.base import BotatoBase
from typing import Optional, List
from botato.models.emoji import Emoji

class ReactionCountDetails(BotatoBase):
    """
    Represents the details of a reaction count.
    """
    
    burst: int
    normal: int
    

class Reaction(BotatoBase):
    """
    Represents a reaction to a message.
    """
    
    count: int
    count_details: Optional[ReactionCountDetails] = None
    me: bool
    me_burst: bool
    emoji: Emoji
    burst_colors: Optional[List[str]] = None