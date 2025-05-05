from typing import Optional, List

from botato.models.base import BotatoBase
from botato.models.snowflake import Snowflake
from botato.models.role import Role


class Guild(BotatoBase):
    """
    Represents a Discord guild (server).

    Documentation:
    https://discord.com/developers/docs/resources/guild#guild-resource
    """
    
    id: Snowflake
    name: str
    icon: Optional[str] = None
    icon_hash: Optional[str] = None
    splash: Optional[str] = None
    discovery_splash: Optional[str] = None
    owner: Optional[bool] = None
    owner_id: Optional[Snowflake] = None
    permissions: Optional[str] = None
    region: Optional[str] = None
    afk_channel_id: Optional[Snowflake] = None
    afk_timeout: Optional[int] = None
    widget_enabled: Optional[bool] = None
    widget_channel_id: Optional[Snowflake] = None
    verification_level: Optional[int] = None
    default_message_notifications: Optional[int] = None
    explicit_content_filter: Optional[int] = None
    roles: Optional[List[Role]] = None
    features: Optional[List[str]] = None
    mfa_level: Optional[int] = None
    application_id: Optional[Snowflake] = None
    system_channel_id: Optional[Snowflake] = None
    system_channel_flags: Optional[int] = None
    rules_channel_id: Optional[Snowflake] = None
    max_presences: Optional[int] = None
    max_members: Optional[int] = None
    vanity_url_code: Optional[str] = None
    description: Optional[str] = None
    banner: Optional[str] = None
    premium_tier: Optional[int] = None
    premium_subscription_count: Optional[int] = None
    preferred_locale: Optional[str] = None
    public_updates_channel_id: Optional[Snowflake] = None
    max_video_channel_users: Optional[int] = None
    max_stage_video_channel_users: Optional[int] = None
    approximate_member_count: Optional[int] = None
    approximate_presence_count: Optional[int] = None
    nsfw_level: Optional[int] = None
    premium_progress_bar_enabled: Optional[bool] = None
    safety_alerts_channel_id: Optional[Snowflake] = None
    
    # TODO: Define models for these
    stickers: Optional[List[dict]] = None
    incidents_data: Optional[dict] = None
    welcome_screen: Optional[dict] = None