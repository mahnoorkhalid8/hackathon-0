"""
CEO Briefing Generator for Instagram Business
Generates weekly executive reports with analytics and system health
"""

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("../.env")

from social_media_server import InstagramAPI, AuditLogger
from instagram_auth import InstagramAuth


class CEOBriefingGenerator:
    """Generates executive briefings for Instagram Business performance"""

    # Marketing costs
    COST_PER_POST = 5.00  # $5 per post

    def __init__(self):
        self.logger = AuditLogger("logs/ceo_briefing_logs.json")

        # Load credentials
        self.business_id = os.getenv("INSTAGRAM_BUSINESS_ID")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.token_expires = os.getenv("IG_TOKEN_EXPIRES_AT")

        if not self.business_id or not self.access_token:
            raise ValueError("Instagram credentials not found in environment")

        self.instagram = InstagramAPI(self.business_id, self.access_token, self.logger)

    def fetch_recent_media(self, days: int = 7) -> List[Dict]:
        """
        Fetch media from the last N days

        Args:
            days: Number of days to look back

        Returns:
            List of media items with metadata
        """
        import requests

        url = f"{self.instagram.GRAPH_API_BASE}/{self.business_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
            "access_token": self.access_token,
            "limit": 100  # Get up to 100 recent posts
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                all_media = response_data.get("data", [])

                # Filter by date
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                recent_media = []

                for media in all_media:
                    timestamp_str = media.get("timestamp")
                    if timestamp_str:
                        media_date = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        if media_date >= cutoff_date:
                            recent_media.append(media)

                self.logger.log(
                    "fetch_recent_media",
                    {"days": days, "business_id": self.business_id},
                    {"status_code": 200, "total_media": len(all_media), "recent_media": len(recent_media)},
                    "success"
                )

                return recent_media
            else:
                error_message = response_data.get("error", {}).get("message", "Failed to fetch media")
                self.logger.log(
                    "fetch_recent_media",
                    {"days": days},
                    response_data,
                    "error"
                )
                return []

        except Exception as e:
            self.logger.log(
                "fetch_recent_media",
                {"days": days},
                {"error": str(e)},
                "error"
            )
            return []

    def get_media_insights(self, media_id: str) -> Dict:
        """
        Get insights for a specific media item

        Args:
            media_id: Instagram media ID

        Returns:
            Dict with insights data
        """
        result = self.instagram.get_media_insights(
            media_id,
            metrics=["engagement", "impressions", "reach", "saved"]
        )

        if result.get("success"):
            # Convert insights array to dict
            insights_dict = {}
            for insight in result.get("insights", []):
                name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    insights_dict[name] = values[0].get("value", 0)
            return insights_dict
        else:
            return {}

    def check_system_health(self) -> Dict:
        """
        Check system health status

        Returns:
            Dict with health status
        """
        health = {
            "status": "healthy",
            "issues": [],
            "warnings": []
        }

        # Check token expiration
        if self.token_expires:
            is_expired = InstagramAuth.is_token_expired(self.token_expires, buffer_days=7)
            days_until_expiry = InstagramAuth.is_token_expired(self.token_expires, buffer_days=0)

            if is_expired:
                health["status"] = "warning"
                health["warnings"].append({
                    "type": "token_expiring_soon",
                    "message": f"Access token expires on {self.token_expires}",
                    "action": "Run: python cli.py refresh"
                })

            if days_until_expiry:
                health["status"] = "critical"
                health["issues"].append({
                    "type": "token_expired",
                    "message": f"Access token expired on {self.token_expires}",
                    "action": "URGENT: Run: python cli.py refresh"
                })

        # Check for recent critical errors
        ceo_log_path = Path("../logs/ceo_briefing.json")
        if ceo_log_path.exists():
            try:
                logs = json.loads(ceo_log_path.read_text())
                # Check for critical errors in last 7 days
                cutoff = datetime.now(timezone.utc) - timedelta(days=7)
                recent_critical = [
                    log for log in logs
                    if datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")) >= cutoff
                    and log.get("severity") == "CRITICAL"
                ]

                if recent_critical:
                    health["status"] = "critical" if health["status"] != "critical" else "critical"
                    for error in recent_critical[:3]:  # Show top 3
                        health["issues"].append({
                            "type": error.get("error_type", "unknown"),
                            "message": error.get("error_message", "Unknown error"),
                            "action": error.get("context", {}).get("action_required", "Review logs")
                        })
            except Exception:
                pass

        return health

    def calculate_metrics(self, media_list: List[Dict]) -> Dict:
        """
        Calculate aggregate metrics

        Args:
            media_list: List of media items with insights

        Returns:
            Dict with calculated metrics
        """
        total_posts = len(media_list)
        total_impressions = sum(m.get("insights", {}).get("impressions", 0) for m in media_list)
        total_reach = sum(m.get("insights", {}).get("reach", 0) for m in media_list)
        total_engagement = sum(m.get("insights", {}).get("engagement", 0) for m in media_list)
        total_saved = sum(m.get("insights", {}).get("saved", 0) for m in media_list)

        # Calculate costs
        total_cost = total_posts * self.COST_PER_POST

        # Calculate cost per engagement
        cost_per_engagement = total_cost / total_engagement if total_engagement > 0 else 0

        # Calculate engagement rate
        engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0

        return {
            "total_posts": total_posts,
            "total_impressions": total_impressions,
            "total_reach": total_reach,
            "total_engagement": total_engagement,
            "total_saved": total_saved,
            "total_cost": total_cost,
            "cost_per_engagement": cost_per_engagement,
            "engagement_rate": engagement_rate,
            "avg_impressions_per_post": total_impressions / total_posts if total_posts > 0 else 0,
            "avg_engagement_per_post": total_engagement / total_posts if total_posts > 0 else 0
        }

    def find_top_post(self, media_list: List[Dict]) -> Optional[Dict]:
        """
        Find the top performing post by engagement

        Args:
            media_list: List of media items with insights

        Returns:
            Top performing post or None
        """
        if not media_list:
            return None

        return max(
            media_list,
            key=lambda m: m.get("insights", {}).get("engagement", 0)
        )

    def generate_markdown_report(self, days: int = 7) -> str:
        """
        Generate CEO briefing in Markdown format

        Args:
            days: Number of days to analyze

        Returns:
            Markdown formatted report
        """
        # Fetch data
        print(f"Fetching Instagram media from last {days} days...")
        media_list = self.fetch_recent_media(days)

        # Get insights for each post
        print(f"Fetching insights for {len(media_list)} posts...")
        for media in media_list:
            media["insights"] = self.get_media_insights(media["id"])

        # Calculate metrics
        metrics = self.calculate_metrics(media_list)

        # Find top post
        top_post = self.find_top_post(media_list)

        # Check system health
        health = self.check_system_health()

        # Generate report
        report_date = datetime.now().strftime("%B %d, %Y")
        date_range = f"{(datetime.now() - timedelta(days=days)).strftime('%b %d')} - {datetime.now().strftime('%b %d, %Y')}"

        report = f"""# Instagram Business - CEO Briefing
**Report Date:** {report_date}
**Period:** {date_range} ({days} days)

---

## 📊 Executive Summary

"""

        # System Health Section
        if health["status"] == "critical":
            report += "### 🚨 CRITICAL SYSTEM ISSUES\n\n"
            for issue in health["issues"]:
                report += f"- **{issue['type']}**: {issue['message']}\n"
                report += f"  - Action Required: `{issue['action']}`\n\n"
        elif health["status"] == "warning":
            report += "### ⚠️ System Warnings\n\n"
            for warning in health["warnings"]:
                report += f"- **{warning['type']}**: {warning['message']}\n"
                report += f"  - Recommended Action: `{warning['action']}`\n\n"
        else:
            report += "### ✅ System Status: Healthy\n\n"

        report += "---\n\n"

        # Performance Metrics
        report += "## 📈 Performance Metrics\n\n"
        report += "| Metric | Value |\n"
        report += "|--------|-------|\n"
        report += f"| **Total Posts** | {metrics['total_posts']} |\n"
        report += f"| **Total Impressions** | {metrics['total_impressions']:,} |\n"
        report += f"| **Total Reach** | {metrics['total_reach']:,} |\n"
        report += f"| **Total Engagement** | {metrics['total_engagement']:,} |\n"
        report += f"| **Engagement Rate** | {metrics['engagement_rate']:.2f}% |\n"
        report += f"| **Total Saved** | {metrics['total_saved']:,} |\n\n"

        # Financial Metrics
        report += "## 💰 Marketing Investment\n\n"
        report += "| Metric | Value |\n"
        report += "|--------|-------|\n"
        report += f"| **Cost per Post** | ${self.COST_PER_POST:.2f} |\n"
        report += f"| **Total Marketing Cost** | ${metrics['total_cost']:.2f} |\n"
        report += f"| **Cost per Engagement** | ${metrics['cost_per_engagement']:.4f} |\n"

        # Handle division by zero for cost per 1K impressions
        if metrics['total_impressions'] > 0:
            cost_per_1k = (metrics['total_cost'] / (metrics['total_impressions'] / 1000))
            report += f"| **Cost per 1K Impressions** | ${cost_per_1k:.2f} |\n\n"
        else:
            report += f"| **Cost per 1K Impressions** | N/A |\n\n"

        # Top Performing Post
        if top_post:
            report += "## 🏆 Top Performing Post\n\n"

            caption = top_post.get("caption", "No caption")
            caption_preview = caption[:100] + "..." if len(caption) > 100 else caption

            engagement = top_post.get("insights", {}).get("engagement", 0)
            impressions = top_post.get("insights", {}).get("impressions", 0)
            reach = top_post.get("insights", {}).get("reach", 0)
            saved = top_post.get("insights", {}).get("saved", 0)

            report += f"**Caption:** {caption_preview}\n\n"
            report += f"**Posted:** {top_post.get('timestamp', 'Unknown')}\n\n"
            report += f"**Link:** {top_post.get('permalink', 'N/A')}\n\n"
            report += "**Performance:**\n"
            report += f"- Engagement: {engagement:,}\n"
            report += f"- Impressions: {impressions:,}\n"
            report += f"- Reach: {reach:,}\n"
            report += f"- Saved: {saved:,}\n"
            report += f"- Engagement Rate: {(engagement / impressions * 100):.2f}%\n\n"

        # Recent Posts Summary
        if media_list:
            report += "## 📝 Recent Posts Summary\n\n"
            report += "| Date | Caption | Engagement | Impressions | Reach |\n"
            report += "|------|---------|------------|-------------|-------|\n"

            for media in sorted(media_list, key=lambda m: m.get("timestamp", ""), reverse=True)[:10]:
                date = datetime.fromisoformat(media.get("timestamp", "").replace("Z", "+00:00")).strftime("%b %d")
                caption = media.get("caption", "No caption")[:30] + "..."
                engagement = media.get("insights", {}).get("engagement", 0)
                impressions = media.get("insights", {}).get("impressions", 0)
                reach = media.get("insights", {}).get("reach", 0)

                report += f"| {date} | {caption} | {engagement:,} | {impressions:,} | {reach:,} |\n"

            report += "\n"

        # Recommendations
        report += "## 💡 Recommendations\n\n"

        if metrics['total_posts'] == 0:
            report += f"- **No posts in the last {days} days** - Consider increasing posting frequency\n"
            report += "- **Start posting regularly** - Aim for 3-5 posts per week for optimal engagement\n"
        elif metrics['total_posts'] < 3:
            report += f"- **Low posting frequency** ({metrics['total_posts']} posts in {days} days) - Aim for 3-5 posts per week\n"

        if metrics['engagement_rate'] < 2.0:
            report += f"- **Low engagement rate** ({metrics['engagement_rate']:.2f}%) - Industry average is 2-3%\n"
            report += "  - Consider: More engaging captions, better hashtags, optimal posting times\n"

        if metrics['cost_per_engagement'] > 0.10:
            report += f"- **High cost per engagement** (${metrics['cost_per_engagement']:.4f}) - Optimize content strategy\n"

        if top_post:
            report += f"- **Replicate success** - Analyze what made the top post successful and create similar content\n"

        report += "\n---\n\n"
        report += f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        report += f"*Powered by Instagram Business Automation System*\n"

        return report

    def save_report(self, report: str, filename: Optional[str] = None) -> Path:
        """
        Save report to file

        Args:
            report: Markdown report content
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        if not filename:
            filename = f"ceo_briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        report_path = reports_dir / filename
        report_path.write_text(report, encoding='utf-8')

        return report_path


def generate_ceo_briefing(days: int = 7, save: bool = True) -> Dict:
    """
    MCP tool function: Generate CEO briefing

    Args:
        days: Number of days to analyze
        save: Whether to save report to file

    Returns:
        Dict with report content and metadata
    """
    try:
        generator = CEOBriefingGenerator()
        report = generator.generate_markdown_report(days)

        result = {
            "success": True,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }

        if save:
            report_path = generator.save_report(report)
            result["saved_to"] = str(report_path)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import sys

    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Parse arguments
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days argument: {sys.argv[1]}")
            sys.exit(1)

    print(f"Generating CEO Briefing for last {days} days...")
    print("="*60)

    result = generate_ceo_briefing(days=days, save=True)

    if result["success"]:
        print("\n" + result["report"])
        print("\n" + "="*60)
        print(f"✓ Report saved to: {result.get('saved_to', 'N/A')}")
    else:
        print(f"✗ Error generating report: {result['error']}")
        sys.exit(1)
