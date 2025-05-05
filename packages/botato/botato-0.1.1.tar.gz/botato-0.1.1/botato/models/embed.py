from botato.models.base import BotatoBase
from typing import Optional, List


class EmbedField(BotatoBase):
    """
    Represents a field in an embed.
    """
    
    name: str
    value: str
    inline: Optional[bool] = None
        

class EmbedAuthor(BotatoBase):
    """
    Represents the author of an embed.
    """
    
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None
        

class EmbedProvider(BotatoBase):
    """
    Represents a provider of an embed.
    """
    
    name: Optional[str] = None
    url: Optional[str] = None
        

class EmbedVideo(BotatoBase):
    """
    Represents a video in an embed.
    """
    
    url: Optional[str] = None
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
        
        
class EmbedImage(BotatoBase):
    """
    Represents an image in an embed.
    """
    
    url: Optional[str] = None
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
        
        
class EmbedThumbnail(BotatoBase):
    """
    Represents a thumbnail in an embed.
    """
    
    url: Optional[str] = None
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
        
        
class EmbedFooter(BotatoBase):
    """
    Represents a footer in an embed.
    """
    
    text: str
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None
        
    
class Embed(BotatoBase):
    """
    Represents an embed in a Discord message.
    
    Documentation:
    https://discord.com/developers/docs/resources/message#embed-object
    """
    
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    color: Optional[int] = None
    footer: Optional[EmbedFooter] = None
    image: Optional[EmbedImage] = None
    thumbnail: Optional[EmbedThumbnail] = None
    video: Optional[EmbedVideo] = None
    provider: Optional[EmbedProvider] = None
    fields: Optional[List[EmbedField]] = None