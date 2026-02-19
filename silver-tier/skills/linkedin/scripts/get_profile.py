#!/usr/bin/env python3
"""
LinkedIn Skill: Get Profile Information
Script to retrieve LinkedIn profile information using the API
"""

import os
import json
import requests
from pathlib import Path
import dotenv

dotenv.load_dotenv()

def get_linkedin_profile():
    """
    Get LinkedIn profile information using the userinfo endpoint

    Returns:
        dict: Result dictionary with profile information or error
    """
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')

    if not access_token:
        return {
            "success": False,
            "error": "LinkedIn access token not found in environment variables"
        }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        # Get user info from LinkedIn
        userinfo_url = f"{api_url.rstrip('/')}/userinfo"
        response = requests.get(userinfo_url, headers=headers, timeout=15)

        if response.status_code == 200:
            user_data = response.json()

            return {
                "success": True,
                "profile": {
                    "id": user_data.get('sub'),
                    "name": user_data.get('name'),
                    "email": user_data.get('email'),
                    "given_name": user_data.get('given_name'),
                    "family_name": user_data.get('family_name'),
                    "locale": user_data.get('locale')
                }
            }
        else:
            return {
                "success": False,
                "error": f"Failed to get profile. Status: {response.status_code}, Response: {response.text}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during profile retrieval: {str(e)}"
        }


def get_linkedin_network_info():
    """
    Get LinkedIn network information (connections count, etc.)

    Returns:
        dict: Result dictionary with network information or error
    """
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')

    if not access_token:
        return {
            "success": False,
            "error": "LinkedIn access token not found in environment variables"
        }

    # Using the person ID from environment or getting from userinfo
    person_id = os.getenv('LINKEDIN_PERSON_ID', '').split(':')[-1]

    if not person_id or person_id == 'your_person_id':
        # Try to get the person ID from userinfo
        profile_result = get_linkedin_profile()
        if profile_result["success"]:
            person_id = profile_result["profile"]["id"]
        else:
            return profile_result  # Return the error from profile retrieval

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        # Get basic profile information using the person ID
        profile_url = f"{api_url.rstrip('/')}/me"
        response = requests.get(profile_url, headers=headers, timeout=15)

        if response.status_code == 200:
            profile_data = response.json()

            return {
                "success": True,
                "network_info": {
                    "id": profile_data.get('id'),
                    "firstName": profile_data.get('firstName', {}).get('localized', {}).get('en_US') if 'firstName' in profile_data else 'Unknown',
                    "lastName": profile_data.get('lastName', {}).get('localized', {}).get('en_US') if 'lastName' in profile_data else 'Unknown',
                    "profile_url": f"https://www.linkedin.com/in/{profile_data.get('id', '')}" if profile_data.get('id') else None
                }
            }
        else:
            return {
                "success": False,
                "error": f"Failed to get network info. Status: {response.status_code}, Response: {response.text}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during network info retrieval: {str(e)}"
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get LinkedIn profile information")
    parser.add_argument("--network", action='store_true', help="Get network information instead of basic profile")

    args = parser.parse_args()

    if args.network:
        result = get_linkedin_network_info()
    else:
        result = get_linkedin_profile()

    print(json.dumps(result, indent=2))

    if not result["success"]:
        exit(1)