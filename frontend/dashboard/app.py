import streamlit as st
import datetime
import pandas as pd
import random

st.set_page_config(page_title="XMRT DAO - Corporate Meshnet", layout="wide")

### --- Corporate Fintech Styling ---
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
    margin: 3px 6px 0;
    border-radius: 20px;
    font-size: 17px;
    font-weight: 600;
}
.card {
    background: #2d2d2d;
    border: 1.5px solid #00ff88;
    box-shadow: 0 3px 16px #00ff8822;
    padding: 26px 22px 18px 22px;
    border-radius: 14px;
    margin-bottom: 26px;
}
.orange { color: #00ff88; font-weight: bold; }
.interaction-btn {
    background: linear-gradient(90deg, #00ff88 0%, #00cc66 100%);
    color: #1a1a1a !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #2d2d2d;
    border-radius: 10px 10px 0 0;
    padding: 10px 18px;
}
.stTabs [aria-selected="true"] {
    background: #1a1a1a !important;
    border: 1.5px solid #00ff88;
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
    box-shadow: 0 2px #00ff8833;
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


### --- Load Data ---


# Function to load data from JSON
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_data():
    try:
        df = pd.read_json('meshnet_scoreboard.json')
        # Ensure 'last_update' is datetime objects for proper sorting
        df['last_update'] = pd.to_datetime(df['last_update'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

df = load_data()

# Check if the DataFrame is empty
if df.empty:
    st.warning("No data to display. Please ensure 'meshnet_scoreboard.json' is correctly populated.")
    st.stop() # Stop the app if no data


### --- Sidebar ---

st.sidebar.header("XMRT DAO Corporate Meshnet")

# Filter by Miner ID
miner_ids = sorted(df['miner_id'].unique())
selected_miner_id = st.sidebar.selectbox("Select Miner ID", ['All'] + miner_ids)

# Filter by Time Range
time_range_options = {
    "Last 24 Hours": datetime.datetime.now() - datetime.timedelta(hours=24),
    "Last 7 Days": datetime.datetime.now() - datetime.timedelta(days=7),
    "Last 30 Days": datetime.datetime.now() - datetime.timedelta(days=30),
    "All Time": datetime.datetime.min # Represents no time filter
}

selected_time_range = st.sidebar.selectbox("Select Time Range", list(time_range_options.keys()))

# Apply filters
filtered_df = df.copy()

if selected_miner_id != 'All':
    filtered_df = filtered_df[filtered_df['miner_id'] == selected_miner_id]

if selected_time_range != "All Time":
    start_time = time_range_options[selected_time_range]
    filtered_df = filtered_df[filtered_df['last_update'] >= start_time]


### --- Main Dashboard ---

st.title("Corporate Meshnet Dashboard")

# Display Key Metrics
st.subheader("Key Metrics")

if not filtered_df.empty:
    total_hashes = filtered_df['hashes_per_second'].sum()
    avg_temp = filtered_df['temperature'].mean()
    total_miners = filtered_df['miner_id'].nunique()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Hashes/Second", value=f"{total_hashes:,.2f}")
    with col2:
        st.metric(label="Average Temperature (°C)", value=f"{avg_temp:,.2f}")
    with col3:
        st.metric(label="Total Active Miners", value=total_miners)
else:
    st.info("No data for the selected filters.")


# Leaderboard
st.subheader("Miner Leaderboard")

if not filtered_df.empty:
    # Aggregate data for leaderboard: sum hashes and get last reported temp for each miner
    leaderboard_df = filtered_df.groupby('miner_id').agg(
        total_hashes=('hashes_per_second', 'sum'),
        last_temp=('temperature', lambda x: x.iloc[-1]) # Get the last reported temperature
    ).sort_values(by='total_hashes', ascending=False).reset_index()

    # Display leaderboard with styling
    for index, row in leaderboard_df.iterrows():
        rank = index + 1
        st.markdown(f"""
        <div class="miner-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <span class="leaderboard-rank">#{rank}</span>
                    <span style="font-size: 1.2em; font-weight: bold;">{row['miner_id']}</span>
                </div>
                <span class="orange">{row['total_hashes']:,.2f} H/s</span>
            </div>
            <div style="text-align: right; font-size: 0.9em; color: #aaaaaa;">
                Last Temp: {row['last_temp']:.1f}°C
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No miners to display in the leaderboard.")


# Historical Performance Chart
st.subheader("Historical Performance")

if not filtered_df.empty:
    # Group by date and sum hashes per second
    daily_performance = filtered_df.set_index('last_update').resample('D')['hashes_per_second'].sum().reset_index()
    daily_performance.columns = ['Date', 'Total Hashes/Second']

    st.line_chart(daily_performance.set_index('Date'))
else:
    st.info("No historical data for the selected filters.")


# Miner Details (expandable)
st.subheader("Miner Details")

if not filtered_df.empty:
    for miner_id in filtered_df['miner_id'].unique():
        with st.expander(f"Details for Miner ID: {miner_id}"):
            miner_df = filtered_df[filtered_df['miner_id'] == miner_id].sort_values(by='last_update', ascending=False)
            st.write(miner_df[['last_update', 'hashes_per_second', 'temperature', 'fan_speed', 'power_consumption']])
else:
    st.info("No miner details to display.")


### --- Footer ---
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #1a1a1a;
    color: #e0e0e0;
    text-align: center;
    padding: 10px;
    font-size: 0.9em;
    border-top: 1px solid #00ff88;
}
.footer a {
    color: #00ff88;
    text-decoration: none;
}
</style>
<div class="footer">
    <p>Developed by <a href="mailto:xmrtsolutions@gmail.com">DevGruGold</a> | &copy; 2024 XMRT DAO. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)


