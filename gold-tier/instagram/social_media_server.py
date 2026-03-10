"""
Social Media MCP Server - Gold Tier Autonomous Employee
Provides Instagram, Facebook, and Twitter tools with comprehensive audit logging
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MCP Server imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("Warning: MCP library not installed. Install with: pip install mcp")
    Server = None


class AuditLogger:
    """Centralized audit logging for all social media operations"""

    def __init__(self, log_file: str = "logs/instagram_logs.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)

        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.write_text("[]")

    def log(self, tool_name: str, input_data: Dict, response_data: Dict, status: str):
        """
        Log every API call with full context

        Args:
            tool_name: Name of the tool/operation
            input_data: Full input parameters
            response_data: API response or error details
            status: success or error
        """
        try:
            # Read existing logs
            logs = json.loads(self.log_file.read_text())

            # Create log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tool": tool_name,
                "input": input_data,
                "response": response_data,
                "status": status
            }

            logs.append(log_entry)

            # Write back
            self.log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            print(f"Warning: Failed to write audit log: {e}")


class InstagramAPI:
    """Instagram Business API wrapper with 2-step posting process"""

    GRAPH_API_BASE = "https://graph.facebook.com/v21.0"

    def __init__(self, business_id: str, access_token: str, logger: AuditLogger):
        self.business_id = business_id
        self.access_token = access_token
        self.logger = logger

    def create_media_container(
        self,
        image_url: str,
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        user_tags: Optional[list] = None
    ) -> Dict:
        """
        Step 1: Create media container for Instagram post

        Args:
            image_url: Public URL of the image to post
            caption: Post caption (optional)
            location_id: Instagram location ID (optional)
            user_tags: List of user tags (optional)

        Returns:
            Dict with container_id or error
        """
        url = f"{self.GRAPH_API_BASE}/{self.business_id}/media"

        params = {
            "image_url": image_url,
            "access_token": self.access_token
        }

        if caption:
            params["caption"] = caption
        if location_id:
            params["location_id"] = location_id
        if user_tags:
            params["user_tags"] = json.dumps(user_tags)

        input_data = {
            "business_id": self.business_id,
            "image_url": image_url,
            "caption": caption,
            "location_id": location_id,
            "user_tags": user_tags
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200 and "id" in response_data:
                self.logger.log(
                    "instagram_create_container",
                    input_data,
                    {"status_code": 200, "container_id": response_data["id"]},
                    "success"
                )

                return {
                    "success": True,
                    "container_id": response_data["id"]
                }
            else:
                error_message = response_data.get("error", {}).get("message", "Container creation failed")
                error_code = response_data.get("error", {}).get("code", "unknown")

                self.logger.log(
                    "instagram_create_container",
                    input_data,
                    response_data,
                    "error"
                )

                return {
                    "success": False,
                    "error": error_message,
                    "error_code": error_code,
                    "details": response_data
                }

        except requests.RequestException as e:
            self.logger.log(
                "instagram_create_container",
                input_data,
                {"error": str(e)},
                "error"
            )

            return {
                "success": False,
                "error": f"Network error: {e}",
                "error_code": "network_error"
            }

    def publish_media_container(self, container_id: str) -> Dict:
        """
        Step 2: Publish the media container to Instagram

        Args:
            container_id: Container ID from create_media_container

        Returns:
            Dict with post_id or error
        """
        url = f"{self.GRAPH_API_BASE}/{self.business_id}/media_publish"

        params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }

        input_data = {
            "business_id": self.business_id,
            "container_id": container_id
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200 and "id" in response_data:
                self.logger.log(
                    "instagram_publish_container",
                    input_data,
                    {"status_code": 200, "post_id": response_data["id"]},
                    "success"
                )

                return {
                    "success": True,
                    "post_id": response_data["id"]
                }
            else:
                error_message = response_data.get("error", {}).get("message", "Publishing failed")
                error_code = response_data.get("error", {}).get("code", "unknown")

                self.logger.log(
                    "instagram_publish_container",
                    input_data,
                    response_data,
                    "error"
                )

                return {
                    "success": False,
                    "error": error_message,
                    "error_code": error_code,
                    "details": response_data
                }

        except requests.RequestException as e:
            self.logger.log(
                "instagram_publish_container",
                input_data,
                {"error": str(e)},
                "error"
            )

            return {
                "success": False,
                "error": f"Network error: {e}",
                "error_code": "network_error"
            }

    def post_image(
        self,
        image_url: str,
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        user_tags: Optional[list] = None
    ) -> Dict:
        """
        Complete 2-step process: Create container and publish

        Args:
            image_url: Public URL of the image
            caption: Post caption
            location_id: Instagram location ID
            user_tags: List of user tags

        Returns:
            Dict with post_id or error
        """
        # Step 1: Create container
        container_result = self.create_media_container(
            image_url, caption, location_id, user_tags
        )

        if not container_result["success"]:
            return container_result

        # Step 2: Publish container
        publish_result = self.publish_media_container(container_result["container_id"])

        return publish_result

    def get_media_insights(self, media_id: str, metrics: list = None) -> Dict:
        """
        Get insights for a published media item

        Args:
            media_id: Instagram media ID
            metrics: List of metrics to retrieve (engagement, impressions, reach, saved)

        Returns:
            Dict with insights data
        """
        if metrics is None:
            metrics = ["engagement", "impressions", "reach", "saved"]

        url = f"{self.GRAPH_API_BASE}/{media_id}/insights"
        params = {
            "metric": ",".join(metrics),
            "access_token": self.access_token
        }

        input_data = {
            "media_id": media_id,
            "metrics": metrics
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                self.logger.log(
                    "instagram_get_insights",
                    input_data,
                    {"status_code": 200, "data_count": len(response_data.get("data", []))},
                    "success"
                )

                return {
                    "success": True,
                    "insights": response_data.get("data", [])
                }
            else:
                self.logger.log(
                    "instagram_get_insights",
                    input_data,
                    response_data,
                    "error"
                )

                return {
                    "success": False,
                    "error": response_data.get("error", {}).get("message", "Failed to fetch insights"),
                    "details": response_data
                }

        except requests.RequestException as e:
            self.logger.log(
                "instagram_get_insights",
                input_data,
                {"error": str(e)},
                "error"
            )

            return {
                "success": False,
                "error": f"Network error: {e}"
            }


class SocialMediaServer:
    """MCP Server for Social Media Operations"""

    def __init__(self):
        self.logger = AuditLogger()

        # Load Instagram credentials
        self.ig_business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
        self.ig_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_token_expires = os.getenv("IG_TOKEN_EXPIRES_AT")

        # Initialize Instagram API
        if self.ig_business_id and self.ig_access_token:
            self.instagram = InstagramAPI(
                self.ig_business_id,
                self.ig_access_token,
                self.logger
            )
        else:
            self.instagram = None
            print("Warning: Instagram credentials not found in environment")

        # Initialize MCP server
        if Server:
            self.server = Server("social-media-server")
            self._register_tools()
        else:
            self.server = None

    def _register_tools(self):
        """Register all MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="instagram_post_image",
                    description="Post an image to Instagram Business account using 2-step process (create container + publish)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "Public URL of the image to post"
                            },
                            "caption": {
                                "type": "string",
                                "description": "Post caption (optional)"
                            },
                            "location_id": {
                                "type": "string",
                                "description": "Instagram location ID (optional)"
                            }
                        },
                        "required": ["image_url"]
                    }
                ),
                Tool(
                    name="instagram_get_insights",
                    description="Get performance insights for an Instagram post",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "media_id": {
                                "type": "string",
                                "description": "Instagram media ID"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Metrics to retrieve (engagement, impressions, reach, saved)"
                            }
                        },
                        "required": ["media_id"]
                    }
                ),
                Tool(
                    name="generate_ceo_briefing",
                    description="Generate executive briefing with Instagram analytics, system health, and marketing ROI for the last N days",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "description": "Number of days to analyze (default: 7)",
                                "default": 7
                            },
                            "save": {
                                "type": "boolean",
                                "description": "Save report to file (default: true)",
                                "default": True
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            if not self.instagram:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Instagram API not initialized. Check credentials."
                    })
                )]

            if name == "instagram_post_image":
                result = self.instagram.post_image(
                    image_url=arguments.get("image_url"),
                    caption=arguments.get("caption"),
                    location_id=arguments.get("location_id")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "instagram_get_insights":
                result = self.instagram.get_media_insights(
                    media_id=arguments.get("media_id"),
                    metrics=arguments.get("metrics")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "generate_ceo_briefing":
                from ceo_briefing import generate_ceo_briefing
                result = generate_ceo_briefing(
                    days=arguments.get("days", 7),
                    save=arguments.get("save", True)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Unknown tool: {name}"
                    })
                )]

    async def run(self):
        """Run the MCP server"""
        if self.server:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        else:
            print("MCP server not available. Install mcp library.")


# Standalone functions for direct usage (non-MCP mode)
def post_instagram_image(
    image_url: str,
    caption: Optional[str] = None,
    location_id: Optional[str] = None
) -> Dict:
    """
    Standalone function to post image to Instagram

    Args:
        image_url: Public URL of the image
        caption: Post caption
        location_id: Instagram location ID

    Returns:
        Dict with result
    """
    logger = AuditLogger()
    business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not business_id or not access_token:
        return {
            "success": False,
            "error": "Instagram credentials not found in environment"
        }

    instagram = InstagramAPI(business_id, access_token, logger)
    return instagram.post_image(image_url, caption, location_id)


def get_instagram_insights(media_id: str, metrics: list = None) -> Dict:
    """
    Standalone function to get Instagram insights

    Args:
        media_id: Instagram media ID
        metrics: List of metrics

    Returns:
        Dict with insights
    """
    logger = AuditLogger()
    business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not business_id or not access_token:
        return {
            "success": False,
            "error": "Instagram credentials not found in environment"
        }

    instagram = InstagramAPI(business_id, access_token, logger)
    return instagram.get_media_insights(media_id, metrics)


async def main():
    """Main entry point for MCP server"""
    server = SocialMediaServer()
    await server.run()


if __name__ == "__main__":
    import asyncio

    # Check if running as MCP server or standalone
    if os.getenv("MCP_MODE", "true").lower() == "true":
        asyncio.run(main())
    else:
        # Standalone test mode
        print("Running in standalone test mode...")
        print("\nExample: Post an image")
        result = post_instagram_image(
            image_url="https://example.com/image.jpg",
            caption="Test post from Social Media Server"
        )
        print(json.dumps(result, indent=2))
