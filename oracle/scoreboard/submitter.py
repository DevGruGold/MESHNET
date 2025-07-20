#!/usr/bin/env python3
"""
Meshnet Oracle Submitter
Parses meshnet_scoreboard.json, signs data, and submits proofs to MeshMiner.sol
"""

import json
import time
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OracleSubmitter:
    def __init__(self, web3_provider="https://sepolia.infura.io/v3/YOUR_PROJECT_ID"):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        
        # Oracle Node private key (should be loaded from secure storage)
        self.private_key = None  # Load from environment or secure storage
        self.oracle_account = None
        
        if self.private_key:
            self.oracle_account = Account.from_key(self.private_key)
            logger.info(f"Oracle account loaded: {self.oracle_account.address}")
        else:
            logger.warning("Oracle private key not set. Submitter will not be able to sign transactions.")

        # Contract addresses and ABIs (to be set during deployment)
        self.mesh_miner_address = None
        self.mesh_miner_abi = None # Load MeshMiner ABI here
        self.mesh_miner_contract = None

    def load_scoreboard_data(self, scoreboard_path="meshnet_scoreboard.json"):
        """Load and parse meshnet scoreboard data"""
        try:
            with open(scoreboard_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Scoreboard file not found at {scoreboard_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {scoreboard_path}")
            return None

    def sign_proof_data(self, rig_id, hashes):
        """Sign the proof data with the Oracle Node's private key"""
        if not self.oracle_account:
            logger.error("Oracle account not initialized. Cannot sign data.")
            return None

        message = f"rigId:{rig_id},hashes:{hashes}"
        encoded_message = encode_defunct(text=message)
        signed_message = self.w3.eth.account.sign_message(encoded_message, private_key=self.private_key)
        return signed_message.signature.hex()

    def submit_proof_to_contract(self, rig_id, hashes, signature):
        """Submit proof to MeshMiner.sol via submitProof()"""
        if not self.mesh_miner_contract:
            logger.error("MeshMiner contract not initialized.")
            return
        if not self.oracle_account:
            logger.error("Oracle account not initialized. Cannot send transaction.")
            return

        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.oracle_account.address)
            tx = self.mesh_miner_contract.functions.submitProof(
                rig_id,
                hashes,
                bytes.fromhex(signature[2:]) # Remove '0x' prefix and convert to bytes
            ).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': 2000000, # Estimate gas or set a reasonable limit
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'from': self.oracle_account.address
            })

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            logger.info(f"Proof submission transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Error submitting proof to contract: {e}")
            return None

    def run_submitter(self, scoreboard_path="meshnet_scoreboard.json"):
        """Main submitter logic"""
        scoreboard_data = self.load_scoreboard_data(scoreboard_path)
        if not scoreboard_data:
            return

        for rig_data in scoreboard_data.get("rigs", []):
            rig_id = rig_data.get("rig_id")
            hashes = rig_data.get("hash_count")

            if rig_id and hashes is not None:
                signature = self.sign_proof_data(rig_id, hashes)
                if signature:
                    logger.info(f"Submitting proof for rig {rig_id} with {hashes} hashes...")
                    self.submit_proof_to_contract(bytes.fromhex(rig_id[2:]), hashes, signature) # Convert rig_id to bytes
                else:
                    logger.warning(f"Could not sign proof for rig {rig_id}")
            else:
                logger.warning(f"Skipping malformed rig data: {rig_data}")

if __name__ == "__main__":
    # Example usage (replace with actual contract addresses and private keys)
    submitter = OracleSubmitter()
    # submitter.private_key = "YOUR_ORACLE_PRIVATE_KEY"
    # submitter.mesh_miner_address = "YOUR_MESH_MINER_CONTRACT_ADDRESS"
    # submitter.mesh_miner_abi = [...] # Your MeshMiner ABI
    
    # if submitter.mesh_miner_address and submitter.mesh_miner_abi:
    #     submitter.mesh_miner_contract = submitter.w3.eth.contract(
    #         address=submitter.mesh_miner_address, abi=submitter.mesh_miner_abi
    #     )

    # Create a dummy scoreboard file for testing
    dummy_scoreboard_data = {
        "rigs": [
            {"rig_id": "0x" + "a"*64, "hash_count": 100000},
            {"rig_id": "0x" + "b"*64, "hash_count": 150000}
        ]
    }
    with open("/home/ubuntu/MESHNET/oracle/scoreboard/meshnet_scoreboard.json", "w") as f:
        json.dump(dummy_scoreboard_data, f, indent=2)

    submitter.run_submitter(scoreboard_path="/home/ubuntu/MESHNET/oracle/scoreboard/meshnet_scoreboard.json")


