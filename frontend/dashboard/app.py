
import streamlit as st
import datetime

st.set_page_config(page_title="XMRT DAO on Meshnet", layout="wide")

# --- CashDapp Neon Style ---
st.markdown("""
    <style>
        body { background: #101010 !important; color: #fff; font-family: 'Inter', 'Arial', sans-serif; }
        h1, h2, h3, h4, h5 { color: #24FF00 !important; }
        .stButton > button {
            background-color: #24FF00 !important;
            color: #101010 !important;
            width: 100%;
            height: 50px;
            font-size: 22px;
            border-radius: 8px;
            font-weight: bold;
            margin-bottom: 10px;
            box-shadow: 0 2px 16px #24FF0080;
        }
        .stTextInput > div > input, .stNumberInput > div > input {
            background: #222;
            color: #fff;
            font-size: 18px;
            border-radius: 8px;
            border: 2px solid #24FF00;
        }
        .orange { color: #FF6600; font-weight: bold; }
        .profile-chip {
            display: inline-block;
            background: #242424;
            color: #24FF00;
            border: 2px solid #FF6600;
            padding: 5px 18px;
            margin: 3px 6px 3px 0;
            border-radius: 20px;
            font-size: 17px;
            font-weight: 600;
        }
        .onboarding-box {
            background: #181818;
            border: 2px solid #24FF00;
            box-shadow: 0 2px 24px #24FF0040;
            padding: 24px 20px 14px 20px;
            border-radius: 14px;
            margin-bottom: 22px;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: #121212;
            border-radius: 10px 10px 0 0;
        }
        .stTabs [data-baseweb="tab"] {
            color: #fff;
            background: #242424;
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
            margin-right: 2px;
            font-size: 18px;
        }
        .stTabs [aria-selected="true"] {
            color: #24FF00 !important;
            background: #181818;
            border-bottom: 3px solid #FF6600 !important;
        }
        @media (max-width: 700px) {
            .onboarding-box { padding: 12px 6px 8px 6px; }
            h1 { font-size: 25px; }
        }
    </style>
""", unsafe_allow_html=True)

# --- Onboarding State ---
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "profile" not in st.session_state:
    st.session_state.profile = {}

# --- Onboarding Flow ---
if not st.session_state.onboarded:
    st.markdown('<div class="onboarding-box">', unsafe_allow_html=True)
    st.markdown('<h1>XMRT DAO <span class="orange">on Meshnet</span></h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#fff;">Welcome to the future of <span class="orange">decentralized money</span> & mesh mining.</h3>', unsafe_allow_html=True)
    st.write("Get started instantly—no login, no wallet connect. Your session is private and local.")
    name = st.text_input("🧑 Name or Alias", help="Your mesh or investor identity")
    role = st.selectbox("Your Mode", ["Miner", "Investor / Guest", "Just Curious"])
    mesh_alias = st.text_input("Mesh Handle (display for node/miner tracking)", max_chars=18)
    if role == "Miner":
        purpose = st.selectbox("Mining Purpose", ["Connectivity", "Bridge Data", "Run Agent", "Other"])
    else:
        purpose = "N/A"
    if st.button("🚦 Enter XMRT Meshnet"):
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
st.markdown('<div style="background:#181818; padding:13px 22px 8px 22px; border-radius:10px; margin-bottom:20px;">', unsafe_allow_html=True)
cols = st.columns([2,2,6])
with cols[0]: st.markdown(f'<div class="profile-chip">👤 {st.session_state.profile.get("name","")}</div>', unsafe_allow_html=True)
with cols[1]: st.markdown(f'<div class="profile-chip">🔗 {st.session_state.profile.get("mesh_alias","")}</div>', unsafe_allow_html=True)
with cols[2]: st.markdown(f'<div class="profile-chip">🛠️ {st.session_state.profile.get("role","")}: {st.session_state.profile.get("purpose","")}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Session Tracking/Stats ---
if "visit_count" not in st.session_state:
    st.session_state.visit_count = 1
else:
    st.session_state.visit_count += 1
if "session_events" not in st.session_state:
    st.session_state.session_events = []
st.session_state.session_events.append(f"Visited at step {st.session_state.visit_count}")

# --- Main Dashboard Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Mesh Dashboard",
    "Agents & AI",
    "CashDapp",
    "Eliza Boardroom",
    "Session"
])

with tab1:
    st.markdown('<h2 style="color:#24FF00;">Mesh Miner Dashboard</h2>', unsafe_allow_html=True)
    st.metric("Active Nodes", 8, "+2 new in last hour")
    st.metric("Mesh Sessions (demo)", st.session_state.visit_count)
    st.write('<span class="orange">Node1</span> (active), Node2 (idle), Node3 (joining)...', unsafe_allow_html=True)
    if st.button("Simulate Mesh Message"):
        st.session_state.session_events.append("Mesh Message Sent")
        st.success("Mesh message sent! (simulated)")
    st.success("Mining enabled! (simulated)")

with tab2:
    st.markdown('<h2 style="color:#24FF00;">Agents, LangChain, Eliza, GPT-5 (Demo)</h2>', unsafe_allow_html=True)
    st.write("AI agents route, score, and automate mesh data (simulated).")
    ai_input = st.text_input("Ask an Agent or AI:")
    if st.button("Run AI Agent"):
        st.session_state.session_events.append(f"AI Agent Queried: {ai_input}")
        st.info("AI/Agent: 'XMRT mesh status is optimal. All agents running.'")
    st.write('<span class="orange">Eliza Chatbot:</span> Hello! How can I help with your mesh or investment questions?', unsafe_allow_html=True)

with tab3:
    st.markdown('<h2 style="color:#24FF00;">CashDapp – Crypto Payments Demo</h2>', unsafe_allow_html=True)
    st.write("Simulate sending, receiving, or bridging digital assets on mesh. All demo—no real crypto.")
    cash_amount = st.number_input("Amount to send", min_value=0.01, step=0.01, value=1.00)
    cash_to = st.text_input("Destination (mesh alias or wallet)")
    # Neon buttons
    send, request = st.columns(2)
    with send:
        if st.button("💸 Send Payment"):
            st.session_state.session_events.append(f"CashDapp: Sent {cash_amount} to {cash_to}")
            st.success(f"Payment of ${cash_amount} sent to {cash_to} (simulated)!")
    with request:
        if st.button("🟧 Request Payment"):
            st.session_state.session_events.append(f"CashDapp: Requested {cash_amount} from {cash_to}")
            st.info(f"Payment request for ${cash_amount} sent to {cash_to} (simulated)!")
    st.write('<div class="orange">Track your mesh payments, bridge to Monero, and manage digital assets. (All demo, no real money!)</div>', unsafe_allow_html=True)
    st.markdown('<span class="orange">Monero support coming soon!</span>', unsafe_allow_html=True)

with tab4:
    st.markdown('<h2 style="color:#24FF00;">Eliza Executive Boardroom 🧑‍💼</h2>', unsafe_allow_html=True)
    st.write("Chat with Eliza, your AI board advisor. Ask about XMRT DAO, mesh growth, or investor strategy.")
    eliza_input = st.text_input("Ask Eliza (Boardroom):")
    if st.button("Ask Eliza"):
        eliza_res = f"Eliza: For '{eliza_input}', the board suggests focusing on mesh resilience and investor transparency. XMRT DAO's next move is global mesh partnerships."
        st.session_state.session_events.append(f"Eliza Boardroom: {eliza_input}")
        st.info(eliza_res)
    st.warning("Eliza Boardroom is a simulation for investor/exec Q&A.")

with tab5:
    st.markdown('<h2 style="color:#24FF00;">Session Profile & Tracking</h2>', unsafe_allow_html=True)
    st.write("Your current session profile (local only):")
    st.json(st.session_state.profile)
    st.write("Session events (track your clicks in this session):")
    st.json(st.session_state.session_events)
    if st.button("🔄 Start Over"):
        st.session_state.onboarded = False
        st.experimental_rerun()

st.markdown("---")
st.write('<span style="color:#24FF00;font-weight:bold;">XMRT DAO on Meshnet</span> | All rights reserved | Contact: <a href="mailto:xmrtnet@gmail.com" style="color:#FF6600;">xmrtnet@gmail.com</a>', unsafe_allow_html=True)
