
import streamlit as st
import datetime
import gspread
from google.auth import default
from gspread_dataframe import set_with_dataframe
import pandas as pd
import yagmail

creds, _ = default()
gc = gspread.authorize(creds)

SHEET_NAME = "XMRT_Mining_Sessions"
try:
    sh = gc.open(SHEET_NAME)
except gspread.SpreadsheetNotFound:
    sh = gc.create(SHEET_NAME)
    worksheet = sh.get_worksheet(0)
    worksheet.append_row(['timestamp', 'email', 'session_id', 'mesh_alias', 'mining_purpose', 'screenshot_url'])
worksheet = sh.get_worksheet(0)

try:
    yag = yagmail.SMTP('me')
except:
    yag = None

st.set_page_config(page_title="XMRT DAO Mesh Mining Portal", layout="wide")
st.markdown('<h1 style="color:#1d3557;">XMRT DAO Mesh Mining Portal</h1>', unsafe_allow_html=True)
st.write("Register your mining session below. You'll receive a confirmation email and can check your mining status any time.")
tab1, tab2, tab3 = st.tabs(["🚦 Register Mining Session", "🔎 Check Mining Status", "About/Contact"])

with tab1:
    st.header("Register Mining Session")
    email = st.text_input("Your Email", help="Used for confirmations")
    mesh_alias = st.text_input("Mesh Alias / Node ID")
    mining_purpose = st.selectbox("Mining Purpose", ["Connectivity", "Bridge Data", "Run Agent", "Other"])
    session_id = st.text_input("Unique Session ID", help="From your Meshtastic device or mining dashboard")
    screenshot = st.file_uploader("Upload Screenshot (optional)", type=["png", "jpg", "jpeg"])
    screenshot_url = ""
    if screenshot:
        with open(f"/tmp/{session_id}_screenshot.png", "wb") as f:
            f.write(screenshot.read())
        screenshot_url = f"uploaded:{session_id}_screenshot.png"
    if st.button("Register Session"):
        if not email or not mesh_alias or not session_id:
            st.error("Please fill in all required fields!")
        else:
            timestamp = str(datetime.datetime.now())
            worksheet.append_row([timestamp, email, session_id, mesh_alias, mining_purpose, screenshot_url])
            if yag:
                yag.send(
                    to=email,
                    subject=f"XMRT DAO Mining Session Confirmation for {session_id}",
                    contents=f"Thank you for registering your mining session!\n\nSession ID: {session_id}\nMesh Alias: {mesh_alias}\nPurpose: {mining_purpose}\n\nKeep mining and check your status at https://xmrtdao.streamlit.app/"
                )
                st.success(f"Session registered! Confirmation sent to {email}.")
            else:
                st.warning("Session registered, but confirmation email not sent (Gmail not setup in this environment).")

with tab2:
    st.header("Check Mining Status")
    lookup = st.text_input("Enter your Email or Session ID to check status:")
    if st.button("Check Status"):
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        if lookup:
            matches = df[(df['email'] == lookup) | (df['session_id'] == lookup)]
            if not matches.empty:
                st.success(f"Found {len(matches)} session(s):")
                st.dataframe(matches)
            else:
                st.warning("No mining sessions found for that email or session ID.")
        else:
            st.info("Please enter an email or session ID.")

with tab3:
    st.header("About / Contact")
    st.write("XMRT DAO Meshnet is a real, live mining pool for decentralized mesh mining with Meshtastic.")
    st.write("**Contact:** [xmrtnet@gmail.com](mailto:xmrtnet@gmail.com)")

st.markdown("---")
st.write("All mining activity is tracked live. Your privacy is important—no data shared outside XMRT DAO.")
