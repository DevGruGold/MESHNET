
import streamlit as st
import datetime

st.set_page_config(page_title="XMRT DAO – Corporate Meshnet", layout="wide")

# --- Corporate Fintech Styling ---
st.markdown("""
    <style>
        body { background: #f4f7fb !important; color: #222; font-family: 'Inter', 'Arial', sans-serif; }
        h1, h2, h3, h4, h5 { color: #1d3557; }
        .stButton > button {
            background: linear-gradient(90deg, #276ef1 0%, #5ad1e6 100%);
            color: #fff !important;
            width: 100%;
            height: 50px;
            font-size: 20px;
            border-radius: 7px;
            font-weight: 600;
            margin-bottom: 12px;
            box-shadow: 0 2px 12px #5ad1e644;
        }
        .stTextInput > div > input, .stNumberInput > div > input {
            background: #fff;
            color: #222;
            font-size: 18px;
            border-radius: 7px;
            border: 1.5px solid #276ef1;
        }
        .onboarding-box {
            background: #fff;
            border: 1.5px solid #e0e5ec;
            box-shadow: 0 4px 24px #5ad1e622;
            padding: 28px 22px 18px 22px;
            border-radius: 14px;
            margin-bottom: 20px;
        }
        .profile-chip {
            display: inline-block;
            background: #e8f1fa;
            color: #276ef1;
            border: 1.5px solid #ff6600;
            padding: 5px 18px;
            margin: 3px 6px 3px 0;
            border-radius: 20px;
            font-size: 17px;
            font-weight: 600;
        }
        .card {
            background: #fff;
            border-radius: 14px;
            box-shadow: 0 3px 16px #1d355722;
            padding: 26px 22px 18px 22px;
            margin-bottom: 26px;
            border: 1.5px solid #e0e5ec;
        }
        .orange { color: #ff6600; font-weight: bold; }
        .interaction-btn {
            background: linear-gradient(90deg, #ff6600 0%, #276ef1 100%);
            color: #fff !important;
            font-weight: 600;
            border-radius: 8px;
            font-size: 19px;
            margin-bottom: 8px;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: #f4f7fb;
            border-radius: 10px 10px 0 0;
        }
        .stTabs [data-baseweb="tab"] {
            color: #276ef1;
            background: #e8f1fa;
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
            margin-right: 2px;
            font-size: 18px;
        }
        .stTabs [aria-selected="true"] {
            color: #fff !important;
            background: linear-gradient(90deg, #276ef1 0%, #5ad1e6 100%);
            border-bottom: 3px solid #ff6600 !important;
        }
        @media (max-width: 700px) {
            .onboarding-box, .card { padding: 12px 6px 10px 6px; }
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
    st.markdown('<h3>Welcome to the professional mesh for AI, agents, and crypto payments.</h3>', unsafe_allow_html=True)
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
st.markdown('<div style="background:#e8f1fa; padding:13px 22px 10px 22px; border-radius:10px; margin-bottom:20px;">', unsafe_allow_html=True)
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
    "Interact",
    "CashDapp",
    "Eliza Boardroom",
    "Session"
])

with tab1:
    st.markdown('<div class="card"><h2>Mesh Miner Dashboard</h2>', unsafe_allow_html=True)
    st.metric("Active Nodes", 8, "+2 new in last hour")
    st.metric("Mesh Sessions (demo)", st.session_state.visit_count)
    st.write('<span class="orange">Node1</span> (active), Node2 (idle), Node3 (joining)...', unsafe_allow_html=True)
    if st.button("Simulate Mesh Message", key="meshmsg"):
        st.session_state.session_events.append("Mesh Message Sent")
        st.success("Mesh message sent! (simulated)")
    st.success("Mining enabled! (simulated)")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card"><h2>Ways to Interact with XMRT Ecosystem</h2>', unsafe_allow_html=True)
    st.write("**No login, no tokens required—just tap to interact!**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🟦 Join Meshnet Mining"):
            st.session_state.session_events.append("Joined Meshnet mining")
            st.info("You mined a block! (simulated)")
        if st.button("🤖 Deploy an Agent"):
            st.session_state.session_events.append("Deployed an agent")
            st.info("Agent deployed to mesh (simulated)")
    with c2:
        if st.button("💬 Vote in DAO"):
            st.session_state.session_events.append("Voted in DAO")
            st.success("Demo vote cast for XMRT proposal!")
        if st.button("🔗 Bridge Data"):
            st.session_state.session_events.append("Data bridged")
            st.success("Data bridged to another mesh or chain!")
    with c3:
        if st.button("🟧 Tip Miner (Monero style)"):
            st.session_state.session_events.append("Tipped miner")
            st.success("Tip sent to mesh miner (simulated, Monero orange!)")
        if st.button("📲 Invite a Friend"):
            st.session_state.session_events.append("Invited friend")
            st.info("Invite link generated (demo only)")
    st.write("**Coming soon: Real mesh mining, on-chain voting, and agent deployments.**")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card"><h2>CashDapp – Crypto Payments Demo</h2>', unsafe_allow_html=True)
    st.write("Simulate sending, receiving, or bridging digital assets on mesh. All demo—no real crypto.")
    cash_amount = st.number_input("Amount to send", min_value=0.01, step=0.01, value=1.00)
    cash_to = st.text_input("Destination (mesh alias or wallet)")
    send, request = st.columns(2)
    with send:
        if st.button("💸 Send Payment", key="sendpay"):
            st.session_state.session_events.append(f"CashDapp: Sent {cash_amount} to {cash_to}")
            st.success(f"Payment of ${cash_amount} sent to {cash_to} (simulated)!")
    with request:
        if st.button("🟧 Request Payment", key="reqpay"):
            st.session_state.session_events.append(f"CashDapp: Requested {cash_amount} from {cash_to}")
            st.info(f"Payment request for ${cash_amount} sent to {cash_to} (simulated)!")
    st.write('<div class="orange">Track your mesh payments, bridge to Monero, and manage digital assets. (All demo, no real money!)</div>', unsafe_allow_html=True)
    st.markdown('<span class="orange">Monero support coming soon!</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card"><h2>Eliza Executive Boardroom 🧑‍💼</h2>', unsafe_allow_html=True)
    st.write("Chat with Eliza, your AI board advisor. Ask about XMRT DAO, mesh growth, or investor strategy.")
    eliza_input = st.text_input("Ask Eliza (Boardroom):")
    if st.button("Ask Eliza"):
        eliza_res = f"Eliza: For '{eliza_input}', the board suggests focusing on mesh resilience and investor transparency. XMRT DAO's next move is global mesh partnerships."
        st.session_state.session_events.append(f"Eliza Boardroom: {eliza_input}")
        st.info(eliza_res)
    st.warning("Eliza Boardroom is a simulation for investor/exec Q&A.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="card"><h2>Session Profile & Tracking</h2>', unsafe_allow_html=True)
    st.write("Your current session profile (local only):")
    st.json(st.session_state.profile)
    st.write("Session events (track your clicks in this session):")
    st.json(st.session_state.session_events)
    if st.button("🔄 Start Over"):
        st.session_state.onboarded = False
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.write('<span style="color:#276ef1;font-weight:bold;">XMRT DAO on Meshnet</span> | All rights reserved | Contact: <a href="mailto:xmrtnet@gmail.com" style="color:#ff6600;">xmrtnet@gmail.com</a>', unsafe_allow_html=True)
