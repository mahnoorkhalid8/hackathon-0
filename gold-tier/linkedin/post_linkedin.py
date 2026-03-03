#!/usr/bin/env python3
"""
Script to post LinkedIn content from approved files
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


def build_share_url(share_urn):
    """Build public LinkedIn feed URL from share URN."""
    if not share_urn:
        return None
    return f"https://www.linkedin.com/feed/update/{share_urn}/"


def log_post_activity(content_preview, status):
    """Log the post activity to a JSON file"""
    logs_dir = Path("Logs")
    logs_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f'{today}_linkedin.json'

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'linkedin_post',
        'content_preview': content_preview[:100].encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'),
        'status': status
    }

    # Read existing logs or create new
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except UnicodeDecodeError:
            # If there's a Unicode error reading the file, start fresh
            logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    return log_file

def move_to_done_folder(source_file):
    """Move the approved file to the Done folder"""
    done_dir = Path("Done")
    done_dir.mkdir(exist_ok=True)

    dest_file = done_dir / source_file.name
    source_file.rename(dest_file)

    return dest_file

def update_dashboard():
    """Update the Dashboard.md with the success message and increment task count"""
    dashboard_path = Path("Dashboard.md")

    if dashboard_path.exists():
        content = dashboard_path.read_text(encoding='utf-8')

        # Update or add the success message
        if "LinkedIn post successfully shared" not in content:
            content += f"\n\n- LinkedIn post successfully shared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Find and update the completed tasks count
        completed_match = re.search(r'Completed Tasks: (\d+)', content)
        if completed_match:
            current_count = int(completed_match.group(1))
            new_count = current_count + 1
            content = content.replace(
                f'Completed Tasks: {current_count}',
                f'Completed Tasks: {new_count}'
            )
        else:
            # If no Completed Tasks section found, add it
            content += f"\n\nCompleted Tasks: 1"

        dashboard_path.write_text(content, encoding='utf-8')
    else:
        # Create dashboard if it doesn't exist
        content = f"""# AI Employee Dashboard

## Task Status
Completed Tasks: 1

## Recent Activity
- LinkedIn post successfully shared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        dashboard_path.write_text(content, encoding='utf-8')

def process_approved_linkedin_posts():
    """Process all approved LinkedIn posts"""
    approved_dir = Path("Approved")

    # Find all LinkedIn post files in the approved folder
    linkedin_files = list(approved_dir.glob("*linkedin*.md"))
    if not linkedin_files:
        print("[INFO] No approved LinkedIn draft found in Approved/. Nothing to post.")
        return True

    had_failure = False
    processed_count = 0

    for file_path in linkedin_files:
        print(f"Processing LinkedIn post: {file_path.name}")

        # Extract the post content from the file
        content = file_path.read_text(encoding='utf-8')

        # Extract content between "Post Content" and "Approval Instructions"
        lines = content.split('\n')
        post_content_lines = []
        in_post_content = False

        for line in lines:
            if "## Post Content" in line:
                in_post_content = True
                continue
            elif "## Image URL" in line or "## Approval Instructions" in line:
                break
            elif in_post_content:
                post_content_lines.append(line)

        # Clean up the extracted content
        post_content = '\n'.join(post_content_lines).strip()

        # Remove the header markers and empty lines at the beginning
        post_content = '\n'.join([line for line in post_content.split('\n') if not line.startswith('#')])
        post_content = post_content.strip()

        # Extract image URL/path from section-based draft format
        image_url = None
        image_section_match = re.search(
            r'##\s*Image URL\s*\n+(.+?)(?:\n##\s*|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if image_section_match:
            image_candidate = image_section_match.group(1).strip().splitlines()[0].strip()
            if image_candidate and not image_candidate.startswith('-'):
                image_url = image_candidate
                print(f"Found image reference: {image_url}")

        # print(f"Extracted content: {post_content[:100].encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')}...")
        print("Extracted content (character count):", len(post_content))

        # Get LinkedIn configuration
        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        person_id = os.getenv('LINKEDIN_PERSON_ID', '').split(':')[-1]  # Extract just the ID part

        if not access_token:
            print("[ERROR] LinkedIn access token not found in environment variables")
            return False

        if not person_id or person_id == 'your_person_id':
            print("[ERROR] LinkedIn person ID not properly configured")
            return False

        print(f"Attempting to post to LinkedIn profile: urn:li:person:{person_id}")

        try:
            # Actually post to LinkedIn with optional image
            response = post_to_linkedin_api(post_content, access_token, person_id, image_url)

            if response.status_code in [200, 201]:
                print(f"[SUCCESS] LinkedIn post published successfully!")
                print(f"Response: {response.text}")
                share_urn = None
                share_url = None
                try:
                    response_json = response.json()
                    share_urn = response_json.get("id")
                    share_url = build_share_url(share_urn)
                except Exception:
                    pass

                if share_url:
                    print(f"[INFO] Open post URL: {share_url}")

                # Log the successful post
                log_file = log_post_activity(post_content, 'posted')
                print(f"Activity logged to: {log_file}")

                # Move the file to Done folder
                moved_file = move_to_done_folder(file_path)
                print(f"Moved approved file to: {moved_file}")

                # Update the dashboard
                update_dashboard()
                print("Dashboard updated with successful post")
                processed_count += 1
            else:
                print(f"[ERROR] Failed to post to LinkedIn. Status: {response.status_code}, Response: {response.text}")

                # Log the failed post
                log_file = log_post_activity(post_content, 'failed')
                print(f"Activity logged to: {log_file}")
                had_failure = True
        except Exception as e:
            print(f"[ERROR] Exception during posting: {str(e)}")
            import traceback
            traceback.print_exc()
            log_file = log_post_activity(post_content, 'error')
            print(f"Activity logged to: {log_file}")
            had_failure = True

    print(f"\n[SUMMARY] Processed {processed_count} LinkedIn posts")
    if had_failure:
        print("[WARNING] Some posts failed to publish")
    return not had_failure

if __name__ == "__main__":
    print("LinkedIn Post Processor")
    print("=" * 50)
    success = process_approved_linkedin_posts()
    if success:
        print("\n✅ All LinkedIn posts processed successfully!")
    else:
        print("\n❌ Some LinkedIn posts failed to process")