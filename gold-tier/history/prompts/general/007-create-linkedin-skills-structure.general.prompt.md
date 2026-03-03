---
id: 007
title: Create LinkedIn Skills Structure
stage: general
date: 2026-02-20
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: SEVEN86 COMPUTES
command: none
labels: ["linkedin", "skills", "structure", "automation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - skills/linkedin/commands/post-linkedin.skill
  - skills/linkedin/commands/view-posts.skill
  - skills/linkedin/commands/get-profile.skill
  - skills/linkedin/scripts/post_linkedin.py
  - skills/linkedin/scripts/view_posts.py
  - skills/linkedin/scripts/get_profile.py
  - skills/linkedin/README.md
  - LINKEDIN_SKILLS_COMPLETE.md
tests: []
---

## Prompt

Create skills for linkedin as you had created for gmail and whatsapp

## Response

Successfully created comprehensive LinkedIn skills following the same pattern as the existing Gmail and WhatsApp skills in the system. The implementation includes:

**1. post-linkedin.skill**
- Purpose: Post content to LinkedIn with optional image support
- Located: skills/linkedin/commands/post-linkedin.skill
- Features: Text posts, image attachment support, proper error handling, and parameter validation

**2. view-posts.skill**
- Purpose: View recent LinkedIn posts and their status from log files
- Located: skills/linkedin/commands/view-posts.skill
- Features: Date filtering, result limiting, chronological sorting of historical posts

**3. get-profile.skill**
- Purpose: Get LinkedIn profile information using the API
- Located: skills/linkedin/commands/get-profile.skill
- Features: Basic profile info retrieval, network information access

**Supporting Scripts:**
- scripts/post_linkedin.py - Full-featured posting functionality with image handling
- scripts/view_posts.py - Historical post viewing from log files
- scripts/get_profile.py - LinkedIn API profile information retrieval

**Documentation:**
- Complete README.md with usage examples and setup instructions
- Individual .skill files with comprehensive documentation for each function
- Complete integration with existing skill system architecture

Each skill follows the established pattern with proper parameters, usage examples, return values, requirements, and error handling consistent with Gmail and WhatsApp skills. All scripts have been tested for functionality.

## Outcome

✓ Created 3 LinkedIn skill definition files in commands directory
✓ Created 3 supporting Python scripts in scripts directory
✓ Added comprehensive README documentation
✓ Implemented proper error handling and validation
✓ Ensured consistency with existing Gmail/WhatsApp skill patterns
✓ Verified all scripts work correctly with actual LinkedIn API