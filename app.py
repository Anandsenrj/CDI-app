import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Trading Dashboard", layout="wide")

# -------------------------------
# AUTO REFRESH (SAFE)
# -------------------------------
st_autorefresh(interval=10000, key="refresh")

# -------------------------------
# UI STYLE
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
}
.metric-card:hover {
    transform:translateY(-10px) scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 CDI Trading Dashboard")

# -------------------------------
# LIVE PRICE + CHANGE
# -------------------------------
@st.cache_data(ttl=30)
def fetch_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency":"usd","ids":"bitcoin,ethereum,uniswap"}
    return requests.get(url, params=params).json()

def color(c): return "green" if c >= 0 else "red"

prices = fetch_prices()

st.subheader("💰 Live Crypto Prices")

if prices:
    cols = st.columns(3)
    for col, coin in zip(cols, prices):
        col.markdown(f"""
        <div class='metric-card'>
            <h3>{coin['symbol'].upper()}</h3>
            <h2>${coin['current_price']}</h2>
            <p style='color:{color(coin['price_change_percentage_24h'])}'>
                {coin['price_change_percentage_24h']:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------
# CANDLESTICK
# -------------------------------
def fetch_candles():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/ohlc"
    data = requests.get(url, params={"vs_currency":"usd","days":1}).json()
    df = pd.DataFrame(data, columns=["time","open","high","low","close"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

st.subheader("📊 Candlestick Chart")

try:
    df_c = fetch_candles()
    fig = go.Figure(data=[go.Candlestick(
        x=df_c['time'],
        open=df_c['open'],
        high=df_c['high'],
        low=df_c['low'],
        close=df_c['close']
    )])
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Chart unavailable")

# -------------------------------
# DATA INPUT
# -------------------------------
mode = st.sidebar.radio("Data Source", ["Sample Data", "Upload CSV"])
file = st.sidebar.file_uploader("Upload CSV", type=["csv"]) if mode=="Upload CSV" else None

if file:
    df = pd.read_csv(file)
else:
    df = pd.DataFrame({
        "tokens":[5000,4200,3900,3500,3000,2500,2000],
        "votes":[300,250,200,180,160,140,120],
        "transactions":[1200,1100,1050,980,900,850,780]
    })

# FIX dict
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
# CDI CALC
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
# METRICS
# -------------------------------
st.subheader("📊 CDI Metrics")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Gini", f"{g:.3f}")
c2.metric("HHI", f"{h:.3f}")
c3.metric("Entropy", f"{e:.3f}")
c4.metric("CDI", f"{cdi:.3f}")

# -------------------------------
# ANALYTICS
# -------------------------------
chart_df = pd.DataFrame({"Metric":["Gini","HHI","Entropy"],"Value":[g,h,e]})
st.plotly_chart(px.bar(chart_df,x="Metric",y="Value",color="Metric"), use_container_width=True)

# -------------------------------
# MULTI PROTOCOL
# -------------------------------
st.subheader("📊 Multi-Protocol Comparison")

protocols=["Uniswap","Aave","Curve"]
vals=[np.random.uniform(0.4,0.9) for _ in protocols]
st.plotly_chart(px.bar(x=protocols,y=vals,color=protocols), use_container_width=True)

# -------------------------------
# TIME SERIES
# -------------------------------
dates = pd.date_range(end=pd.Timestamp.today(), periods=12)
ts = pd.DataFrame({"Date":dates,"CDI":np.random.uniform(cdi-0.05,cdi+0.05,12)})
st.plotly_chart(px.line(ts,x="Date",y="CDI",markers=True), use_container_width=True)

# -------------------------------
# UNISWAP DATA
# -------------------------------
def fetch_uniswap():
    url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    query="""{ pools(first:5){volumeUSD totalValueLockedUSD}}"""
    try:
        res=requests.post(url,json={"query":query}).json()
        pools=res["data"]["pools"]
        vol=sum(float(p["volumeUSD"]) for p in pools)
        tvl=sum(float(p["totalValueLockedUSD"]) for p in pools)
        return vol,tvl
    except:
        return None,None

st.subheader("🌐 DeFi Analytics")

vol,tvl=fetch_uniswap()
if vol:
    st.metric("Volume", f"${int(vol):,}")
    st.metric("TVL", f"${int(tvl):,}")

# -------------------------------
# AI INSIGHTS
# -------------------------------
st.subheader("🤖 AI Insights")

if cdi<0.3:
    st.error("Highly Centralized")
elif cdi<0.6:
    st.warning("Moderate")
else:
    st.success("Highly Decentralized")

# -------------------------------
# FORMULA
# -------------------------------
st.latex(r"CDI = \frac{G + H + E}{3}")
