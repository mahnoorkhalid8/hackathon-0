"""
Facebook Skill - AI Employee Skill for Facebook Integration

This skill provides Facebook posting capabilities for the AI employee.
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


class FacebookSkill:
    """Facebook integration skill for AI employee."""

    def __init__(self):
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.app_id = FACEBOOK_APP_ID
        self.app_secret = FACEBOOK_APP_SECRET

    def get_page_access_token(self) -> Optional[str]:
        """Get page access token using the user access token."""
        if not self.access_token:
            print("[ERROR] Missing required Facebook access token")
            return None

        # First, get all pages that the user can manage to find the specific page
        url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={self.access_token}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                pages = data.get('data', [])

                if not pages:
                    print("[ERROR] No pages found that user can manage. Make sure you are an admin/editor of the Facebook page.")
                    print(f"[ERROR] Requested page ID: {self.page_id}")
                    return None

                # Find the specific page by ID
                for page in pages:
                    if page['id'] == self.page_id:
                        return page['access_token']

                # If we get here, the page was not found in the user's accessible pages
                print(f"[ERROR] Page with ID {self.page_id} not found in user's managed pages.")
                print("[ERROR] Make sure you are an admin/editor of this page and that the page ID is correct.")

                # List available pages for debugging
                print("[DEBUG] Available pages:")
                for page in pages:
                    print(f"[DEBUG]   - Name: {page['name']}, ID: {page['id']}, Category: {page['category']}")
                return None
            else:
                print(f"[ERROR] Failed to get user's pages: {response.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Exception getting page access token: {e}")
            return None

    def post_message(self, message: str) -> Dict[str, Any]:
        """
        Post a text message to Facebook page.

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

        # Get page access token
        page_token = self.get_page_access_token()
        if not page_token:
            return {
                "success": False,
                "error": "Could not get page access token",
                "post_id": None
            }

        # Prepare post data
        post_data = {
            'message': message,
            'access_token': page_token
        }

        # Post to Facebook page
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
        response = requests.post(url, data=post_data)

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "post_id": result.get('id', 'unknown'),
                "message": f"Successfully posted to Facebook: {result.get('id', 'unknown')}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to post to Facebook: {response.status_code} - {response.text}",
                "post_id": None
            }

    def get_post_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get a summary of recent Facebook posts.

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

        # Get recent posts from Facebook page
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/posts?limit={limit}&access_token={self.access_token}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                posts = []

                for post in data.get('data', []):
                    post_info = {
                        'id': post.get('id'),
                        'message': post.get('message', '')[:200] + '...' if post.get('message') and len(post.get('message')) > 200 else post.get('message'),
                        'created_time': post.get('created_time'),
                        'shares': post.get('shares', {}).get('count', 0) if post.get('shares') else 0,
                        'likes': 0,  # Would need another API call to get like count
                        'comments': 0  # Would need another API call to get comment count
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
                    "error": f"Failed to get posts from Facebook: {response.status_code} - {response.text}",
                    "posts": []
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception getting posts from Facebook: {e}",
                "posts": []
            }

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Facebook skill actions.

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
                page_token = self.get_page_access_token()
                return {
                    "success": bool(page_token),
                    "page_access_token_valid": bool(page_token),
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
facebook_skill = FacebookSkill()


def execute_facebook_skill(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute Facebook skill action.

    Args:
        action: The action to perform
        **kwargs: Additional arguments

    Returns:
        Dictionary with result of the action
    """
    import asyncio

    # For synchronous execution, we'll call the methods directly
    if action == "post_message":
        message = kwargs.get('message', '')
        return facebook_skill.post_message(message)
    elif action == "get_summary":
        limit = kwargs.get('limit', 10)
        return facebook_skill.get_post_summary(limit)
    elif action == "check_credentials":
        if facebook_skill.access_token and facebook_skill.page_id:
            page_token = facebook_skill.get_page_access_token()
            return {
                "success": bool(page_token),
                "page_access_token_valid": bool(page_token),
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
    result = execute_facebook_skill("check_credentials")
    print("Check credentials result:", result)

    if result["success"]:
        result = execute_facebook_skill("get_summary", limit=5)
        print("Get summary result:", result)