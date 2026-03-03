#!/usr/bin/env python3
"""
Save generated posts to a CSV file for manual posting
This allows you to post them manually when network is available
"""

import json
from pathlib import Path

posts_file = Path(__file__).parent / 'generated_posts.json'

if not posts_file.exists():
    print("[ERROR] generated_posts.json not found")
    exit(1)

with open(posts_file, encoding='utf-8') as f:
    posts = json.load(f)

# Create CSV
import csv
csv_file = Path(__file__).parent / 'posts_to_post.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Pillar', 'Topic', 'Content', 'Status'])
    
    for post in posts:
        if post.get('status') == 'draft':
            writer.writerow([
                post.get('id'),
                post.get('pillar'),
                post.get('topic'),
                post.get('content'),
                'draft'
            ])

print(f"[SUCCESS] Saved {len([p for p in posts if p.get('status') == 'draft'])} posts to posts_to_post.csv")
print(f"[INFO] File: {csv_file}")
print("[INFO] You can now share these posts manually on LinkedIn")
