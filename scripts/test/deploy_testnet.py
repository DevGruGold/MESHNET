import os
import json
from web3 import Web3
from solcx import compile_standard, install_solc

# Install solc compiler if not already installed
install_solc("0.8.0")

# Connect to Sepolia (replace with your Infura Project ID or local node)
# w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/YOUR_PROJECT_ID"))
# For local testing with Ganache/Hardhat node:
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Ensure connection is successful
if not w3.is_connected():
    print("Failed to connect to Web3 provider.")
    exit()

# Load account from private key (replace with your actual private key)
# THIS IS FOR TESTING ONLY. NEVER EXPOSE PRIVATE KEYS IN PRODUCTION CODE.
private_key = os.getenv("PRIVATE_KEY")
if not private_key:
    print("PRIVATE_KEY environment variable not set.")
    exit()

account = w3.eth.account.from_key(private_key)
w3.eth.default_account = account.address

print(f"Connected to network. Deploying from account: {account.address}")

def deploy_contract(contract_name, *args):
    print(f"\nDeploying {contract_name}...")
    with open(f"../contracts/{contract_name}.sol", "r") as f:
        contract_source_code = f.read()

    # Compile Solidity contract
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {f"{contract_name}.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    })

    bytecode = compiled_sol["contracts"][f"{contract_name}.sol"][contract_name]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"][f"{contract_name}.sol"][contract_name]["abi"]

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Get latest transaction
    nonce = w3.eth.get_transaction_count(account.address)

    # Build transaction
    transaction = Contract.constructor(*args).build_transaction({
        "chainId": w3.eth.chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": account.address,
        "nonce": nonce
    })

    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contract_address
    print(f"{contract_name} deployed to: {contract_address}")
    return w3.eth.contract(address=contract_address, abi=abi), contract_address


def main():
    # Deploy XMRT
    xmrt_contract, xmrt_address = deploy_contract("XMRT")

    # Deploy MeshMiner, passing XMRT address
    mesh_miner_contract, mesh_miner_address = deploy_contract("mesh/MeshMiner", xmrt_address)

    # Set up roles (example addresses, replace with actual Eliza, Langflow, Validator addresses)
    eliza_address = "0x742d35Cc6634C0532925a3b8D0C9e3e0C8b0e5B2"  # Example Eliza address
    langflow_address = "0x8ba1f109551bD432803012645Hac136c5c2BD754" # Example Langflow address
    validator_address = "0x9f2d04a9c2f0f6c3e8b1a5d4c7e9f2a8b5c6d3e7" # Example Validator address

    print("\nSetting up roles...")
    # Grant CEO_AI_ROLE to Eliza
    ceo_ai_role = xmrt_contract.functions.CEO_AI_ROLE().call()
    tx = xmrt_contract.functions.grantRole(ceo_ai_role, eliza_address).build_transaction({"nonce": w3.eth.get_transaction_count(account.address)})
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.rawTransaction))
    print(f"Granted CEO_AI_ROLE to Eliza: {eliza_address}")

    # Grant AUDIT_AI_ROLE to Langflow
    audit_ai_role = xmrt_contract.functions.AUDIT_AI_ROLE().call()
    tx = xmrt_contract.functions.grantRole(audit_ai_role, langflow_address).build_transaction({"nonce": w3.eth.get_transaction_count(account.address)})
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.rawTransaction))
    print(f"Granted AUDIT_AI_ROLE to Langflow: {langflow_address}")

    # Grant MESH_VALIDATOR_ROLE to Validator in XMRT
    mesh_validator_role_xmrt = xmrt_contract.functions.MESH_VALIDATOR_ROLE().call()
    tx = xmrt_contract.functions.grantRole(mesh_validator_role_xmrt, validator_address).build_transaction({"nonce": w3.eth.get_transaction_count(account.address)})
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.rawTransaction))
    print(f"Granted MESH_VALIDATOR_ROLE in XMRT to Validator: {validator_address}")

    # Grant MESH_VALIDATOR_ROLE to Validator in MeshMiner
    mesh_validator_role_meshminer = mesh_miner_contract.functions.MESH_VALIDATOR_ROLE().call()
    tx = mesh_miner_contract.functions.grantRole(mesh_validator_role_meshminer, validator_address).build_transaction({"nonce": w3.eth.get_transaction_count(account.address)})
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed_tx.rawTransaction))
    print(f"Granted MESH_VALIDATOR_ROLE in MeshMiner to Validator: {validator_address}")

    print("\nDeployment and role setup complete!")
    print(f"XMRT Address: {xmrt_address}")
    print(f"MeshMiner Address: {mesh_miner_address}")

    # Save deployment info to a JSON file
    deployment_info = {
        "XMRT_ADDRESS": xmrt_address,
        "MESH_MINER_ADDRESS": mesh_miner_address,
        "ELIZA_ADDRESS": eliza_address,
        "LANGFLOW_ADDRESS": langflow_address,
        "VALIDATOR_ADDRESS": validator_address
    }
    with open("deployment_info.json", "w") as f:
        json.dump(deployment_info, f, indent=4)
    print("Deployment info saved to deployment_info.json")

if __name__ == "__main__":
    main()


