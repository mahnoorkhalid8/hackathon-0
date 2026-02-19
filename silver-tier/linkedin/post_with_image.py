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

dotenv.load_dotenv(Path(__file__).parent.parent / '.env')

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
        register_url = f"{api_url}assets?action=registerUpload"
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
        
        if register_response.status_code not in [200, 201]:
            print(f"[ERROR] Failed to register image upload: {register_response.text}")
            return None
        
        register_json = register_response.json()
        
        # Extract upload URL and asset URN (more robust extraction)
        try:
            upload_url = register_json['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_json['value']['asset']
        except KeyError as e:
            print(f"[ERROR] Could not extract upload URL or asset from response: {e}")
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
    userinfo_url = f"{api_url}userinfo"
    userinfo_headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers, timeout=15)
        if userinfo_response.status_code == 200:
            sub_id = userinfo_response.json().get('sub')
            if sub_id:
                return f"urn:li:member:{sub_id}"
    except Exception:
        pass

    return f"urn:li:member:{fallback_person_urn}"


def post_to_linkedin_api(post_content, access_token, person_urn, image_url=None):
    """
    Post content to LinkedIn API with optional image
    """
    # LinkedIn API endpoint for creating posts
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')
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
            print("[LOG] Image upload failed, posting text only")
    else:
        print("[LOG] No image provided, posting text only")
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "NONE"

    # Make the API call
    print("\n[LOG] Post data being sent to LinkedIn:")
    print(json.dumps(post_data, indent=2))
    print(f"\n[LOG] Making POST request to: {api_url}ugcPosts")
    
    response = requests.post(
        f"{api_url}ugcPosts",
        headers=headers,
        json=post_data,
        timeout=30
    )

    return response


def build_share_url(share_urn):
    """Build public LinkedIn feed URL from share URN."""
    if not share_urn:
        return None
    return f"https://www.linkedin.com/feed/update/{share_urn}/"


def log_post_activity(content_preview, status):
    """Log the post activity to a JSON file"""
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f'{today}_linkedin.json'

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'linkedin_post',
        'content_preview': content_preview[:100],
        'status': status
    }

    # Read existing logs or create new
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    return log_file

def move_to_done_folder(source_file):
    """Move the approved file to the Done folder"""
    done_dir = Path(__file__).parent / "done"
    done_dir.mkdir(exist_ok=True)

    dest_file = done_dir / source_file.name
    source_file.rename(dest_file)

    return dest_file

def update_dashboard(post_content):
    """Update the Dashboard.md with the success message and increment task count"""
    dashboard_path = Path(__file__).parent.parent / "Dashboard.md"

    if dashboard_path.exists():
        content = dashboard_path.read_text(encoding='utf-8')

        # Update or add the success message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_entry = f"\n- [{timestamp}] LinkedIn post published: {post_content[:50]}..."

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

        # Add the new entry to recent activity
        if "## Recent Activity" in content:
            parts = content.split("## Recent Activity")
            content = parts[0] + "## Recent Activity" + new_entry + parts[1]
        else:
            content += f"\n\n## Recent Activity{new_entry}"

        dashboard_path.write_text(content, encoding='utf-8')
    else:
        # Create dashboard if it doesn't exist
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"""# AI Employee Dashboard

## Task Status
Completed Tasks: 1

## Recent Activity
- [{timestamp}] LinkedIn post published
"""
        dashboard_path.write_text(content, encoding='utf-8')

def process_generated_posts():
    """Process all generated LinkedIn posts from generated_posts.json"""
    posts_file = Path(__file__).parent / "generated_posts.json"
    
    if not posts_file.exists():
        print("[ERROR] generated_posts.json not found")
        return False
    
    # Load posts
    try:
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load posts: {e}")
        return False
    
    # Filter draft posts
    draft_posts = [p for p in posts if p.get('status') == 'draft']
    
    if not draft_posts:
        print("[INFO] No draft posts found")
        return True
    
    # Get LinkedIn configuration
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    person_id = os.getenv('LINKEDIN_PERSON_ID')
    
    if not access_token:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN not found in .env")
        return False
    
    if not person_id:
        print("[ERROR] LINKEDIN_PERSON_ID not found in .env")
        return False
    
    print(f"[INFO] Found {len(draft_posts)} draft posts to publish")
    print(f"[INFO] Using LinkedIn person ID: {person_id}")
    print()
    
    processed_count = 0
    failed_count = 0
    
    for idx, post in enumerate(draft_posts, 1):
        post_id = post.get('id')
        pillar = post.get('pillar', 'unknown')
        topic = post.get('topic', 'unknown')
        content = post.get('content', '')
        
        print(f"[{idx}/{len(draft_posts)}] Posting: {topic} ({pillar})")
        print(f"  Content: {content[:75]}...")
        
        try:
            response = post_to_linkedin_api(content, access_token, person_id)
            
            if response.status_code in [200, 201]:
                print(f"  [SUCCESS] ✅ Post published!")
                
                # Update status
                post['status'] = 'posted'
                post['posted_at'] = datetime.now().isoformat()
                
                try:
                    response_json = response.json()
                    post['linkedin_post_id'] = response_json.get('id', '')
                except:
                    pass
                
                # Log activity
                log_post_activity(content, 'posted')
                
                # Update dashboard
                update_dashboard(content)
                
                processed_count += 1
            else:
                print(f"  [ERROR] ❌ Failed: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                log_post_activity(content, 'failed')
                failed_count += 1
        
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            log_post_activity(content, 'error')
            failed_count += 1
        
        print()
        
        # Wait between posts
        if idx < len(draft_posts):
            print("[WAIT] Waiting 10 seconds before next post...")
            time.sleep(10)
    
    # Save updated posts
    try:
        with open(posts_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"[SAVED] Updated posts file")
    except Exception as e:
        print(f"[ERROR] Failed to save posts: {e}")
    
    print()
    print("=" * 70)
    print(f"[SUMMARY] Posted: {processed_count}, Failed: {failed_count}")
    print("=" * 70)
    
    return failed_count == 0

if __name__ == "__main__":
    print("=" * 70)
    print("LinkedIn Post Processor - Image Support")
    print("=" * 70)
    print()
    
    success = process_generated_posts()
    
    if success:
        print("\n✅ All posts published successfully!")
    else:
        print("\n⚠️  Some posts failed - check logs for details")
