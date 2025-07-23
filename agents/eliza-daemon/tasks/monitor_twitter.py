import tweepy
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class TwitterMonitor:
    def __init__(self):
        self.bearer_token = os.getenv("TWITTER_BEARER")
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        self.last_follower_count = 0

    async def check_new_followers(self):
        """Check for new Twitter followers"""
        try:
            # Get XMRT Twitter account info
            user = self.client.get_user(username="XMRT_io")
            current_followers = user.data.public_metrics['followers_count']

            new_followers = current_followers - self.last_follower_count
            self.last_follower_count = current_followers

            if new_followers > 0:
                logger.info(f"🐦 New followers detected: {new_followers}")
                return {
                    "new_count": new_followers,
                    "total_followers": current_followers,
                    "timestamp": "now"
                }

            return {"new_count": 0, "total_followers": current_followers}

        except Exception as e:
            logger.error(f"Twitter monitoring error: {e}")
            return {"error": str(e)}

async def check_new_followers():
    """Module function for Eliza to call"""
    monitor = TwitterMonitor()
    return await monitor.check_new_followers()
