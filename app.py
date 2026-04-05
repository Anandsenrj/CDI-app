import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import requests

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Dashboard", layout="wide")

# -------------------------------
# UI STYLE
# -------------------------------
st.markdown("""
<style>
body { background:#0f172a; color:white; }

.metric-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    transition: 0.4s;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    cursor:pointer;
}
.metric-card:hover {
    transform: translateY(-10px) scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 CDI Intelligence Dashboard")

# -------------------------------
# DATA FETCH (COINGECKO)
# -------------------------------
def fetch_real_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/uniswap"
        data = requests.get(url).json()

        market = data["market_data"]

        tokens = [market["total_value_locked"] or 1000000] * 7
        transactions = [market["total_volume"]["usd"] / (i+1) for i in range(7)]
        votes = np.random.randint(50, 300, 7)

        return pd.DataFrame({
            "tokens": tokens,
            "votes": votes,
            "transactions": transactions
        })

    except:
        return None

# -------------------------------
# INPUT
# -------------------------------
mode = st.sidebar.radio("Data Source", [
    "Sample Data",
    "Upload CSV",
    "Live DeFi Data"
])

file = None
if mode == "Upload CSV":
    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# -------------------------------
# LOAD DATA
# -------------------------------
if mode == "Upload CSV" and file:
    df = pd.read_csv(file)

elif mode == "Live DeFi Data":
    df = fetch_real_data()

    if df is None:
        st.error("⚠️ Failed to fetch live data")
        st.stop()
    else:
        st.success("🌐 Live data loaded (CoinGecko)")

else:
    df = pd.DataFrame({
        "tokens":[5000,4200,3900,3500,3000,2500,2000],
        "votes":[300,250,200,180,160,140,120],
        "transactions":[1200,1100,1050,980,900,850,780]
    })

# -------------------------------
# VALIDATION
# -------------------------------
if not {"tokens","votes","transactions"}.issubset(df.columns):
    st.error("CSV must contain tokens, votes, transactions")
    st.stop()

st.subheader("📊 Dataset")
st.dataframe(df)

# -------------------------------
# METRIC FUNCTIONS
# -------------------------------
def gini(x):
    x = np.sort(x)
    n = len(x)
    return (2*np.sum((np.arange(1,n+1)*x)))/(n*np.sum(x))-(n+1)/n if np.sum(x)!=0 else 0

def hhi(x):
    return np.sum((x/np.sum(x))**2)*10000 if np.sum(x)!=0 else 0

def entropy(x):
    p = x/np.sum(x)
    return -np.sum(p*np.log2(p+1e-9))

# -------------------------------
# CALCULATE
# -------------------------------
g = 1 - gini(df["tokens"])
h = 1 - (hhi(df["votes"]) / 10000)
e = entropy(df["transactions"]) / np.log2(len(df))
cdi = (g + h + e) / 3

# -------------------------------
# CLICKABLE CARDS
# -------------------------------
if "metric" not in st.session_state:
    st.session_state.metric = None

def card(title, val, key):
    if st.button(title, key=key):
        st.session_state.metric = key

    st.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{val}</h2>
    </div>
    """, unsafe_allow_html=True)

st.subheader("📊 Metrics")

c1,c2,c3,c4 = st.columns(4)

with c1: card("Gini", f"{g:.3f}", "gini")
with c2: card("HHI", f"{h:.3f}", "hhi")
with c3: card("Entropy", f"{e:.3f}", "entropy")
with c4: card("CDI", f"{cdi:.3f}", "cdi")

# -------------------------------
# POPUP INFO
# -------------------------------
if st.session_state.metric == "gini":
    st.info("Gini → inequality in token distribution")
elif st.session_state.metric == "hhi":
    st.info("HHI → governance concentration")
elif st.session_state.metric == "entropy":
    st.info("Entropy → transaction diversity")
elif st.session_state.metric == "cdi":
    st.success(f"CDI Score = {cdi:.3f}")

# -------------------------------
# PLOTLY CHARTS
# -------------------------------
st.subheader("📈 Interactive Charts")

chart_df = pd.DataFrame({
    "Metric":["Gini","HHI","Entropy"],
    "Value":[g,h,e]
})

fig1 = px.bar(chart_df, x="Metric", y="Value", color="Metric", text="Value")
fig1.update_layout(transition_duration=800)

fig2 = px.pie(chart_df, names="Metric", values="Value")

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# AI INSIGHTS (NO API)
# -------------------------------
st.subheader("🤖 AI Explanation")

if cdi < 0.3:
    st.error("🔴 Highly centralized system")
elif cdi < 0.6:
    st.warning("🟡 Moderately decentralized system")
else:
    st.success("🟢 Highly decentralized system")

st.markdown(f"""
- Ownership Score: {g:.2f}  
- Governance Score: {h:.2f}  
- Usage Score: {e:.2f}  

👉 System shows **{'strong' if cdi>0.6 else 'moderate' if cdi>0.3 else 'low'} decentralization**
""")

# -------------------------------
# FORMULA
# -------------------------------
st.subheader("📐 Formula")

st.latex(r"CDI = \frac{G + H + E}{3}")
