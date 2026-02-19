"""
Quick script to view one draft post and copy to LinkedIn
"""

import json

# Read the generated posts
with open('generated_posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

print("="*70)
print("LINKEDIN DRAFT POST VIEWER")
print("="*70)
print()

# Find first draft post
draft_post = None
for post in posts:
    if post.get('status') == 'draft':
        draft_post = post
        break

if not draft_post:
    print("No draft posts found! Generate some first:")
    print("python linkedin_post_generator.py --pillar all")
    exit()

print(f"POST TO COPY TO LINKEDIN:")
print(f"ID: {draft_post['id']}")
print(f"Pillar: {draft_post['pillar']}")
print(f"Topic: {draft_post['topic']}")
print()
print("-" * 50)
print("COPY THE CONTENT BELOW TO LINKEDIN:")
print("-" * 50)
print(draft_post['content'])
print("-" * 50)
print(f"POSTED AT: {draft_post['generated_at']}")
print()
print("After posting on LinkedIn:")
print("1. Change status in generated_posts.json from 'draft' to 'posted'")
print("2. Or run: python -c \"import json; p=json.load(open('generated_posts.json')); [post.update({'status':'posted'}) for post in p if post['id']==1]; json.dump(p, open('generated_posts.json','w'), indent=2)\"")