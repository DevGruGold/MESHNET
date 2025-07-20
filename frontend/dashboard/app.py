import streamlit as st
import datetime
import pandas as pd
import random

st.set_page_config(page_title="XMRT DAO – Corporate Meshnet", layout="wide")

# --- Theme Management ---
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" # Default to Dark theme

# --- Corporate Fintech Styling ---
if st.session_state.theme == "Dark":
    st.markdown("""
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
            @media (max-width: 700px) {
                .onboarding-box, .card { padding: 12px 6px 10px 6px; }
                h1 { font-size: 25px; }
            }
        </style>
    """, unsafe_allow_html=True)
else: # Light theme styling
    st.markdown("""
        <style>
            body { background: #f0f2f6 !important; color: #333333; font-family: 'Inter', 'Arial', sans-serif; }
            h1, h2, h3, h4, h5 { color: #333333; } /* Changed to dark grey for visibility */
            .stButton > button {
                background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
                color: #ffffff !important;
                width: 100%;
                height: 50px;
                font-size: 20px;
                border-radius: 7px;
                font-weight: 600;
                margin-bottom: 12px;
                box-shadow: 0 2px 12px rgba(0, 123, 255, 0.25);
            }
            .stTextInput > div > input, .stNumberInput > div > input {
                background: #ffffff;
                color: #333333;
                font-size: 18px;
                border-radius: 7px;
                border: 1.5px solid #007bff;
            }
            .onboarding-box {
                background: #ffffff;
                border: 1.5px solid #007bff;
                box-shadow: 0 4px 24px rgba(0, 123, 255, 0.1);
                padding: 28px 22px 18px 22px;
                border-radius: 14px;
                margin-bottom: 20px;
            }
            .profile-chip {
                display: inline-block;
                background: #007bff;
                color: #ffffff;
                border: 1.5px solid #007bff;
                padding: 5px 18px;
                margin: 3px 6px 3px 0;
                border-radius: 20px;
                font-size: 17px;
                font-weight: 600;
            }
            .card {
                background: #ffffff;
                border-radius: 14px;
                box-shadow: 0 3px 16px rgba(0, 123, 255, 0.1);
                padding: 26px 22px 18px 22px;
                margin-bottom: 26px;
                border: 1.5px solid #007bff;
            }
            .orange { color: #007bff; font-weight: bold; }
            .interaction-btn {
                background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
                color: #ffffff !important;
                font-weight: 600;
                border-radius: 8px;
                font-size: 19px;
                margin-bottom: 8px;
            }
            .stTabs [data-baseweb="tab-list"] {
                background: #f0f2f6;
                border-radius: 10px 10px 0 0;
            }
            .stTabs [data-baseweb="tab"] {
                color: #007bff;
                background: #ffffff;
                border-radius: 10px 10px 0 0;
                padding: 10px 18px;
                margin-right: 2px;
                font-size: 18px;
            }
            .stTabs [aria-selected="true"] {
                color: #ffffff !important;
                background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
                border-bottom: 3px solid #007bff !important;
            }
            .leaderboard-rank {
                background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
                color: #ffffff;
                padding: 5px 12px;
                border-radius: 15px;
                font-weight: bold;
                margin-right: 10px;
            }
            .miner-card {
                background: #ffffff;
                border: 1px solid #007bff;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
            }
            .top-miner {
                background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
                color: #ffffff;
                border: 2px solid #007bff;
            }
            @media (max-width: 700px) {
                .onboarding-box, .card { padding: 12px 6px 10px 6px; }
                h1 { font-size: 25px; }
            }
        </style>
    """, unsafe_allow_html=True)

# --- Theme Toggle (for demonstration) ---
if st.sidebar.button(f"Switch to {"Light" if st.session_state.theme == "Dark" else "Dark"} Theme"):
    st.session_state.theme = 'Light' if st.session_state.theme == 'Dark' else 'Dark'
    st.experimental_rerun()

# --- Initialize Miner Leaderboard Data ---
@st.cache_data
def get_miner_leaderboard():
    miners = [
        {"rank": 1, "handle": "CryptoMiner_X", "hash_rate": "2.5 TH/s", "blocks_mined": 1247, "xmrt_earned": 15420.50, "uptime": "99.8%", "location": "USA", "status": "🟢 Active"},
        {"rank": 2, "handle": "MeshNode_Alpha", "hash_rate": "2.1 TH/s", "blocks_mined": 1089, "xmrt_earned": 13567.25, "uptime": "99.5%", "location": "Germany", "status": "🟢 Active"},
        {"rank": 3, "handle": "QuantumMiner", "hash_rate": "1.9 TH/s", "blocks_mined": 987, "xmrt_earned": 12234.75, "uptime": "98.9%", "location": "Japan", "status": "🟢 Active"},
        {"rank": 4, "handle": "DeepMesh_Pro", "hash_rate": "1.7 TH/s", "blocks_mined": 856, "xmrt_earned": 10678.00, "uptime": "99.2%", "location": "Canada", "status": "🟢 Active"},
        {"rank": 5, "handle": "NeuralNode_1", "hash_rate": "1.5 TH/s", "blocks_mined": 743, "xmrt_earned": 9234.50, "uptime": "97.8%", "location": "UK", "status": "🟡 Syncing"},
        {"rank": 6, "handle": "CyberMiner_Z", "hash_rate": "1.4 TH/s", "blocks_mined": 689, "xmrt_earned": 8567.25, "uptime": "98.5%", "location": "Australia", "status": "🟢 Active"},
        {"rank": 7, "handle": "MeshGuardian", "hash_rate": "1.3 TH/s", "blocks_mined": 634, "xmrt_earned": 7890.75, "uptime": "99.1%", "location": "Netherlands", "status": "🟢 Active"},
        {"rank": 8, "handle": "DigitalNomad", "hash_rate": "1.2 TH/s", "blocks_mined": 578, "xmrt_earned": 7123.00, "uptime": "96.7%", "location": "Singapore", "status": "🟢 Active"},
        {"rank": 9, "handle": "BlockChaser", "hash_rate": "1.1 TH/s", "blocks_mined": 523, "xmrt_earned": 6456.50, "uptime": "98.3%", "location": "Brazil", "status": "🟢 Active"},
        {"rank": 10, "handle": "MeshMaster_V2", "hash_rate": "1.0 TH/s", "blocks_mined": 467, "xmrt_earned": 5789.25, "uptime": "97.5%", "location": "France", "status": "🟡 Syncing"}
    ]
    return pd.DataFrame(miners)

# --- Onboarding State ---
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "profile" not in st.session_state:
    st.session_state.profile = {}

# --- Onboarding Flow ---
if not st.session_state.onboarded:
    st.markdown("<div class=\'onboarding-box\'>", unsafe_allow_html=True)
    st.markdown("<h1>XMRT DAO <span class=\'orange\'>on Meshnet</span></h1>", unsafe_allow_html=True)
    st.markdown("<h3>Welcome to the XMRT Ecosystem: A decentralized autonomous organization powered by AI and secure mesh networking.</h3>", unsafe_allow_html=True)
    st.write("Get started instantly—no login, no wallet connect. Your session is private and local.")
    name = st.text_input("🧑 Name or Alias", help="Your XMRT DAO or Meshnet identity")
    role = st.selectbox("Your Role", ["XMRT Miner", "XMRT Investor / Guest", "XMRT Developer", "Just Curious"])
    mesh_alias = st.text_input("Meshnet Handle (display for node/miner tracking)", max_chars=18)
    if role == "XMRT Miner":
        purpose = st.selectbox("Mining Purpose", ["Provide Connectivity", "Bridge Data", "Run AI Agent", "Secure Network", "Other"])
    elif role == "XMRT Developer":
        purpose = st.selectbox("Development Focus", ["Smart Contracts", "Frontend DApps", "AI Agents", "Meshnet Protocols", "Other"])
    else:
        purpose = "N/A"
    if st.button("🚦 Enter XMRT Ecosystem"):
        st.session_state.onboarded = True
        st.session_state.profile = {
            "name": name,
            "role": role,
            "mesh_alias": mesh_alias,
            "purpose": purpose,
            "joined": str(datetime.datetime.now())
        }
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Header/Profile ---
st.markdown("<div style=\'background:#2d2d2d; padding:13px 22px 10px 22px; border-radius:10px; margin-bottom:20px;\'>", unsafe_allow_html=True)
cols = st.columns([2,2,6])
with cols[0]: st.markdown(f"<div class=\'profile-chip\'>👤 {st.session_state.profile.get('name','')}<\/div>", unsafe_allow_html=True)
with cols[1]: st.markdown(f"<div class=\'profile-chip\'>🔗 {st.session_state.profile.get('mesh_alias','')}<\/div>", unsafe_allow_html=True)
with cols[2]: st.markdown(f"<div class=\'profile-chip\'>🛠️ {st.session_state.profile.get('role','')}: {st.session_state.profile.get('purpose','')}<\/div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Session Tracking/Stats ---
if "visit_count" not in st.session_state:
    st.session_state.visit_count = 1
else:
    st.session_state.visit_count += 1
if "session_events" not in st.session_state:
    st.session_state.session_events = []
st.session_state.session_events.append(f"Visited at step {st.session_state.visit_count}")

# --- Main Dashboard Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "XMRT Meshnet Dashboard",
    "Miner Leaderboard",
    "XMRT DAO Interactions",
    "XMRT CashDapp",
    "Eliza AI Boardroom",
    "Session & Analytics"
])

with tab1:
    st.markdown("<div class=\'card\'><h2>XMRT Meshnet Overview</h2>", unsafe_allow_html=True)
    st.metric("Active Meshnet Nodes", 1234, "+57 new in last 24h")
    st.metric("Total Mesh Sessions (demo)", st.session_state.visit_count)
    st.write("<span class=\'orange\'>Node Status:</span> Decentralized, resilient, and growing. Monitor your connected nodes and network health.", unsafe_allow_html=True)
    if st.button("Simulate Meshnet Data Transfer", key="meshmsg"):
        st.session_state.session_events.append("Meshnet Data Transfer Simulated")
        st.success("Secure data transfer across Meshnet completed! (simulated)")
    st.success("XMRT Meshnet is active and securing communications.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class=\'card\'><h2>🏆 XMRT Miner Leaderboard</h2>", unsafe_allow_html=True)
    st.write("**Top performing miners in the XMRT Meshnet ecosystem. Rankings updated in real-time based on hash rate, blocks mined, and network contribution.**")
    
    # Leaderboard controls
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        sort_by = st.selectbox("Sort by:", ["Rank", "Hash Rate", "Blocks Mined", "XMRT Earned", "Uptime"])
    with col2:
        filter_status = st.selectbox("Filter by Status:", ["All", "🟢 Active", "🟡 Syncing", "🔴 Offline"])
    with col3:
        if st.button("🔄 Refresh Leaderboard"):
            st.session_state.session_events.append("Refreshed Miner Leaderboard")
            st.success("Leaderboard updated!")
    
    # Get leaderboard data
    df = get_miner_leaderboard()
    
    # Apply filters
    if filter_status != "All":
        df = df[df['status'] == filter_status]
    
    # Display top 3 miners prominently
    st.markdown("### 🥇 Top 3 Miners")
    top3_cols = st.columns(3)
    
    for i, (idx, miner) in enumerate(df.head(3).iterrows()):
        with top3_cols[i]:
            medal = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"""
            <div class=\'miner-card top-miner\'>
                <h4>{medal} #{miner['rank']} {miner['handle']}</h4>
                <p><strong>Hash Rate:</strong> {miner['hash_rate']}</p>
                <p><strong>Blocks:</strong> {miner['blocks_mined']}</p>
                <p><strong>XMRT Earned:</strong> {miner['xmrt_earned']:, .2f}</p>
                <p><strong>Uptime:</strong> {miner['uptime']}</p>
                <p><strong>Status:</strong> {miner['status']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Full leaderboard table
    st.markdown("### 📊 Complete Leaderboard")
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df['XMRT Earned'] = display_df['xmrt_earned'].apply(lambda x: f"{x:, .2f}")
    display_df = display_df[['rank', 'handle', 'hash_rate', 'blocks_mined', 'XMRT Earned', 'uptime', 'location', 'status']]
    display_df.columns = ['Rank', 'Miner Handle', 'Hash Rate', 'Blocks Mined', 'XMRT Earned', 'Uptime', 'Location', 'Status']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Mining statistics
    st.markdown("### 📈 Network Mining Statistics")
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("Total Network Hash Rate", "15.2 TH/s", "+0.8 TH/s")
    with stat_cols[1]:
        st.metric("Active Miners", len(df[df['status'] == '🟢 Active']), "+2")
    with stat_cols[2]:
        st.metric("Total Blocks Mined", f"{df['blocks_mined'].sum():,}", "+127")
    with stat_cols[3]:
        st.metric("Total XMRT Distributed", f"{df['xmrt_earned'].sum():, .2f}", "+1,234.56")
    
    # Mining pool actions
    mining_cols = st.columns(3)
    with mining_cols[0]:
        if st.button("🚀 Start Mining", key="start_mining"):
            st.session_state.session_events.append("Started XMRT Mining")
            st.success("Mining operation initiated! Your node is now contributing to the XMRT network.")
    with mining_cols[1]:
        if st.button("📊 View My Stats", key="my_stats"):
            st.session_state.session_events.append("Viewed Mining Stats")
            st.info("Your mining statistics: Hash Rate: 0.5 TH/s | Blocks: 23 | XMRT Earned: 287.50")
    with mining_cols[2]:
        if st.button("⚙️ Optimize Settings", key="optimize"):
            st.session_state.session_events.append("Optimized Mining Settings")
            st.info("Mining settings optimized for maximum efficiency!")
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class=\'card\'><h2>Engage with XMRT DAO</h2>", unsafe_allow_html=True)
    st.write("**Participate in governance, contribute to the ecosystem, and earn rewards!**")
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
    st.write("**Real-time mesh mining, on-chain governance, and AI agent deployments are actively being integrated.**")
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class=\'card\'><h2>XMRT CashDapp – Secure Payments & Transfers</h2>", unsafe_allow_html=True)
    st.write("Experience seamless and private digital asset transactions within the XMRT Ecosystem. All demo—no real crypto.")
    cash_amount = st.number_input("Amount to send (XMRT)", min_value=0.01, step=0.01, value=100.00)
    cash_to = st.text_input("Recipient (Meshnet Handle or XMRT Wallet Address)")
    send, request = st.columns(2)
    with send:
        if st.button("💸 Send XMRT Payment", key="sendpay"):
            st.session_state.session_events.append(f"CashDapp: Sent {cash_amount} XMRT to {cash_to}")
            st.success(f"Payment of {cash_amount} XMRT sent to {cash_to} (simulated)!")
    with request:
        if st.button("🟧 Request XMRT Payment", key="reqpay"):
            st.session_state.session_events.append(f"CashDapp: Requested {cash_amount} XMRT from {cash_to}")
            st.info(f"Payment request for {cash_amount} XMRT sent to {cash_to} (simulated)!")
    st.write("<div class=\'orange\'>Track your XMRT transactions, bridge to other cryptocurrencies, and manage your digital assets securely. (All demo, no real money!)</div>", unsafe_allow_html=True)
    st.markdown("<span class=\'orange\'>Full Monero and cross-chain support coming soon!</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("<div class=\'card\'><h2>Eliza AI Boardroom 🧑‍💼 – Strategic Insights</h2>", unsafe_allow_html=True)
    st.write("Engage with Eliza, our advanced AI board advisor. Get real-time insights on XMRT DAO governance, Meshnet growth, and ecosystem development.")
    eliza_input = st.text_input("Ask Eliza (Boardroom):")
    if st.button("Ask Eliza"):
        eliza_res = f"Eliza: For '{eliza_input}', the XMRT DAO board emphasizes sustainable Meshnet expansion and robust AI integration. Our focus remains on empowering decentralized innovation and community-driven growth."
        st.session_state.session_events.append(f"Eliza Boardroom: {eliza_input}")
        st.info(eliza_res)
    st.warning("Eliza AI Boardroom provides simulated strategic guidance and is under continuous development for real-time integration.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab6:
    st.markdown("<div class=\'card\'><h2>Session Profile & Ecosystem Analytics</h2>", unsafe_allow_html=True)
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
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.write("<span style=\'color:#00ff88;font-weight:bold;\'>XMRT DAO on Meshnet</span> | Empowering Decentralized Futures | Contact: <a href=\'mailto:contact@xmrt.org\' style=\'color:#00ff88;\'>contact@xmrt.org</a>", unsafe_allow_html=True)


