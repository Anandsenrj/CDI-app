import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="CDI Dashboard", layout="wide")

st.title("🧠 CDI Multi-Protocol Dashboard")

# -------------------------------
# FETCH DATA (SIMULATED REAL)
# -------------------------------
def fetch_protocol_data(name):
    base = {
        "Uniswap": 30000000,
        "Aave": 25000000,
        "Curve": 20000000
    }

    tokens = [base[name] / (i+1) for i in range(7)]
    votes = np.random.randint(100, 500, 7)
    transactions = [base[name] / (i+2) for i in range(7)]

    return pd.DataFrame({
        "tokens": tokens,
        "votes": votes,
        "transactions": transactions
    })

# -------------------------------
# SELECT PROTOCOL
# -------------------------------
protocol = st.sidebar.selectbox(
    "Select Protocol",
    ["Uniswap", "Aave", "Curve"]
)

df = fetch_protocol_data(protocol)

# -------------------------------
# FIX (DICT ISSUE)
# -------------------------------
if isinstance(df["tokens"].iloc[0], dict):
    df["tokens"] = df["tokens"].apply(lambda x: x.get("usd", 0))

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
h = 1 - (hhi(df["votes"]) / 10000)
e = entropy(df["transactions"]) / np.log2(len(df))
cdi = (g+h+e)/3

# -------------------------------
# SHOW METRICS
# -------------------------------
col1,col2,col3,col4 = st.columns(4)

col1.metric("Gini", round(g,3))
col2.metric("HHI", round(h,3))
col3.metric("Entropy", round(e,3))
col4.metric("CDI", round(cdi,3))

# -------------------------------
# MULTI-PROTOCOL COMPARISON
# -------------------------------
st.subheader("📊 Protocol Comparison")

protocols = ["Uniswap","Aave","Curve"]
results = []

for p in protocols:
    d = fetch_protocol_data(p)
    g_ = 1 - gini(d["tokens"])
    h_ = 1 - (hhi(d["votes"]) / 10000)
    e_ = entropy(d["transactions"]) / np.log2(len(d))
    c_ = (g_+h_+e_)/3

    results.append([p, g_, h_, e_, c_])

comp_df = pd.DataFrame(results, columns=["Protocol","Gini","HHI","Entropy","CDI"])

fig_comp = px.bar(comp_df, x="Protocol", y="CDI", color="Protocol", title="CDI Comparison")
st.plotly_chart(fig_comp, use_container_width=True)

# -------------------------------
# TIME SERIES (SIMULATED)
# -------------------------------
st.subheader("📈 Time-Series Analysis")

days = pd.date_range(end=pd.Timestamp.today(), periods=10)

ts_data = pd.DataFrame({
    "Date": days,
    "CDI": np.random.uniform(cdi-0.05, cdi+0.05, len(days))
})

fig_ts = px.line(ts_data, x="Date", y="CDI", markers=True, title="CDI Over Time")
st.plotly_chart(fig_ts, use_container_width=True)

# -------------------------------
# INSIGHTS
# -------------------------------
st.subheader("🤖 Insights")

if cdi < 0.3:
    st.error("Highly Centralized")
elif cdi < 0.6:
    st.warning("Moderately Decentralized")
else:
    st.success("Highly Decentralized")

# -------------------------------
# FORMULA
# -------------------------------
st.subheader("📐 Formula")

st.latex(r"CDI = \frac{G + H + E}{3}")
