# LinkedIn Skills

This directory contains skills for interacting with LinkedIn, including posting content and retrieving profile information.

## Available Skills

### `post-linkedin`
Post content to LinkedIn with optional image support.

- **Command**: `post-linkedin`
- **Description**: Post content to LinkedIn with support for text content and optional image attachments
- **Main script**: `scripts/post_linkedin.py`
- **Parameters**:
  - `content` (required): The content to post
  - `image_url` (optional): URL or file path to an image to include
  - `person_id` (optional): LinkedIn person ID to post as

### `view-posts`
View recent LinkedIn posts and their status.

- **Command**: `view-posts`
- **Description**: View recent LinkedIn posts from log files
- **Main script**: `scripts/view_posts.py`
- **Parameters**:
  - `days` (optional): Number of days to look back (default: 7)
  - `limit` (optional): Maximum number of posts to show (default: 10)

### `get-profile`
Get LinkedIn profile information using the API.

- **Command**: `get-profile`
- **Description**: Retrieve your LinkedIn profile information including name, email, and other profile details
- **Main script**: `scripts/get_profile.py`
- **Parameters**:
  - `network` (optional): Whether to get network information instead of basic profile

## Prerequisites

To use these LinkedIn skills, you need:

1. **LinkedIn API Access**: Valid LinkedIn API credentials
2. **Environment Variables**:
   - `LINKEDIN_ACCESS_TOKEN`: Your LinkedIn access token
   - `LINKEDIN_PERSON_ID`: Your LinkedIn person ID (optional, can be auto-detected)
   - `LINKEDIN_API_URL`: LinkedIn API endpoint (defaults to 'https://api.linkedin.com/v2/')

3. **Python Dependencies**: Make sure you have the required packages installed:
   - `requests`
   - `python-dotenv`

## Setup

1. **Configure Authentication**:
   Add your LinkedIn API credentials to your `.env` file:
   ```bash
   LINKEDIN_ACCESS_TOKEN=your_access_token_here
   LINKEDIN_PERSON_ID=your_person_id_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

## Usage Examples

### Post Content to LinkedIn:
```bash
python scripts/post_linkedin.py --content "Excited to share my latest update!"
```

### Post with Image:
```bash
python scripts/post_linkedin.py \
  --content "Check out my new project" \
  --image "path/to/image.jpg"
```

### View Recent Posts:
```bash
python scripts/view_posts.py --days 14 --limit 20
```

### Get Profile Information:
```bash
python scripts/get_profile.py
```

## Notes

- Make sure your LinkedIn API credentials have the necessary permissions for the operations you want to perform
- Image uploads may take a few seconds to process
- Posts are subject to LinkedIn's content policies and rate limits
- The `view-posts` skill reads from local log files in the `Logs` directory