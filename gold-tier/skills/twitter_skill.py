"""
Twitter (X) Skill - AI Employee Skill for Twitter/X Integration

This skill provides Twitter/X posting capabilities for the AI employee.
Note: Twitter API v2 requires Bearer Token or OAuth 2.0 authentication.
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

TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')


class TwitterSkill:
    """Twitter/X integration skill for AI employee."""

    def __init__(self):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.api_key = TWITTER_API_KEY
        self.api_secret = TWITTER_API_SECRET
        self.access_token = TWITTER_ACCESS_TOKEN
        self.access_token_secret = TWITTER_ACCESS_TOKEN_SECRET

    def get_headers(self) -> Dict[str, str]:
        """Get headers for Twitter API requests."""
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        return headers

    def post_tweet(self, text: str) -> Dict[str, Any]:
        """
        Post a tweet to Twitter/X.

        Args:
            text: The text to tweet

        Returns:
            Dictionary with result of the tweet operation
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Empty tweet provided",
                "tweet_id": None
            }

        # Check if we have the required credentials
        if not self.bearer_token:
            return {
                "success": False,
                "error": "Missing TWITTER_BEARER_TOKEN in environment",
                "tweet_id": None
            }

        # Prepare tweet data
        tweet_data = {
            "text": text[:280]  # Twitter has a 280 character limit
        }

        # Post to Twitter API v2
        url = "https://api.twitter.com/2/tweets"
        headers = self.get_headers()

        try:
            response = requests.post(url, headers=headers, json=tweet_data)
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "tweet_id": result.get('data', {}).get('id'),
                    "message": f"Successfully posted to Twitter: {result.get('data', {}).get('id', 'unknown')}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to post to Twitter: {response.status_code} - {response.text}",
                    "tweet_id": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception posting to Twitter: {e}",
                "tweet_id": None
            }

    def get_recent_tweets(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent tweets from the authenticated user.

        Args:
            limit: Number of recent tweets to retrieve (default: 10)

        Returns:
            Dictionary with recent tweets
        """
        if not self.bearer_token:
            return {
                "success": False,
                "error": "Missing TWITTER_BEARER_TOKEN in environment",
                "tweets": []
            }

        # Get the user ID first
        user_url = "https://api.twitter.com/2/users/me"
        headers = self.get_headers()

        try:
            # Get user info
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get user info: {user_response.status_code} - {user_response.text}",
                    "tweets": []
                }

            user_data = user_response.json()
            user_id = user_data.get('data', {}).get('id')

            if not user_id:
                return {
                    "success": False,
                    "error": "Could not get user ID",
                    "tweets": []
                }

            # Get recent tweets
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': min(limit, 100),  # Twitter API max is 100
                'tweet.fields': 'created_at,public_metrics,author_id'
            }

            tweets_response = requests.get(tweets_url, headers=headers, params=params)

            if tweets_response.status_code == 200:
                data = tweets_response.json()
                tweets = []

                for tweet in data.get('data', []):
                    tweet_info = {
                        'id': tweet.get('id'),
                        'text': tweet.get('text', '')[:200] + '...' if len(tweet.get('text', '')) > 200 else tweet.get('text'),
                        'created_at': tweet.get('created_at'),
                        'retweet_count': tweet.get('public_metrics', {}).get('retweet_count', 0),
                        'like_count': tweet.get('public_metrics', {}).get('like_count', 0),
                        'reply_count': tweet.get('public_metrics', {}).get('reply_count', 0),
                        'quote_count': tweet.get('public_metrics', {}).get('quote_count', 0)
                    }
                    tweets.append(tweet_info)

                return {
                    "success": True,
                    "tweets": tweets,
                    "total_tweets": len(tweets)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get tweets: {tweets_response.status_code} - {tweets_response.text}",
                    "tweets": []
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception getting tweets: {e}",
                "tweets": []
            }

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Twitter skill actions.

        Args:
            action: The action to perform ('post_tweet', 'get_tweets', etc.)
            **kwargs: Additional arguments for the action

        Returns:
            Dictionary with result of the action
        """
        if action == "post_tweet":
            text = kwargs.get('text', '')
            return self.post_tweet(text)
        elif action == "get_tweets":
            limit = kwargs.get('limit', 10)
            return self.get_recent_tweets(limit)
        elif action == "check_credentials":
            has_bearer = bool(self.bearer_token)
            if has_bearer:
                # Test the API
                user_url = "https://api.twitter.com/2/users/me"
                headers = self.get_headers()

                try:
                    response = requests.get(user_url, headers=headers)
                    if response.status_code == 200:
                        user_data = response.json()
                        return {
                            "success": True,
                            "authenticated": True,
                            "user_name": user_data.get('data', {}).get('name'),
                            "user_id": user_data.get('data', {}).get('id')
                        }
                    else:
                        return {
                            "success": False,
                            "authenticated": False,
                            "error": f"Auth failed: {response.status_code}"
                        }
                except Exception:
                    return {
                        "success": False,
                        "authenticated": False
                    }
            else:
                return {
                    "success": False,
                    "authenticated": False,
                    "credentials_present": bool(self.bearer_token)
                }
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "supported_actions": ["post_tweet", "get_tweets", "check_credentials"]
            }


# Create a global instance for the orchestrator to use
twitter_skill = TwitterSkill()


def execute_twitter_skill(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute Twitter skill action.

    Args:
        action: The action to perform
        **kwargs: Additional arguments

    Returns:
        Dictionary with result of the action
    """
    if action == "post_tweet":
        text = kwargs.get('text', '')
        return twitter_skill.post_tweet(text)
    elif action == "get_tweets":
        limit = kwargs.get('limit', 10)
        return twitter_skill.get_recent_tweets(limit)
    elif action == "check_credentials":
        if twitter_skill.bearer_token:
            # Test the API
            user_url = "https://api.twitter.com/2/users/me"
            headers = {"Authorization": f"Bearer {twitter_skill.bearer_token}"}

            try:
                response = requests.get(user_url, headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "success": True,
                        "authenticated": True,
                        "user_name": user_data.get('data', {}).get('name'),
                        "user_id": user_data.get('data', {}).get('id')
                    }
                else:
                    return {
                        "success": False,
                        "authenticated": False,
                        "error": f"Auth failed: {response.status_code}"
                    }
            except Exception:
                return {
                    "success": False,
                    "authenticated": False
                }
        else:
            return {
                "success": False,
                "authenticated": False,
                "credentials_present": bool(twitter_skill.bearer_token)
            }
    else:
        return {
            "success": False,
            "error": f"Unknown action: {action}",
            "supported_actions": ["post_tweet", "get_tweets", "check_credentials"]
        }


# Example usage
if __name__ == "__main__":
    # Test the skill
    result = execute_twitter_skill("check_credentials")
    print("Check credentials result:", result)

    if result["success"]:
        result = execute_twitter_skill("get_tweets", limit=5)
        print("Get tweets result:", result)