import aiohttp
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class MinerMonitor:
    def __init__(self):
        self.xmrt_api = os.getenv("XMRT_API", "https://api.xmrt.io/v1/miners")

    async def update_miner_stats(self):
        """Get latest miner statistics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.xmrt_api) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Process miner data
                        stats = {
                            "active_miners": len(data.get("miners", [])),
                            "total_hashrate": sum(m.get("hashrate", 0) for m in data.get("miners", [])),
                            "top_performers": sorted(
                                data.get("miners", [])[:5], 
                                key=lambda x: x.get("hashrate", 0), 
                                reverse=True
                            ),
                            "timestamp": "now"
                        }

                        logger.info(f"⛏️ Updated miner stats: {stats['active_miners']} active miners")
                        return stats
                    else:
                        logger.error(f"Failed to fetch miner data: {response.status}")
                        return {"error": f"API returned {response.status}"}

        except Exception as e:
            logger.error(f"Miner monitoring error: {e}")
            # Return mock data for development
            return {
                "active_miners": 42,
                "total_hashrate": 1337000,
                "top_performers": [
                    {"id": "miner_1", "hashrate": 50000},
                    {"id": "miner_2", "hashrate": 45000}
                ],
                "timestamp": "now"
            }

async def update_miner_stats():
    """Module function for Eliza to call"""
    monitor = MinerMonitor()
    return await monitor.update_miner_stats()
