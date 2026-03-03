#!/usr/bin/env python3
"""
LinkedIn Skill: Post Content
Script to post content to LinkedIn with optional image support
"""

import os
import json
import requests
import time
from pathlib import Path
from datetime import datetime
import dotenv
import re
import mimetypes

dotenv.load_dotenv()

def upload_image_to_linkedin(image_path, access_token, author_urn):
    """
    Upload image to LinkedIn and return the image asset URN
    Supports both local file paths and HTTP URLs
    """
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')

    try:
        if image_path.startswith('http://') or image_path.startswith('https://'):
            print(f"Downloading image from URL: {image_path}")
            img_response = requests.get(image_path, timeout=10)
            if img_response.status_code != 200:
                print(f"[WARNING] Failed to download image from {image_path}")
                return None
            image_data = img_response.content
        else:
            file_path = Path(image_path)
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path

            print(f"Reading image from local file: {file_path}")

            if not file_path.exists():
                print(f"[WARNING] Image file not found: {file_path}")
                return None

            with open(file_path, 'rb') as f:
                image_data = f.read()

        print(f"Image size: {len(image_data)} bytes")
        if len(image_data) > 5 * 1024 * 1024:
            print("[WARNING] Large image detected (>5MB). LinkedIn may delay processing in feed.")

        # Step 1: Register upload
        register_url = f"{api_url}/assets?action=registerUpload"
        register_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        register_data = {
            "registerUploadRequest": {
                "owner": author_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        print("[LOG] Registering image upload with LinkedIn...")
        register_response = requests.post(register_url, headers=register_headers, json=register_data)
        print(f"[LOG] Register response status: {register_response.status_code}")
        print(f"[LOG] Register response: {register_response.text}")

        if register_response.status_code not in [200, 201]:
            print(f"[ERROR] Failed to register image upload: {register_response.text}")
            return None

        register_json = register_response.json()

        # Extract upload URL and asset URN (more robust extraction)
        try:
            upload_url = register_json['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_json['value']['asset']
        except KeyError as e:
            print(f"[ERROR] Could not extract upload URL or asset URN from response: {e}")
            print(f"[LOG] Full response: {json.dumps(register_json, indent=2)}")
            return None

        print(f"[LOG] Got upload URL and asset URN: {asset_urn}")

        # Step 2: Upload image data
        print("[LOG] Uploading image data to LinkedIn...")
        content_type, _ = mimetypes.guess_type(str(image_path))
        if not content_type or not content_type.startswith("image/"):
            content_type = "image/jpeg"

        upload_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': content_type
        }

        upload_response = requests.put(upload_url, data=image_data, headers=upload_headers)
        print(f"[LOG] Upload response status: {upload_response.status_code}")

        if upload_response.status_code not in [200, 201, 204]:
            print(f"[ERROR] Image upload failed: {upload_response.text}")
            return None

        print(f"[SUCCESS] Image uploaded successfully with asset URN: {asset_urn}")

        # Give LinkedIn media service time to finalize asset before creating post.
        print("[LOG] Waiting 8 seconds for image processing...")
        time.sleep(8)

        return asset_urn

    except Exception as e:
        print(f"[ERROR] Exception during image upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_author_urn(access_token, fallback_person_urn):
    """Resolve author urn from userinfo endpoint with fallback to configured person id."""
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')
    userinfo_url = f"{api_url}/userinfo"
    userinfo_headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers, timeout=15)
        if userinfo_response.status_code == 200:
            sub_id = userinfo_response.json().get('sub')
            if sub_id:
                # Try the standard person URN first
                person_urn = f"urn:li:person:{sub_id}"
                return person_urn
    except Exception:
        pass

    # Fallback to the configured person ID
    return f"urn:li:person:{fallback_person_urn}"


def post_to_linkedin_api(post_content, access_token, person_urn, image_url=None):
    """
    Post content to LinkedIn API with optional image
    """
    # LinkedIn API endpoint for creating posts
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/').rstrip('/')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    author_urn = get_author_urn(access_token, person_urn)

    # Build the post data
    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                }
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Add image if provided
    if image_url:
        print(f"\n[LOG] Processing image: {image_url}")
        image_asset_urn = upload_image_to_linkedin(image_url, access_token, author_urn)

        if image_asset_urn:
            print(f"[LOG] Adding image to post with asset: {image_asset_urn}")
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "media": image_asset_urn
                }
            ]
            print("[LOG] Image configuration added to post data")
        else:
            raise RuntimeError("Image upload failed. Post canceled to avoid text-only publish.")
    else:
        print("[LOG] No image URL provided, posting text only")
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "NONE"

    # Make the API call
    print("\n[LOG] Post data being sent to LinkedIn:")
    print(json.dumps(post_data, indent=2))
    print(f"\n[LOG] Making POST request to: {api_url}/ugcPosts")

    response = requests.post(
        f"{api_url}/ugcPosts",
        headers=headers,
        json=post_data
    )

    return response


def post_linkedin(content, image_url=None, person_id=None):
    """
    Function to post content to LinkedIn

    Args:
        content (str): The content to post
        image_url (str, optional): Path or URL to image to include
        person_id (str, optional): LinkedIn person ID to post as

    Returns:
        dict: Result dictionary with success status and any error message
    """
    # Get LinkedIn configuration
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not person_id:
        person_id = os.getenv('LINKEDIN_PERSON_ID', '').split(':')[-1]  # Extract just the ID part

    if not access_token:
        return {
            "success": False,
            "error": "LinkedIn access token not found in environment variables"
        }

    if not person_id or person_id == 'your_person_id':
        return {
            "success": False,
            "error": "LinkedIn person ID not properly configured"
        }

    try:
        # Actually post to LinkedIn with optional image
        response = post_to_linkedin_api(content, access_token, person_id, image_url)

        if response.status_code in [200, 201]:
            return {
                "success": True,
                "message_id": response.json().get("id"),
                "message": f"LinkedIn post published successfully! Status: {response.status_code}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to post to LinkedIn. Status: {response.status_code}, Response: {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during posting: {str(e)}"
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Post content to LinkedIn")
    parser.add_argument("--content", type=str, required=True, help="Content to post")
    parser.add_argument("--image", type=str, help="Image URL or file path to include")
    parser.add_argument("--person-id", type=str, help="LinkedIn person ID")

    args = parser.parse_args()

    result = post_linkedin(args.content, args.image, args.person_id)

    if result["success"]:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
        exit(1)