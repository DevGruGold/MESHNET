
import streamlit as st
import datetime

st.set_page_config(page_title="MESHNET Onboarding", layout="wide")

st.markdown("""
    <style>
        body { background-color: #f4f9fd; color: #222; font-family: 'Inter', 'Arial', sans-serif; }
        h1, h2, h3, h4, h5 { color: #006699; }
        .stButton > button {
            background-color: #006699;
            color: white;
            width: 100%;
            height: 50px;
            font-size: 20px;
            border-radius: 5px;
            margin-bottom: 8px;
        }
        .stTextInput > div > input, .stTextArea > div > textarea {
            font-size: 18px;
            border-radius: 8px;
            border: 1.5px solid #006699;
        }
        .onboarding-box {
            background: #e6f2ff;
            padding: 30px 24px 18px 24px;
            border-radius: 12px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.07);
            margin-bottom: 20px;
        }
        .profile-chip {
            display: inline-block;
            background: #d1e9fa;
            color: #006699;
            padding: 4px 18px;
            margin: 3px 3px 3px 0;
            border-radius: 18px;
            font-size: 16px;
            font-weight: 600;
        }
        @media (max-width: 700px) {
            .onboarding-box { padding: 14px 8px 10px 8px; }
            h1 { font-size: 24px; }
        }
    </style>
""", unsafe_allow_html=True)

if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "profile" not in st.session_state:
    st.session_state.profile = {}

if not st.session_state.onboarded:
    st.markdown('<div class="onboarding-box">', unsafe_allow_html=True)
    st.markdown("## Welcome to MESHNET")
    st.write("**XMRT Ecosystem’s Meshnet** is the easiest way to join, mine, or invest in the decentralized future of off-grid, agent-powered networks.")
    st.markdown("### Get Started")
    name = st.text_input("🧑 Your Name or Alias")
    role = st.selectbox("Your Mode", ["Mesh Miner", "Investor / Observer", "Just Curious"])
    mesh_alias = st.text_input("Mesh Handle (for node display)", max_chars=18)
    if role == "Mesh Miner":
        purpose = st.selectbox("Mining Purpose", ["Contribute connectivity", "Bridge data", "Run an agent", "Other"])
    else:
        purpose = "N/A"
    if st.button("🚀 Enter MESHNET"):
        st.session_state.onboarded = True
        st.session_state.profile = {
            "name": name,
            "role": role,
            "mesh_alias": mesh_alias,
            "purpose": purpose,
            "joined": str(datetime.datetime.now())
        }
    st.markdown("</div>", unsafe_allow_html=True)
    st.info("No login required. No data leaves your browser/session. All onboarding is instant and local.")
    st.stop()

st.markdown('<div style="background:#e6f2ff; padding:10px 20px 10px 20px; border-radius:8px; margin-bottom:18px;">', unsafe_allow_html=True)
cols = st.columns([2,2,6])
with cols[0]: st.markdown(f'<div class="profile-chip">👤 {st.session_state.profile.get("name","")}</div>', unsafe_allow_html=True)
with cols[1]: st.markdown(f'<div class="profile-chip">🔗 {st.session_state.profile.get("mesh_alias","")}</div>', unsafe_allow_html=True)
with cols[2]: st.markdown(f'<div class="profile-chip">🛠️ {st.session_state.profile.get("role","")}: {st.session_state.profile.get("purpose","")}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if "visit_count" not in st.session_state:
    st.session_state.visit_count = 1
else:
    st.session_state.visit_count += 1
if "session_events" not in st.session_state:
    st.session_state.session_events = []
st.session_state.session_events.append(f"Visited at step {st.session_state.visit_count}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Mesh Dashboard",
    "Agents & AI",
    "CashDapp",
    "Eliza Boardroom",
    "Session"
])

with tab1:
    st.markdown("### Mesh Miner Dashboard")
    st.metric("Active Nodes", 8, "+2 new in last hour")
    st.metric("Mesh Sessions (demo)", st.session_state.visit_count)
    st.write("Simulated mesh status: Node1 (active), Node2 (idle), Node3 (joining)...")
    if st.button("Simulate Mesh Message"):
        st.session_state.session_events.append("Mesh Message Sent")
        st.success("Mesh message sent! (simulated)")
    st.success("Mining enabled! (simulated)")

with tab2:
    st.markdown("### Agents, LangChain, Eliza, GPT-5 (Demo)")
    st.write("AI agents route, score, and automate mesh data (simulated).")
    ai_input = st.text_input("Ask an Agent or AI:")
    if st.button("Run AI Agent"):
        st.session_state.session_events.append(f"AI Agent Queried: {ai_input}")
        st.info("AI/Agent: 'XMRT mesh status is optimal. All agents running.'")
    st.write("Eliza Chatbot: Hello! How can I help with your mesh or investment questions?")

with tab3:
    st.markdown("### CashDapp – Crypto Payments Demo")
    st.write("Simulate sending, receiving, or bridging digital assets on mesh.")
    cash_amount = st.number_input("Amount to send", min_value=0.01, step=0.01)
    cash_to = st.text_input("Destination (mesh alias or wallet)")
    if st.button("Send Payment"):
        st.session_state.session_events.append(f"CashDapp: Sent {cash_amount} to {cash_to}")
        st.success(f"Payment of ${cash_amount} sent to {cash_to} (simulated)!")
    if st.button("Request Payment"):
        st.session_state.session_events.append(f"CashDapp: Requested {cash_amount} from {cash_to}")
        st.info(f"Payment request for ${cash_amount} sent to {cash_to} (simulated)!")
    st.write("Track your mesh payments, bridge to other chains, and manage digital assets. (All demo, no real money!)")

with tab4:
    st.markdown("### Eliza Executive Boardroom 🧑‍💼")
    st.write("Chat with Eliza, your AI board advisor. Ask about XMRT DAO, mesh growth, or investor strategy.")
    eliza_input = st.text_input("Ask Eliza (Boardroom):")
    if st.button("Ask Eliza"):
        eliza_res = f"Eliza: For '{eliza_input}', the board suggests focusing on mesh resilience and investor transparency. XMRT DAO's next move is global mesh partnerships."
        st.session_state.session_events.append(f"Eliza Boardroom: {eliza_input}")
        st.info(eliza_res)
    st.warning("Eliza Boardroom is a simulation for investor/exec Q&A.")

with tab5:
    st.markdown("### Session Profile & Tracking")
    st.write("Your current session profile (local only):")
    st.json(st.session_state.profile)
    st.write("Session events (track your clicks in this session):")
    st.json(st.session_state.session_events)
    if st.button("🔄 Start Over"):
        st.session_state.onboarded = False
        st.experimental_rerun()

st.markdown("---")
st.write("**Meshnet is a product of XMRT.io. No user data stored or transmitted.**")
