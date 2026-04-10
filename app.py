import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import json
import time

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Pro Dashboard", layout="wide")

# -------------------------------
# AUTO REFRESH (SAFE)
# -------------------------------

# -------------------------------
# UI STYLE (UPGRADED)
# -------------------------------
st.markdown("""
<style>
body { background:#0f172a; color:white; }

.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
    backdrop-filter: blur(15px);
    border-radius: 15px;
    padding: 20px;
    text-align:center;
    transition:0.3s;
    box-shadow:0 8px 25px rgba(0,0,0,0.3);
}
.metric-card:hover {
    transform:translateY(-10px) scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 CDI Intelligence Dashboard PRO")

# -------------------------------
# FETCH LIVE PRICES
# -------------------------------
def fetch_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,uniswap&vs_currencies=usd"
        data = requests.get(url).json()
        return {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"],
            "UNI": data["uniswap"]["usd"]
        }
    except:
        return None

prices = fetch_prices()

# -------------------------------
# LIVE PRICE CARDS
# -------------------------------
st.subheader("💰 Live Crypto Prices")

c1,c2,c3 = st.columns(3)

if prices:
    c1.markdown(f"<div class='metric-card'>BTC<br><b>${prices['BTC']}</b></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'>ETH<br><b>${prices['ETH']}</b></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'>UNI<br><b>${prices['UNI']}</b></div>", unsafe_allow_html=True)
else:
    st.error("Failed to fetch live prices")

# -------------------------------
# DATA INPUT
# -------------------------------
mode = st.sidebar.radio("Data Source", ["Sample Data", "Upload CSV"])

file = None
if mode == "Upload CSV":
    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
else:
    df = pd.DataFrame({
        "tokens":[5000,4200,3900,3500,3000,2500,2000],
        "votes":[300,250,200,180,160,140,120],
        "transactions":[1200,1100,1050,980,900,850,780]
    })

# -------------------------------
# FIX DICT ERROR
# -------------------------------
def extract_usd(x):
    if isinstance(x, dict):
        return x.get("usd", 0)
    if isinstance(x, str) and "usd" in x:
        try:
            return json.loads(x)["usd"]
        except:
            return 0
    return x

df["tokens"] = df["tokens"].apply(extract_usd)

# -------------------------------
# METRICS
# -------------------------------
def gini(x):
    x = np.sort(x)
    n = len(x)
    return (2*np.sum((np.arange(1,n+1)*x)))/(n*np.sum(x))-(n+1)/n

def hhi(x):
    return np.sum((x/np.sum(x))**2)*10000

def entropy(x):
    p = x/np.sum(x)
    return -np.sum(p*np.log2(p+1e-9))

g = 1 - gini(df["tokens"])
h = 1 - (hhi(df["votes"])/10000)
e = entropy(df["transactions"]) / np.log2(len(df))
cdi = (g+h+e)/3

# -------------------------------
# CDI CARDS
# -------------------------------
st.subheader("📊 CDI Metrics")

col1,col2,col3,col4 = st.columns(4)

col1.markdown(f"<div class='metric-card'>Gini<br><b>{g:.3f}</b></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'>HHI<br><b>{h:.3f}</b></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'>Entropy<br><b>{e:.3f}</b></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'>CDI<br><b>{cdi:.3f}</b></div>", unsafe_allow_html=True)

# -------------------------------
# CHARTS
# -------------------------------
st.subheader("📈 Analytics")

chart_df = pd.DataFrame({
    "Metric":["Gini","HHI","Entropy"],
    "Value":[g,h,e]
})

fig = px.bar(chart_df, x="Metric", y="Value", color="Metric")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# AUTO REFRESH BUTTON
# -------------------------------
if st.button("🔄 Refresh Prices"):
    st.rerun()

# -------------------------------
# FORMULA
# -------------------------------
st.subheader("📐 Formula")

st.latex(r"CDI = \frac{G + H + E}{3}")
