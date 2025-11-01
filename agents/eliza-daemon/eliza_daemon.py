#!/usr/bin/env python3
"""
🦾 Eliza Daemon - Autonomous AI Agent for XMRT DAO
Main orchestration loop that runs 10-minute decision cycles
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

# Import task modules
from tasks.monitor_twitter import TwitterMonitor
from tasks.monitor_miners import MinerMonitor
from tasks.handle_rewards import RewardHandler
from tasks.governance_agent import GovernanceAgent
from tasks.notify_discord import DiscordNotifier

# Import AI brain and memory
from agent.langchain_brain import ElizaAgent
from memory.supabase_memory import SupabaseMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/eliza.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ElizaDaemon:
    """
    🦾 Main Eliza Daemon Class
    Orchestrates the autonomous agent's decision-making loop
    """

    def __init__(self, config_path='config.json'):
        self.config = self.load_config(config_path)
        self.setup_components()
        self.running = False

    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found!")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {config_path}")
            raise

    def setup_components(self):
        """Initialize all Eliza's components"""
        logger.info("🧠 Initializing Eliza's components...")

        # Initialize memory
        self.memory = SupabaseMemory(self.config)

        # Initialize AI brain
        self.brain = ElizaAgent(self.config, self.memory)

        # Initialize task modules
        self.twitter_monitor = TwitterMonitor(self.config)
        self.miner_monitor = MinerMonitor(self.config)
        self.reward_handler = RewardHandler(self.config)
        self.governance_agent = GovernanceAgent(self.config)
        self.discord_notifier = DiscordNotifier(self.config)

        logger.info("✅ All components initialized successfully")

    async def listen_phase(self):
        """
        👂 LISTEN: Gather data from all sources
        """
        logger.info("👂 LISTEN PHASE: Gathering data...")

        # Gather data from all sources concurrently
        tasks = [
            self.twitter_monitor.check_new_activity(),
            self.miner_monitor.get_current_stats(),
            self.governance_agent.check_pending_proposals(),
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            data = {
                'twitter_activity': results[0] if not isinstance(results[0], Exception) else None,
                'miner_stats': results[1] if not isinstance(results[1], Exception) else None,
                'governance_data': results[2] if not isinstance(results[2], Exception) else None,
                'timestamp': datetime.utcnow().isoformat()
            }

            logger.info(f"📊 Data gathered: {len([k for k, v in data.items() if v is not None])} sources")
            return data

        except Exception as e:
            logger.error(f"Error in listen phase: {e}")
            return {}

    async def think_phase(self, data):
        """
        🧠 THINK: AI-powered decision making
        """
        logger.info("🧠 THINK PHASE: Processing with AI...")

        try:
            # Store data in memory for context
            await self.memory.store_context("latest_data", data)

            # Get AI decisions
            decisions = await self.brain.make_decisions(data)

            logger.info(f"🎯 AI Decisions made: {len(decisions)} actions planned")
            return decisions

        except Exception as e:
            logger.error(f"Error in think phase: {e}")
            return {}

    async def act_phase(self, decisions):
        """
        🎬 ACT: Execute decisions
        """
        logger.info("🎬 ACT PHASE: Executing decisions...")

        actions_taken = []

        try:
            # Execute different types of actions
            if 'rewards' in decisions:
                reward_results = await self.reward_handler.distribute_rewards(decisions['rewards'])
                actions_taken.extend(reward_results)

            if 'tweets' in decisions:
                tweet_results = await self.twitter_monitor.send_tweets(decisions['tweets'])
                actions_taken.extend(tweet_results)

            if 'proposals' in decisions:
                proposal_results = await self.governance_agent.create_proposals(decisions['proposals'])
                actions_taken.extend(proposal_results)

            if 'notifications' in decisions:
                notification_results = await self.discord_notifier.send_notifications(decisions['notifications'])
                actions_taken.extend(notification_results)

            # Log all actions taken
            for action in actions_taken:
                logger.info(f"✅ Action executed: {action}")

            # Notify Discord of cycle completion
            await self.discord_notifier.send_cycle_summary(len(actions_taken))

            return actions_taken

        except Exception as e:
            logger.error(f"Error in act phase: {e}")
            return []

    async def sleep_phase(self, cycle_data):
        """
        💤 SLEEP: Log cycle and wait
        """
        cycle_summary = {
            'cycle_completed_at': datetime.utcnow().isoformat(),
            'data_sources': len([k for k, v in cycle_data.get('listen_data', {}).items() if v]),
            'decisions_made': len(cycle_data.get('decisions', {})),
            'actions_taken': len(cycle_data.get('actions', []))
        }

        # Store cycle summary in memory
        await self.memory.store_cycle_summary(cycle_summary)

        logger.info(f"💤 SLEEP PHASE: Cycle complete. Next cycle in 10 minutes...")
        logger.info(f"📊 Cycle Summary: {cycle_summary}")

        # Sleep for 10 minutes (600 seconds)
        await asyncio.sleep(600)

    async def autonomous_loop(self):
        """
        🔄 Main autonomous decision loop
        Listen → Think → Act → Sleep
        """
        logger.info("🦾 Eliza Daemon starting autonomous operation!")

        cycle_count = 0
        self.running = True

        while self.running:
            try:
                cycle_count += 1
                logger.info(f"🔄 Starting Cycle #{cycle_count}")

                # LISTEN: Gather data
                listen_data = await self.listen_phase()

                # THINK: AI decision making
                decisions = await self.think_phase(listen_data)

                # ACT: Execute decisions
                actions = await self.act_phase(decisions)

                # Prepare cycle data for sleep phase
                cycle_data = {
                    'listen_data': listen_data,
                    'decisions': decisions,
                    'actions': actions
                }

                # SLEEP: Log and wait
                await self.sleep_phase(cycle_data)

            except KeyboardInterrupt:
                logger.info("🛑 Shutdown signal received")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(60)  # Short sleep before retry

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Eliza Daemon shutting down...")
        self.running = False

async def main():
    """Main entry point"""
    eliza = ElizaDaemon()

    try:
        await eliza.autonomous_loop()
    except KeyboardInterrupt:
        eliza.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        eliza.shutdown()

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)

    # Run Eliza
    asyncio.run(main())
