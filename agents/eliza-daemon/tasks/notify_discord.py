import aiohttp
import os
from dotenv import load_dotenv
import logging
from typing import Union, List

load_dotenv()
logger = logging.getLogger(__name__)

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK")

    async def send_notification(self, messages: Union[str, List[str]]):
        """Send notifications to Discord"""
        if not self.webhook_url:
            logger.warning("Discord webhook not configured")
            return

        try:
            # Handle both single messages and lists
            if isinstance(messages, str):
                messages = [messages]

            for message in messages:
                await self._send_webhook(message)
                logger.info(f"📢 Discord notification sent: {message[:50]}...")

        except Exception as e:
            logger.error(f"Discord notification error: {e}")

    async def _send_webhook(self, message: str):
        """Send a single message via webhook"""
        payload = {
            "content": f"🦾 **Eliza Daemon**: {message}",
            "username": "Eliza",
            "avatar_url": "https://example.com/eliza-avatar.png"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status != 204:
                    logger.error(f"Discord webhook failed: {response.status}")

async def send_notification(messages: Union[str, List[str]]):
    """Module function for Eliza to call"""
    notifier = DiscordNotifier()
    return await notifier.send_notification(messages)
