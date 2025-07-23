"""
🔗 MESHNET Smart Contract Integration Task
Handles direct interaction with MESHNET smart contracts
"""

import logging
import asyncio
from web3 import Web3
from eth_account import Account
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MeshnetContractHandler:
    """
    🔗 MESHNET Smart Contract Integration
    Handles reward distribution, proposal creation, and blockchain interactions
    """

    def __init__(self, config: Dict):
        self.config = config
        self.setup_web3()
        self.load_contracts()

    def setup_web3(self):
        """Initialize Web3 connection"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.config['MESHNET_CONTRACTS']['RPC_URL']))
            self.validator_account = Account.from_key(
                self.config['MESHNET_CONTRACTS']['VALIDATOR_PRIVATE_KEY']
            )
            logger.info(f"🔗 Connected to blockchain: {self.w3.is_connected()}")
            logger.info(f"🔑 Validator address: {self.validator_account.address}")
        except Exception as e:
            logger.error(f"Failed to setup Web3: {e}")
            raise

    def load_contracts(self):
        """Load smart contract instances"""
        try:
            # Load contract ABIs (these would be loaded from files in practice)
            xmrt_abi = []  # Load from artifacts/contracts/XMRT.sol/XMRT.json
            miner_abi = []  # Load from artifacts/contracts/MeshMiner.sol/MeshMiner.json

            self.xmrt_contract = self.w3.eth.contract(
                address=self.config['MESHNET_CONTRACTS']['XMRT_TOKEN'],
                abi=xmrt_abi
            )

            self.miner_contract = self.w3.eth.contract(
                address=self.config['MESHNET_CONTRACTS']['MESH_MINER'],
                abi=miner_abi
            )

            logger.info("📄 Smart contracts loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load contracts: {e}")
            raise

    async def distribute_rewards(self, reward_data: List[Dict]) -> bool:
        """
        Distribute rewards to miners based on their hash contributions
        """
        try:
            logger.info(f"💰 Processing reward distribution for {len(reward_data)} miners")

            for reward in reward_data:
                miner_address = reward['address']
                reward_amount = int(reward['amount'])  # Amount in wei

                # Create transaction
                tx = self.miner_contract.functions.distributeReward(
                    miner_address,
                    reward_amount
                ).build_transaction({
                    'from': self.validator_account.address,
                    'gas': self.config['MESHNET_CONTRACTS']['GAS_LIMIT'],
                    'gasPrice': int(self.config['MESHNET_CONTRACTS']['GAS_PRICE']),
                    'nonce': self.w3.eth.get_transaction_count(self.validator_account.address)
                })

                # Sign and send transaction
                signed_tx = self.validator_account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

                logger.info(f"💸 Reward sent to {miner_address}: {reward_amount} wei, tx: {tx_hash.hex()}")

                # Wait for confirmation
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt.status == 1:
                    logger.info(f"✅ Reward distribution confirmed: {tx_hash.hex()}")
                else:
                    logger.error(f"❌ Reward distribution failed: {tx_hash.hex()}")
                    return False

                # Small delay between transactions
                await asyncio.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Failed to distribute rewards: {e}")
            return False

    async def create_dao_proposal(self, proposal_data: Dict) -> bool:
        """
        Create a DAO proposal for community voting
        """
        try:
            proposal_id = Web3.keccak(text=f"{proposal_data['title']}-{datetime.now().isoformat()}").hex()

            # Encode proposal data
            encoded_data = self.w3.eth.codec.encode(
                ['string', 'string', 'uint256'],
                [proposal_data['title'], proposal_data['description'], proposal_data.get('value', 0)]
            )

            # Create proposal transaction
            tx = self.xmrt_contract.functions.createProposal(
                bytes.fromhex(proposal_id[2:]),
                proposal_data['target'],
                proposal_data.get('value', 0),
                encoded_data
            ).build_transaction({
                'from': self.validator_account.address,
                'gas': self.config['MESHNET_CONTRACTS']['GAS_LIMIT'],
                'gasPrice': int(self.config['MESHNET_CONTRACTS']['GAS_PRICE']),
                'nonce': self.w3.eth.get_transaction_count(self.validator_account.address)
            })

            # Sign and send
            signed_tx = self.validator_account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            logger.info(f"🏛️ DAO proposal created: {proposal_id}, tx: {tx_hash.hex()}")

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.status == 1

        except Exception as e:
            logger.error(f"Failed to create DAO proposal: {e}")
            return False

    async def get_miner_stats(self) -> List[Dict]:
        """
        Get current miner statistics from the blockchain
        """
        try:
            # This would call contract methods to get miner data
            # Implementation depends on your contract structure
            miners = []

            # Example implementation
            rig_count = self.miner_contract.functions.getRigCount().call()

            for i in range(rig_count):
                rig_data = self.miner_contract.functions.getRigByIndex(i).call()
                miners.append({
                    'rig_id': rig_data[0],
                    'owner': rig_data[1],
                    'total_hashes': rig_data[2],
                    'last_submission': rig_data[3]
                })

            logger.info(f"📊 Retrieved stats for {len(miners)} miners")
            return miners

        except Exception as e:
            logger.error(f"Failed to get miner stats: {e}")
            return []
