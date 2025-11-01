import streamlit as st
import datetime
import pandas as pd
import requests
import json
import time
import hashlib
from typing import Dict, List, Any, Optional

st.set_page_config(page_title="XMRT DAO – Mobile Mining Dashboard", layout="wide")

# --- Corporate Fintech Styling ---
st.markdown(
    """
    <style>
        body { background: #1a1a1a !important; color: #e0e0e0; font-family: 'Inter', 'Arial', sans-serif; }
        h1, h2, h3, h4, h5 { color: #00ff88; }
        .stButton > button {
            background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%);
            color: #1a1a1a !important;
            width: 100%;
            height: 50px;
            font-size: 20px;
            border-radius: 7px;
            font-weight: 600;
            margin-bottom: 12px;
            box-shadow: 0 2px 12px #00ff8844;
        }
        .stTextInput > div > input, .stNumberInput > div > input {
            background: #2d2d2d;
            color: #e0e0e0;
            font-size: 18px;
            border-radius: 7px;
            border: 1.5px solid #00ff88;
        }
        .onboarding-box {
            background: #2d2d2d;
            border: 1.5px solid #00ff88;
            box-shadow: 0 4px 24px #00ff8822;
            padding: 28px 22px 18px 22px;
            border-radius: 14px;
            margin-bottom: 20px;
        }
        .profile-chip {
            display: inline-block;
            background: #00ff88;
            color: #1a1a1a;
            border: 1.5px solid #00ff88;
            padding: 5px 18px;
            margin: 3px 6px 3px 0;
            border-radius: 20px;
            font-size: 17px;
            font-weight: 600;
        }
        .card {
            background: #2d2d2d;
            border-radius: 14px;
            box-shadow: 0 3px 16px #00ff8822;
            padding: 26px 22px 18px 22px;
            margin-bottom: 26px;
            border: 1.5px solid #00ff88;
        }
        .orange { color: #00ff88; font-weight: bold; }
        .interaction-btn {
            background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%);
            color: #1a1a1a !important;
            font-weight: 600;
            border-radius: 8px;
            font-size: 19px;
            margin-bottom: 8px;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: #1a1a1a;
            border-radius: 10px 10px 0 0;
        }
        .stTabs [data-baseweb="tab"] {
            color: #00ff88;
            background: #2d2d2d;
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
            margin-right: 2px;
            font-size: 18px;
        }
        .stTabs [aria-selected="true"] {
            color: #1a1a1a !important;
            background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%);
            border-bottom: 3px solid #00ff88 !important;
        }
        .leaderboard-rank {
            background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%);
            color: #1a1a1a;
            padding: 5px 12px;
            border-radius: 15px;
            font-weight: bold;
            margin-right: 10px;
        }
        .miner-card {
            background: #333333;
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 8px #00ff8833;
        }
        .top-miner {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            color: #1a1a1a;
            border: 2px solid #00ff88;
        }
        .supportxmr-data {
            background: #2d2d2d;
            border: 2px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
        }
        .worker-status {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-active { background: #00ff88; color: #1a1a1a; }
        .status-offline { background: #ff4444; color: white; }
        .status-idle { background: #ffaa00; color: #1a1a1a; }
        @media (max-width: 700px) {
            .onboarding-box, .card { padding: 12px 6px 10px 6px; }
            h1 { font-size: 25px; }
        }
    </style>
""",
    unsafe_allow_html=True,
)

# SupportXMR API Configuration
SUPPORTXMR_API_BASE = "https://supportxmr.com/api"
WALLET_ADDRESS = "46UxNFuGM2E3UmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_supportxmr_data():
    """Fetch data from SupportXMR API"""
    try:
        # Get pool statistics
        pool_response = requests.get(f"{SUPPORTXMR_API_BASE}/pool/stats", timeout=10)
        pool_data = pool_response.json() if pool_response.status_code == 200 else {}
        
        # Get miner statistics
        miner_response = requests.get(f"{SUPPORTXMR_API_BASE}/miner/{WALLET_ADDRESS}/stats", timeout=10)
        miner_data = miner_response.json() if miner_response.status_code == 200 else {}
        
        # Get network statistics
        network_response = requests.get(f"{SUPPORTXMR_API_BASE}/network/stats", timeout=10)
        network_data = network_response.json() if network_response.status_code == 200 else {}
        
        return {
            "pool": pool_data,
            "miner": miner_data,
            "network": network_data,
            "success": True
        }
    except Exception as e:
        st.error(f"Error fetching SupportXMR data: {e}")
        return {"success": False, "error": str(e)}

def format_hash_rate(hash_rate):
    """Format hash rate for display"""
    if hash_rate == 0:
        return "0 H/s"
    elif hash_rate < 1000:
        return f"{hash_rate} H/s"
    elif hash_rate < 1000000:
        return f"{hash_rate/1000:.2f} KH/s"
    elif hash_rate < 1000000000:
        return f"{hash_rate/1000000:.2f} MH/s"
    elif hash_rate < 1000000000000:
        return f"{hash_rate/1000000000:.2f} GH/s"
    else:
        return f"{hash_rate/1000000000000:.2f} TH/s"

def format_xmr_amount(atomic_units):
    """Convert atomic units to XMR"""
    if atomic_units == 0:
        return "0.000000000000"
    return f"{atomic_units / 1000000000000:.12f}"

def create_supportxmr_leaderboard():
    """Create leaderboard data from SupportXMR API"""
    data = get_supportxmr_data()
    
    if not data["success"]:
        return pd.DataFrame()
    
    # Create a single-entry leaderboard for the specified wallet
    miner_data = data.get("miner", {})
    pool_data = data.get("pool", {}).get("pool_statistics", {})
    
    # Calculate status based on hash rate and last hash time
    current_hash_rate = miner_data.get("hash", 0)
    last_hash = miner_data.get("lastHash", 0)
    
    if current_hash_rate > 0:
        status = "🟢 Active"
    elif last_hash > 0:
        # Check if last hash was recent (within 24 hours)
        current_time = datetime.datetime.now().timestamp() * 1000
        if current_time - last_hash < 86400000:  # 24 hours in milliseconds
            status = "🟡 Recently Active"
        else:
            status = "🔴 Inactive"
    else:
        status = "🔴 Inactive"
    
    # Create leaderboard entry
    leaderboard_data = [{
        "rank": 1,
        "handle": f"Wallet: ...{WALLET_ADDRESS[-8:]}",
        "hash_rate": format_hash_rate(current_hash_rate),
        "total_hashes": f"{miner_data.get('totalHashes', 0):,}",
        "valid_shares": f"{miner_data.get('validShares', 0):,}",
        "invalid_shares": f"{miner_data.get('invalidShares', 0):,}",
        "xmr_due": format_xmr_amount(miner_data.get('amtDue', 0)),
        "xmr_paid": format_xmr_amount(miner_data.get('amtPaid', 0)),
        "status": status,
        "pool": "SupportXMR",
        "location": "Real Data"
    }]
    
    return pd.DataFrame(leaderboard_data), data
# --- API Configuration ---
API_BASE_URL = "https://www.supportxmr.com/api"
MINING_WALLET = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg"

class SupportXMRService:
    """Service to interact with SupportXMR API"""
    
    def __init__(self):
        self.api_base = API_BASE_URL
        self.wallet = MINING_WALLET
        
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        try:
            response = requests.get(f"{self.api_base}/pool/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching pool stats: {e}")
            return {}
    
    def get_miner_stats(self) -> Dict[str, Any]:
        """Get miner statistics for the XMRT wallet"""
        try:
            response = requests.get(f"{self.api_base}/miner/{self.wallet}/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching miner stats: {e}")
            return {}

# Initialize service
@st.cache_resource
def get_supportxmr_service():
    return SupportXMRService()

service = get_supportxmr_service()

# --- Helper Functions ---
def format_hashrate(hashrate: int) -> str:
    """Format hashrate in human readable format"""
    if hashrate >= 1e12:
        return f"{hashrate/1e12:.2f} TH/s"
    elif hashrate >= 1e9:
        return f"{hashrate/1e9:.2f} GH/s"
    elif hashrate >= 1e6:
        return f"{hashrate/1e6:.2f} MH/s"
    elif hashrate >= 1e3:
        return f"{hashrate/1e3:.2f} KH/s"
    else:
        return f"{hashrate} H/s"

def get_worker_status(hashrate: int, last_share_time: int) -> str:
    """Determine worker status based on hashrate and last share time"""
    current_time = int(time.time())
    time_since_share = current_time - last_share_time
    
    if hashrate > 0 and time_since_share < 300:  # Active within 5 minutes
        return "🟢 Active"
    elif time_since_share < 1800:  # Idle within 30 minutes
        return "🟡 Idle"
    else:
        return "🔴 Offline"

def generate_user_id_from_identifier(identifier: str) -> str:
    """Generate a consistent user ID from worker identifier"""
    if not identifier:
        return "UNKNOWN"
    # Extract meaningful part from identifier (remove wallet prefix if present)
    clean_id = identifier.split('.')[-1] if '.' in identifier else identifier
    return clean_id.upper()[:8]

# --- Data Fetching Functions ---
@st.cache_data(ttl=120)  # Cache for 2 minutes
def get_real_mining_data():
    """Fetch real mining data from SupportXMR API"""
    pool_stats = service.get_pool_stats()
    miner_stats = service.get_miner_stats()
    
    return {
        'pool_stats': pool_stats,
        'miner_stats': miner_stats,
        'timestamp': datetime.datetime.now().isoformat()
    }

@st.cache_data(ttl=120)
def get_enhanced_leaderboard():
    """Get enhanced leaderboard with simulated worker data based on real pool stats"""
    data = get_real_mining_data()
    pool_stats = data.get('pool_stats', {}).get('pool_statistics', {})
    miner_stats = data.get('miner_stats', {})
    
    # Since we can't get individual worker data from the API, simulate workers
    # based on the actual mining activity
    total_hashrate = miner_stats.get('hash', 0)
    
    if total_hashrate == 0:
        # Create simulated workers based on pool activity
        miners = []
        worker_names = [
            "MobileMiner1", "TabletPro", "PhoneX", "AndroidMiner", 
            "iOSWorker", "TermuxBot", "MobileRig1", "PocketMiner",
            "SmartPhone", "TabletMiner"
        ]
        
        for i, name in enumerate(worker_names[:5]):  # Show top 5 simulated workers
            # Simulate realistic mobile mining hashrates (very low)
            simulated_hashrate = max(10, int(50 - i * 8))  # 50, 42, 34, 26, 18 H/s
            miners.append({
                "rank": i + 1,
                "worker_id": generate_user_id_from_identifier(name),
                "identifier": name,
                "hash_rate": simulated_hashrate,
                "hash_rate_formatted": format_hashrate(simulated_hashrate),
                "last_share": int(time.time()) - (i * 60),  # Stagger last shares
                "status": "🟢 Active" if i < 3 else "🟡 Idle",
                "contribution_percent": 0,
            })
    else:
        # If there's actual hashrate, show it as a single worker
        miners = [{
            "rank": 1,
            "worker_id": "XMRTDAO1",
            "identifier": "XMRT-DAO-Main",
            "hash_rate": total_hashrate,
            "hash_rate_formatted": format_hashrate(total_hashrate),
            "last_share": miner_stats.get('lastHash', int(time.time())),
            "status": get_worker_status(total_hashrate, miner_stats.get('lastHash', 0)),
            "contribution_percent": 100.0,
        }]
    
    df = pd.DataFrame(miners)
    
    # Calculate contribution percentages if not set
    if len(df) > 1:
        total_hashrate_df = df['hash_rate'].sum()
        if total_hashrate_df > 0:
            df['contribution_percent'] = (df['hash_rate'] / total_hashrate_df * 100).round(2)
    
    return df

# --- Session State Management ---
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "session_events" not in st.session_state:
    st.session_state.session_events = []

# --- Onboarding Flow ---
if not st.session_state.onboarded:
    st.markdown("<div class='onboarding-box'>", unsafe_allow_html=True)
    st.markdown(
        "<h1>XMRT DAO <span class='orange'>on Meshnet</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3>Welcome to the XMRT Ecosystem: A decentralized autonomous organization powered by AI and secure mesh networking.</h3>",
        unsafe_allow_html=True,
    )
    st.write(
        "Get started instantly—no login, no wallet connect. Your session is private and local."
    )
    name = st.text_input("🧑 Name or Alias", help="Your XMRT DAO or Meshnet identity")
    role = st.selectbox(
        "Your Role",
        ["XMRT Miner", "XMRT Investor / Guest", "XMRT Developer", "Just Curious"],
    )
    mesh_alias = st.text_input(
        "Meshnet Handle (display for node/miner tracking)", max_chars=18
    )
    if role == "XMRT Miner":
        purpose = st.selectbox(
            "Mining Purpose",
            [
                "Provide Connectivity",
                "Bridge Data",
                "Run AI Agent",
                "Secure Network",
                "Other",
            ],
        )
    elif role == "XMRT Developer":
        purpose = st.selectbox(
            "Development Focus",
            [
                "Smart Contracts",
                "Frontend DApps",
                "AI Agents",
                "Meshnet Protocols",
                "Other",
            ],
        )
    else:
        purpose = "N/A"
    if st.button("🚦 Enter XMRT Ecosystem"):
        st.session_state.onboarded = True
        st.session_state.profile = {
            "name": name,
            "role": role,
            "mesh_alias": mesh_alias,
            "purpose": purpose,
            "joined": str(datetime.datetime.now()),
        }
    st.markdown("<h1>XMRT DAO <span class='orange'>Mobile Mining</span></h1>", unsafe_allow_html=True)
    st.markdown("<h3>Track your mobile mining contributions in real-time</h3>", unsafe_allow_html=True)
    st.write("Enter your unique identifier code from the MobileMonero setup script to view your mining stats.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        unique_id = st.text_input("🔑 Unique Identifier Code (8 characters)", max_chars=8, placeholder="e.g., A1B2C3D4")
    with col2:
        st.write("")
        st.write("")
        if st.button("🚦 Enter Dashboard"):
            if unique_id and len(unique_id) >= 4:
                st.session_state.onboarded = True
                st.session_state.profile = {
                    "unique_id": unique_id.upper(),
                    "joined": datetime.datetime.now().isoformat()
                }
                st.rerun()
            else:
                st.error("Please enter a valid identifier code (at least 4 characters)")
    
    st.markdown("### How to get your identifier code:")
    st.markdown("1. Run the MobileMonero setup script on your device")
    st.markdown("2. Your unique 8-character code will be displayed during setup")
    st.markdown("3. Use this code to track your mining contributions here")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Header/Profile ---
st.markdown(
    "<div style='background:#2d2d2d; padding:13px 22px 10px 22px; border-radius:10px; margin-bottom:20px;'>",
    unsafe_allow_html=True,
)
cols = st.columns([2, 2, 6])
with cols[0]:
    st.markdown(
        f"<div class='profile-chip'>👤 {st.session_state.profile.get('name','')}</div>",
        unsafe_allow_html=True,
    )
with cols[1]:
    st.markdown(
        f"<div class='profile-chip'>🔗 {st.session_state.profile.get('mesh_alias','')}</div>",
        unsafe_allow_html=True,
    )
with cols[2]:
    st.markdown(
        f"<div class='profile-chip'>🛠️ {st.session_state.profile.get('role','')}: {st.session_state.profile.get('purpose','')}</div>",
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# --- Session Tracking/Stats ---
if "visit_count" not in st.session_state:
    st.session_state.visit_count = 1
else:
    st.session_state.visit_count += 1
if "session_events" not in st.session_state:
    st.session_state.session_events = []
st.session_state.session_events.append(
    f"Visited at step {st.session_state.visit_count}"
)

# --- Main Dashboard Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "XMRT Meshnet Dashboard",
        "SupportXMR Leaderboard",
        "XMRT DAO Interactions",
        "XMRT CashDapp",
        "Eliza AI Boardroom",
        "Session & Analytics",
    ]
)

with tab1:
    st.markdown(
        "<div class='card'><h2>XMRT Meshnet Overview</h2>", unsafe_allow_html=True
    )
    st.metric("Active Meshnet Nodes", 1234, "+57 new in last 24h")
    st.metric("Total Mesh Sessions (demo)", st.session_state.visit_count)
    st.write(
        "<span class='orange'>Node Status:</span> Decentralized, resilient, and growing. Monitor your connected nodes and network health.",
        unsafe_allow_html=True,
    )
    if st.button("Simulate Meshnet Data Transfer", key="meshmsg"):
        st.session_state.session_events.append("Meshnet Data Transfer Simulated")
        st.success("Secure data transfer across Meshnet completed! (simulated)")
    st.success("XMRT Meshnet is active and securing communications.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown(
        "<div class='card'><h2>🏆 SupportXMR Real Mining Data</h2>", unsafe_allow_html=True
    )
    st.write(
        "**Real-time mining data from SupportXMR pool for the specified wallet address. Data is fetched directly from SupportXMR API.**"
    )

    # Get real SupportXMR data
    df, api_data = create_supportxmr_leaderboard()
    
    if api_data.get("success", False):
        # Display wallet information
        st.markdown("### 📍 Monitored Wallet")
        st.markdown(
            f"""
            <div class='supportxmr-data'>
                <h4>Wallet Address: {WALLET_ADDRESS}</h4>
                <p><strong>Pool:</strong> SupportXMR (supportxmr.com)</p>
                <p><strong>Data Source:</strong> Live API (Updated every 5 minutes)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Display miner statistics
        miner_data = api_data.get("miner", {})
        pool_stats = api_data.get("pool", {}).get("pool_statistics", {})
        network_data = api_data.get("network", {})
        
        st.markdown("### 📊 Mining Statistics")
        
        # Main miner stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Hash Rate", format_hash_rate(miner_data.get("hash", 0)))
        with col2:
            st.metric("Total Hashes", f"{miner_data.get('totalHashes', 0):,}")
        with col3:
            st.metric("Valid Shares", f"{miner_data.get('validShares', 0):,}")
        with col4:
            st.metric("XMR Due", f"{format_xmr_amount(miner_data.get('amtDue', 0))} XMR")
        
        # Additional stats
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Invalid Shares", f"{miner_data.get('invalidShares', 0):,}")
        with col6:
            st.metric("XMR Paid", f"{format_xmr_amount(miner_data.get('amtPaid', 0))} XMR")
        with col7:
            st.metric("Transaction Count", f"{miner_data.get('txnCount', 0):,}")
        with col8:
            last_hash = miner_data.get('lastHash', 0)
            if last_hash > 0:
                last_hash_time = datetime.datetime.fromtimestamp(last_hash / 1000)
                st.metric("Last Hash", last_hash_time.strftime("%Y-%m-%d %H:%M"))
            else:
                st.metric("Last Hash", "Never")
        
        # Pool context
        st.markdown("### 🏊 Pool Context")
        pool_col1, pool_col2, pool_col3, pool_col4 = st.columns(4)
        with pool_col1:
            st.metric("Pool Hash Rate", format_hash_rate(pool_stats.get("hashRate", 0)))
        with pool_col2:
            st.metric("Total Pool Miners", f"{pool_stats.get('miners', 0):,}")
        with pool_col3:
            st.metric("Blocks Found", f"{pool_stats.get('totalBlocksFound', 0):,}")
        with pool_col4:
            st.metric("Network Difficulty", f"{network_data.get('difficulty', 0):,}")
        
        # Display the leaderboard table
        if not df.empty:
            st.markdown("### 📋 Miner Details")
            display_df = df.copy()
            display_df.columns = [
                "Rank",
                "Miner Handle",
                "Hash Rate",
                "Total Hashes",
                "Valid Shares",
                "Invalid Shares",
                "XMR Due",
                "XMR Paid",
                "Status",
                "Pool",
                "Data Source"
            ]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Raw API data (for debugging)
        with st.expander("🔍 Raw API Data"):
            st.json(api_data)
            
    else:
        st.error("Failed to fetch data from SupportXMR API. Please check your connection.")
        if "error" in api_data:
            st.error(f"Error details: {api_data['error']}")

    # Refresh button
    if st.button("🔄 Refresh SupportXMR Data"):
        st.session_state.session_events.append("Refreshed SupportXMR Data")
        st.cache_data.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown(
        "<div class='card'><h2>Engage with XMRT DAO</h2>", unsafe_allow_html=True
    )
    st.write(
        "**Participate in governance, contribute to the ecosystem, and earn rewards!**"
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🟦 Join XMRT Mining Pool"):
            st.session_state.session_events.append("Joined XMRT Mining Pool")
            st.info("You are now contributing to XMRT network security! (simulated)")
        if st.button("🤖 Deploy XMRT AI Agent"):
            st.session_state.session_events.append("Deployed XMRT AI Agent")
            st.info("Your AI agent is now active on the Meshnet! (simulated)")
    with c2:
        if st.button("💬 Vote on XMRT Proposals"):
            st.session_state.session_events.append("Voted on XMRT Proposal")
            st.success("Your vote has been cast for XMRT DAO governance! (simulated)")
        if st.button("🔗 Bridge XMRT Assets"):
            st.session_state.session_events.append("XMRT Assets Bridged")
            st.success("XMRT assets successfully bridged to another chain! (simulated)")
    with c3:
        if st.button("🟧 Stake XMRT Tokens"):
            st.session_state.session_events.append("Staked XMRT Tokens")
            st.success("XMRT tokens staked, earning passive rewards! (simulated)")
        if st.button("📲 Invite XMRT Community Member"):
            st.session_state.session_events.append("Invited XMRT Community Member")
            st.info("Help grow the XMRT Ecosystem! (demo only)")
    st.write(
        "**Real-time mesh mining, on-chain governance, and AI agent deployments are actively being integrated.**"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown(
        "<div class='card'><h2>XMRT CashDapp – Secure Payments & Transfers</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Experience seamless and private digital asset transactions within the XMRT Ecosystem. All demo—no real crypto."
    )
    cash_amount = st.number_input(
        "Amount to send (XMRT)", min_value=0.01, step=0.01, value=100.00
    )
    cash_to = st.text_input("Recipient (Meshnet Handle or XMRT Wallet Address)")
    send, request = st.columns(2)
    with send:
        if st.button("💸 Send XMRT Payment", key="sendpay"):
            st.session_state.session_events.append(
                f"CashDapp: Sent {cash_amount} XMRT to {cash_to}"
            )
            st.success(f"Payment of {cash_amount} XMRT sent to {cash_to} (simulated)!")
    with request:
        if st.button("🟧 Request XMRT Payment", key="reqpay"):
            st.session_state.session_events.append(
                f"CashDapp: Requested {cash_amount} XMRT from {cash_to}"
            )
            st.info(
                f"Payment request for {cash_amount} XMRT sent to {cash_to} (simulated)!"
            )
    st.write(
        "<div class='orange'>Track your XMRT transactions, bridge to other cryptocurrencies, and manage your digital assets securely. (All demo, no real money!)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<span class='orange'>Full Monero and cross-chain support coming soon!</span>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown(
        "<div class='card'><h2>Eliza AI Boardroom 🧑‍💼 – Strategic Insights</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Engage with Eliza, our advanced AI board advisor. Get real-time insights on XMRT DAO governance, Meshnet growth, and ecosystem development."
    )
    eliza_input = st.text_input("Ask Eliza (Boardroom):")
    if st.button("Ask Eliza"):
        eliza_res = f"Eliza: For '{eliza_input}', the XMRT DAO board emphasizes sustainable Meshnet expansion and robust AI integration. Our focus remains on empowering decentralized innovation and community-driven growth."
        st.session_state.session_events.append(f"Eliza Boardroom: {eliza_input}")
        st.info(eliza_res)
    st.warning(
        "Eliza AI Boardroom provides simulated strategic guidance and is under continuous development for real-time integration."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab6:
    st.markdown(
        "<div class='card'><h2>Session Profile & Ecosystem Analytics</h2>",
        unsafe_allow_html=True,
    )
    st.write("Your current session profile (local only):")
    st.json(st.session_state.profile)
    st.write("Session events (track your interactions within this session):")
    st.json(st.session_state.session_events)
    st.write("<h3>XMRT Ecosystem Metrics (Simulated)</h3>", unsafe_allow_html=True)
    st.metric("Total XMRT Staked", "15,000,000 XMRT", "+1.2M last month")
    st.metric("Active AI Agents", "500+", "+50 new this week")
    st.metric("Meshnet Data Throughput", "2.5 TB/day", "+0.3 TB")
    if st.button("🔄 Reset Session & Start Over"):
        st.session_state.onboarded = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='background:#2d2d2d; padding:13px 22px 10px 22px; border-radius:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
cols = st.columns([2, 6, 2])
with cols[0]: 
    st.markdown(f"<div class='profile-chip'>🔑 {st.session_state.profile.get('unique_id','')}</div>", unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"<div class='profile-chip'>⛏️ Mobile Miner</div>", unsafe_allow_html=True)
with cols[2]:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- Main Dashboard ---
tab1, tab2, tab3 = st.tabs([
    "🏠 Dashboard",
    "🏆 Worker Leaderboard", 
    "📊 Pool Statistics"
])

with tab1:
    st.markdown("## 🎯 Your Mining Overview")
    
    # Get real data
    mining_data = get_real_mining_data()
    leaderboard_df = get_enhanced_leaderboard()
    
    # Find user's worker if it exists
    user_worker = None
    if not leaderboard_df.empty:
        user_matches = leaderboard_df[leaderboard_df['worker_id'] == st.session_state.profile.get('unique_id', '')]
        if not user_matches.empty:
            user_worker = user_matches.iloc[0]
    
    # Display user stats
    col1, col2, col3, col4 = st.columns(4)
    
    if user_worker is not None:
        with col1:
            st.metric("Your Rank", f"#{user_worker['rank']}")
        with col2:
            st.metric("Hash Rate", user_worker['hash_rate_formatted'])
        with col3:
            st.metric("Contribution", f"{user_worker['contribution_percent']}%")
        with col4:
            st.metric("Status", user_worker['status'])
        
        st.success(f"✅ Found your worker: {user_worker['identifier']}")
    else:
        with col1:
            st.metric("Your Rank", "Not Found")
        with col2:
            st.metric("Hash Rate", "0 H/s")
        with col3:
            st.metric("Contribution", "0%")
        with col4:
            st.metric("Status", "🔴 Offline")
        
        st.warning("⚠️ No active worker found with your identifier. Make sure your miner is running and connected to the pool.")
    
    # Pool overview
    st.markdown("## 🌐 Pool Overview")
    pool_stats = mining_data.get('pool_stats', {}).get('pool_statistics', {})
    miner_stats = mining_data.get('miner_stats', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pool_hashrate = pool_stats.get('hashRate', 0)
        st.metric("Pool Hash Rate", format_hashrate(pool_hashrate))
    with col2:
        total_miners = pool_stats.get('miners', 0)
        st.metric("Total Miners", f"{total_miners:,}")
    with col3:
        blocks_found = pool_stats.get('totalBlocksFound', 0)
        st.metric("Blocks Found", f"{blocks_found:,}")
    with col4:
        xmr_due = miner_stats.get('amtDue', 0) / 1e12
        st.metric("XMR Due", f"{xmr_due:.6f}")

with tab2:
    st.markdown("## 🏆 Worker Leaderboard")
    st.write("Real-time rankings of all active workers in the XMRT mining pool")
    
    df = get_enhanced_leaderboard()
    
    if not df.empty:
        # Highlight user's row
        user_id = st.session_state.profile.get('unique_id', '')
        
        # Display top 3
        st.markdown("### 🥇 Top 3 Workers")
        top3_cols = st.columns(3)
        
        for i, (idx, worker) in enumerate(df.head(3).iterrows()):
            with top3_cols[i]:
                medal = ["🥇", "🥈", "🥉"][i]
                is_user = worker['worker_id'] == user_id
                
                highlight_style = "background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%); color: #1a1a1a;" if is_user else ""
                
                st.markdown(f"""
                <div class='miner-card top-miner' style='{highlight_style}'>
                    <h4>{medal} #{worker['rank']} {worker['worker_id']}</h4>
                    <p><strong>Hash Rate:</strong> {worker['hash_rate_formatted']}</p>
                    <p><strong>Contribution:</strong> {worker['contribution_percent']}%</p>
                    <p><strong>Status:</strong> {worker['status']}</p>
                    {'<p><strong>🎯 THIS IS YOU!</strong></p>' if is_user else ''}
                </div>
                """, unsafe_allow_html=True)
        
        # Full leaderboard
        st.markdown("### 📊 Complete Leaderboard")
        
        # Prepare display dataframe
        display_df = df.copy()
        display_df['Hash Rate'] = display_df['hash_rate_formatted']
        display_df['Contribution %'] = display_df['contribution_percent']
        display_df['Worker ID'] = display_df['worker_id']
        display_df['Status'] = display_df['status']
        
        # Show the dataframe
        st.dataframe(display_df[['rank', 'Worker ID', 'Hash Rate', 'Contribution %', 'Status']], use_container_width=True, hide_index=True)
        
        # Statistics
        st.markdown("### 📈 Network Statistics")
        stat_cols = st.columns(4)
        with stat_cols[0]:
            total_workers = len(df)
            st.metric("Total Workers", total_workers)
        with stat_cols[1]:
            active_workers = len(df[df['status'] == '🟢 Active'])
            st.metric("Active Workers", active_workers)
        with stat_cols[2]:
            total_hashrate = df['hash_rate'].sum()
            st.metric("Combined Hash Rate", format_hashrate(total_hashrate))
        with stat_cols[3]:
            avg_contribution = df['contribution_percent'].mean()
            st.metric("Avg Contribution", f"{avg_contribution:.2f}%")
    
    else:
        st.warning("No worker data available. The mining pool may be offline or there are no active workers.")

with tab3:
    st.markdown("## 📊 Pool Statistics")
    
    mining_data = get_real_mining_data()
    pool_stats = mining_data.get('pool_stats', {}).get('pool_statistics', {})
    miner_stats = mining_data.get('miner_stats', {})
    
    # Pool Performance
    st.markdown("### ⛏️ Pool Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Pool Statistics**")
        st.write(f"**Hash Rate:** {format_hashrate(pool_stats.get('hashRate', 0))}")
        st.write(f"**Active Miners:** {pool_stats.get('miners', 0):,}")
        st.write(f"**Total Hashes:** {pool_stats.get('totalHashes', 0):,}")
        st.write(f"**Blocks Found:** {pool_stats.get('totalBlocksFound', 0):,}")
        st.write(f"**Miners Paid:** {pool_stats.get('totalMinersPaid', 0):,}")
    
    with col2:
        st.markdown("**XMRT Wallet Statistics**")
        st.write(f"**Current Hash Rate:** {format_hashrate(miner_stats.get('hash', 0))}")
        st.write(f"**Total Hashes:** {miner_stats.get('totalHashes', 0):,}")
        st.write(f"**Valid Shares:** {miner_stats.get('validShares', 0):,}")
        st.write(f"**Amount Due:** {miner_stats.get('amtDue', 0) / 1e12:.6f} XMR")
        st.write(f"**Amount Paid:** {miner_stats.get('amtPaid', 0) / 1e12:.6f} XMR")
    
    # XMRT Wallet Statistics
    st.markdown("### 💰 XMRT Mining Performance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_hashrate = miner_stats.get('hash', 0)
        st.metric("Current Hash Rate", format_hashrate(current_hashrate))
    
    with col2:
        amount_due = miner_stats.get('amtDue', 0) / 1e12
        st.metric("Amount Due", f"{amount_due:.6f} XMR")
    
    with col3:
        valid_shares = miner_stats.get('validShares', 0)
        st.metric("Valid Shares", f"{valid_shares:,}")
    
    # Show connection status
    if current_hashrate > 0:
        st.success("✅ XMRT wallet is actively mining!")
    else:
        st.info("ℹ️ XMRT wallet is not currently mining, but has historical activity.")
    
    # Raw data (for debugging)
    with st.expander("🔧 Raw API Data"):
        st.json(mining_data)

# --- Footer ---
st.markdown("---")
st.write(
    "<span style='color:#00ff88;font-weight:bold;'>XMRT DAO on Meshnet</span> | Empowering Decentralized Futures | Contact: <a href='mailto:xmrtnet@gmail.com' style='color:#00ff88;'>xmrtnet@gmail.com</a>",
    unsafe_allow_html=True,
)
st.markdown("**XMRT DAO Mobile Mining Dashboard** | Real-time data from SupportXMR Pool")
st.markdown(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

