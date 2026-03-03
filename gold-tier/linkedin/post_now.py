#!/usr/bin/env python3
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

token = os.getenv('LINKEDIN_ACCESS_TOKEN')
person_id = os.getenv('LINKEDIN_PERSON_ID', '547329244')

posts_file = Path(__file__).parent / 'generated_posts.json'
with open(posts_file, encoding='utf-8') as f:
    posts = json.load(f)

drafts = [p for p in posts if p.get('status') == 'draft']

print(f"[INFO] Posting {len(drafts)} posts...")
print(f"[INFO] Person ID: {person_id}")
print()

posted = 0
for i, post in enumerate(drafts, 1):
    content = post['content']
    
    print(f"[{i}/{len(drafts)}] {post['topic'][:30]}...")
    
    data = {
        "author": f"urn:li:member:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    try:
        r = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            json=data,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            },
            timeout=30
        )
        
        if r.status_code in [200, 201]:
            print(f"  ✅ SUCCESS")
            post['status'] = 'posted'
            posted += 1
        else:
            print(f"  ❌ FAILED ({r.status_code}): {r.text[:100]}")
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)[:80]}")

with open(posts_file, 'w', encoding='utf-8') as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)

print()
print(f"[DONE] Posted: {posted}/{len(drafts)}")
