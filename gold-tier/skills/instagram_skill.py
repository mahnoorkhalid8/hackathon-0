"""
Instagram Skill - AI Employee Skill for Instagram Integration

This skill provides Instagram posting capabilities for the AI employee using Facebook's Graph API.
Instagram business accounts are managed through Facebook.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import asyncio

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')


class InstagramSkill:
    """Instagram integration skill for AI employee."""

    def __init__(self):
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.app_id = FACEBOOK_APP_ID
        self.app_secret = FACEBOOK_APP_SECRET

    def get_instagram_account_id(self) -> Optional[str]:
        """Get Instagram account ID associated with the Facebook page."""
        if not self.access_token or not self.page_id:
            print("[ERROR] Missing required Facebook credentials")
            return None

        # Get Instagram account ID from Facebook page
        url = f"https://graph.facebook.com/v19.0/{self.page_id}?fields=instagram_accounts&access_token={self.access_token}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('instagram_accounts', {}).get('data', [])
                if accounts:
                    return accounts[0].get('id')
                else:
                    print("[ERROR] No Instagram account associated with this Facebook page")
                    return None
            else:
                print(f"[ERROR] Failed to get Instagram account: {response.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Exception getting Instagram account: {e}")
            return None

    def post_message(self, message: str) -> Dict[str, Any]:
        """
        Post a text message to Instagram (through Facebook's Graph API).

        Args:
            message: The text message to post

        Returns:
            Dictionary with result of the post operation
        """
        if not message or not message.strip():
            return {
                "success": False,
                "error": "Empty message provided",
                "post_id": None
            }

        # Get Instagram account ID
        instagram_account_id = self.get_instagram_account_id()
        if not instagram_account_id:
            return {
                "success": False,
                "error": "Could not get Instagram account ID",
                "post_id": None
            }

        # First, create the media object
        media_data = {
            'text': message,
            'creation_id': str(int(asyncio.get_event_loop().time() * 1000000)),  # Use timestamp as creation ID
            'access_token': self.access_token
        }

        # Create the media object
        url = f"https://graph.facebook.com/v19.0/{instagram_account_id}/media"
        response = requests.post(url, data=media_data)

        if response.status_code == 200:
            media_result = response.json()
            creation_id = media_result.get('id')

            if creation_id:
                # Publish the media
                publish_data = {
                    'creation_id': creation_id,
                    'access_token': self.access_token
                }

                publish_url = f"https://graph.facebook.com/v19.0/{instagram_account_id}/media_publish"
                publish_response = requests.post(publish_url, data=publish_data)

                if publish_response.status_code == 200:
                    publish_result = publish_response.json()
                    post_id = publish_result.get('id')
                    return {
                        "success": True,
                        "post_id": post_id,
                        "message": f"Successfully posted to Instagram: {post_id}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to publish Instagram post: {publish_response.status_code} - {publish_response.text}",
                        "post_id": None
                    }
            else:
                return {
                    "success": False,
                    "error": "Could not get creation ID from media object",
                    "post_id": None
                }
        else:
            return {
                "success": False,
                "error": f"Failed to create Instagram media object: {response.status_code} - {response.text}",
                "post_id": None
            }

    def get_post_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get a summary of recent Instagram posts.

        Args:
            limit: Number of recent posts to retrieve (default: 10)

        Returns:
            Dictionary with recent posts summary
        """
        if not self.access_token or not self.page_id:
            return {
                "success": False,
                "error": "Missing required Facebook credentials",
                "posts": []
            }

        # Get Instagram account ID
        instagram_account_id = self.get_instagram_account_id()
        if not instagram_account_id:
            return {
                "success": False,
                "error": "Could not get Instagram account ID",
                "posts": []
            }

        # Get recent posts from Instagram account
        url = f"https://graph.facebook.com/v19.0/{instagram_account_id}/media?fields=id,caption,timestamp,like_count,comments_count,media_type,media_url&limit={limit}&access_token={self.access_token}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                posts = []

                for post in data.get('data', []):
                    post_info = {
                        'id': post.get('id'),
                        'caption': post.get('caption', '')[:200] + '...' if post.get('caption') and len(post.get('caption')) > 200 else post.get('caption'),
                        'timestamp': post.get('timestamp'),
                        'media_type': post.get('media_type'),
                        'like_count': post.get('like_count', 0),
                        'comments_count': post.get('comments_count', 0)
                    }
                    posts.append(post_info)

                return {
                    "success": True,
                    "posts": posts,
                    "total_posts": len(posts)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get Instagram posts: {response.status_code} - {response.text}",
                    "posts": []
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception getting Instagram posts: {e}",
                "posts": []
            }

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Instagram skill actions.

        Args:
            action: The action to perform ('post_message', 'get_summary', etc.)
            **kwargs: Additional arguments for the action

        Returns:
            Dictionary with result of the action
        """
        if action == "post_message":
            message = kwargs.get('message', '')
            return self.post_message(message)
        elif action == "get_summary":
            limit = kwargs.get('limit', 10)
            return self.get_post_summary(limit)
        elif action == "check_credentials":
            if self.access_token and self.page_id:
                instagram_id = self.get_instagram_account_id()
                return {
                    "success": bool(instagram_id),
                    "instagram_account_connected": bool(instagram_id),
                    "credentials_present": True
                }
            else:
                return {
                    "success": False,
                    "credentials_present": False
                }
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "supported_actions": ["post_message", "get_summary", "check_credentials"]
            }


# Create a global instance for the orchestrator to use
instagram_skill = InstagramSkill()


def execute_instagram_skill(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute Instagram skill action.

    Args:
        action: The action to perform
        **kwargs: Additional arguments

    Returns:
        Dictionary with result of the action
    """
    if action == "post_message":
        message = kwargs.get('message', '')
        return instagram_skill.post_message(message)
    elif action == "get_summary":
        limit = kwargs.get('limit', 10)
        return instagram_skill.get_post_summary(limit)
    elif action == "check_credentials":
        if instagram_skill.access_token and instagram_skill.page_id:
            instagram_id = instagram_skill.get_instagram_account_id()
            return {
                "success": bool(instagram_id),
                "instagram_account_connected": bool(instagram_id),
                "credentials_present": True
            }
        else:
            return {
                "success": False,
                "credentials_present": False
            }
    else:
        return {
            "success": False,
            "error": f"Unknown action: {action}",
            "supported_actions": ["post_message", "get_summary", "check_credentials"]
        }


# Example usage
if __name__ == "__main__":
    # Test the skill
    result = execute_instagram_skill("check_credentials")
    print("Check credentials result:", result)

    if result["success"]:
        result = execute_instagram_skill("get_summary", limit=5)
        print("Get summary result:", result)