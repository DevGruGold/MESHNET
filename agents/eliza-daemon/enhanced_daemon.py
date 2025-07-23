#!/usr/bin/env python3
"""
🚀 Enhanced Eliza Daemon for MESHNET Integration
Production-ready autonomous agent with MESHNET smart contract integration
"""

import asyncio
import logging
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Import enhanced modules
from eliza_daemon import ElizaDaemon
from tasks.meshnet_contracts import MeshnetContractHandler

# Setup enhanced logging
def setup_logging():
    """Setup comprehensive logging system"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Main log file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/eliza_daemon_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Enhanced Eliza Daemon starting up...")
    return logger

class EnhancedElizaDaemon(ElizaDaemon):
    """
    Enhanced Eliza Daemon with MESHNET integration
    """

    def __init__(self, config_path='config.meshnet.json'):
        super().__init__(config_path)
        self.setup_meshnet_integration()

    def setup_meshnet_integration(self):
        """Initialize MESHNET smart contract integration"""
        try:
            self.meshnet_handler = MeshnetContractHandler(self.config)
            self.logger.info("🔗 MESHNET smart contract integration initialized")
        except Exception as e:
            self.logger.error(f"Failed to setup MESHNET integration: {e}")
            raise

    async def enhanced_decision_loop(self):
        """
        Enhanced decision loop with MESHNET-specific operations
        """
        while True:
            try:
                self.logger.info("🔄 Starting enhanced decision cycle...")

                # 1. Standard monitoring (from base daemon)
                await self.run_monitoring_cycle()

                # 2. MESHNET-specific operations
                await self.handle_meshnet_operations()

                # 3. AI-powered decision making
                await self.make_autonomous_decisions()

                # 4. Execute actions
                await self.execute_pending_actions()

                self.logger.info("✅ Decision cycle completed successfully")

                # Wait for next cycle
                await asyncio.sleep(self.config.get('DAEMON_CONFIG', {}).get('LOOP_INTERVAL_MINUTES', 10) * 60)

            except Exception as e:
                self.logger.error(f"Error in decision loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def handle_meshnet_operations(self):
        """Handle MESHNET-specific blockchain operations"""
        try:
            # Get current miner stats from blockchain
            miner_stats = await self.meshnet_handler.get_miner_stats()

            # Store in memory for AI analysis
            await self.memory_store.store_data('miner_stats', {
                'timestamp': datetime.now().isoformat(),
                'stats': miner_stats
            })

            self.logger.info(f"📊 Updated miner stats for {len(miner_stats)} rigs")

        except Exception as e:
            self.logger.error(f"Error in MESHNET operations: {e}")

    async def execute_reward_distribution(self, reward_data):
        """Execute blockchain reward distribution"""
        try:
            self.logger.info(f"💰 Executing reward distribution for {len(reward_data)} miners")

            success = await self.meshnet_handler.distribute_rewards(reward_data)

            if success:
                # Log successful distribution
                await self.memory_store.store_data('reward_distribution', {
                    'timestamp': datetime.now().isoformat(),
                    'rewards': reward_data,
                    'status': 'success'
                })

                # Notify Discord
                await self.discord_notifier.send_reward_notification(reward_data)

                self.logger.info("✅ Reward distribution completed successfully")
                return True
            else:
                self.logger.error("❌ Reward distribution failed")
                return False

        except Exception as e:
            self.logger.error(f"Error executing reward distribution: {e}")
            return False

    async def create_autonomous_proposal(self, proposal_data):
        """Create DAO proposal based on AI analysis"""
        try:
            self.logger.info(f"🏛️ Creating autonomous DAO proposal: {proposal_data['title']}")

            success = await self.meshnet_handler.create_dao_proposal(proposal_data)

            if success:
                # Store proposal in memory
                await self.memory_store.store_data('dao_proposals', {
                    'timestamp': datetime.now().isoformat(),
                    'proposal': proposal_data,
                    'status': 'created'
                })

                # Notify community
                await self.discord_notifier.send_proposal_notification(proposal_data)

                self.logger.info("✅ DAO proposal created successfully")
                return True
            else:
                self.logger.error("❌ DAO proposal creation failed")
                return False

        except Exception as e:
            self.logger.error(f"Error creating DAO proposal: {e}")
            return False

async def main():
    """Main entry point for enhanced daemon"""
    logger = setup_logging()

    try:
        # Check for config file
        config_path = 'config.meshnet.json'
        if not os.path.exists(config_path):
            logger.error(f"Configuration file {config_path} not found!")
            logger.info("Please copy config.meshnet.json from config.json.template and configure it")
            return

        # Initialize enhanced daemon
        logger.info("🚀 Initializing Enhanced Eliza Daemon...")
        daemon = EnhancedElizaDaemon(config_path)

        # Start autonomous operation
        logger.info("🤖 Starting autonomous decision loop...")
        await daemon.enhanced_decision_loop()

    except KeyboardInterrupt:
        logger.info("🛑 Daemon stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
