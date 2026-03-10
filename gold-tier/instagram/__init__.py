"""
Instagram Business API Integration Package
Production-ready module for Instagram automation
"""

__version__ = "1.0.0"
__author__ = "Gold Tier Autonomous Employee"

from .instagram_auth import InstagramAuth, InstagramAuthError, save_credentials_to_env
from .social_media_server import (
    InstagramAPI,
    AuditLogger,
    post_instagram_image,
    get_instagram_insights
)

__all__ = [
    "InstagramAuth",
    "InstagramAuthError",
    "InstagramAPI",
    "AuditLogger",
    "save_credentials_to_env",
    "post_instagram_image",
    "get_instagram_insights"
]
