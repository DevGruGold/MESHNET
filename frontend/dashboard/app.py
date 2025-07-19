import streamlit as st
from web3 import Web3
from streamlit_wallet_connect import st_wallet_connect

# Corporate Styling (as before)
st.markdown("""
<style>
    body { background-color: #f4f9fd; color: #333; font-family: 'Arial', sans-serif; }
    h1 { color: #006699; text-align: center; }
    .stButton > button { background-color: #006699; color: white; width: 100%; height: 50px; font-size: 18px; border-radius: 5px; }
    .stExpander { background-color: #e6f2ff; border-radius: 5px; }
    .row { display: flex; flex-wrap: wrap; } .col { flex: 1; min-width: 200px; padding: 10px; }
    @media (max-width: 768px) { .row { flex-direction: column; } }
    .metric { box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 10px; border-radius: 5px; background: white; }
</style>
""", unsafe_allow_html=True)

st.title("MESHNET Dashboard")
st.subheader("Powered by XMRT Ecosystem – Decentralized AI-Meshed Future")

# Web3 Setup (Sepolia Testnet)
w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/c843a693bc5d43d1aee471d2491f2414"))  # Use prompted key
xmrt_contract = "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
ipnft_contract = "0x9de91fc136a846d7442d1321a2d1b6aaef494eda"

# Wallet Connect Button
wallet = st_wallet_connect(project_id="3c0e28ee15f49b20eebc46f23df5aa8e", chain="ethereum:11155111")  # Sepolia chain ID
if wallet:
    st.write(f"Connected Wallet: {wallet['address']}")

# Tabs with Full Integration
tab1, tab2, tab3 = st.tabs(["Core Features", "AI & Agents", "Web3 Testing"])

with tab1:
    # Placeholder: Add your core features here
    st.write("Core features coming soon!")

with tab2:
    # Placeholder: Add your AI features here
    st.write("AI features coming soon!")

with tab3:
    st.subheader("Web3 Testing Environment")
    st.write("Interact with XMRT on Sepolia Testnet!")

    # XMRT Coin Integration
    st.markdown("#### XMRT Coin (Sepolia)")
    test_wallet_address = st.text_input("Test Wallet Address (for balance checks):")
    if st.button("Check Balance"):
        balance = w3.eth.get_balance(test_wallet_address) if test_wallet_address else 0
        st.metric("Balance", w3.from_wei(balance, 'ether'), "ETH")
    if st.button("Simulate Transfer"):
        st.success("Simulated XMRT transfer on testnet!")

    # IP-NFT Integration
    st.markdown("#### IP-NFT")
    if st.button("View NFT"):
        st.write("NFT Metadata: Simulated IP rights token.")
    if st.button("Simulate Mint"):
        st.success("NFT minted on testnet (simulation)!")

st.markdown("---")
st.write("**Join XMRT DAO:** Invest in decentralized meshes. [Contact](mailto:joseph@xmrt.io)")


st.markdown("---")
st.write("**Join XMRT DAO:** Invest in decentralized meshes. [Contact](mailto:joseph@xmrt.io)")
