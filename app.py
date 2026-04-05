import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json

# -------------------------------
# CONFIG
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
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 20px;
    text-align:center;
    transition:0.3s;
}
.metric-card:hover {
    transform:translateY(-8px) scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 CDI Intelligence Dashboard")

# -------------------------------
# INPUT
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
# 🔥 FIX DICT ERROR
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
# VALIDATION
# -------------------------------
if not {"tokens","votes","transactions"}.issubset(df.columns):
    st.error("CSV must contain tokens, votes, transactions")
    st.stop()

st.subheader("📊 Dataset")
st.dataframe(df)

# -------------------------------
# METRICS FUNCTIONS
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

# -------------------------------
# CALCULATE
# -------------------------------
g = 1 - gini(df["tokens"])
h = 1 - (hhi(df["votes"])/10000)
e = entropy(df["transactions"]) / np.log2(len(df))
cdi = (g+h+e)/3

# -------------------------------
# FLOATING CARDS
# -------------------------------
st.subheader("📊 Metrics")

col1,col2,col3,col4 = st.columns(4)

col1.markdown(f"<div class='metric-card'>Gini<br><b>{g:.3f}</b></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'>HHI<br><b>{h:.3f}</b></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'>Entropy<br><b>{e:.3f}</b></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'>CDI<br><b>{cdi:.3f}</b></div>", unsafe_allow_html=True)

# -------------------------------
# CHARTS
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
# MULTI PROTOCOL
# -------------------------------
st.subheader("📊 Multi-Protocol Comparison")

protocols = ["Uniswap","Aave","Curve"]
results = []

for p in protocols:
    tokens = np.random.uniform(1e6,1e7,10)
    votes = np.random.randint(50,500,10)
    tx = np.random.uniform(1e5,1e6,10)

    g_ = 1 - gini(tokens)
    h_ = 1 - (hhi(votes)/10000)
    e_ = entropy(tx)/np.log2(len(tx))
    c_ = (g_+h_+e_)/3

    results.append([p,c_])

comp_df = pd.DataFrame(results, columns=["Protocol","CDI"])

fig_comp = px.bar(comp_df, x="Protocol", y="CDI", color="Protocol")
st.plotly_chart(fig_comp, use_container_width=True)

# -------------------------------
# TIME SERIES
# -------------------------------
st.subheader("📈 CDI Over Time")

dates = pd.date_range(end=pd.Timestamp.today(), periods=12)

ts_df = pd.DataFrame({
    "Date": dates,
    "CDI": np.random.uniform(cdi-0.05, cdi+0.05, len(dates))
})

fig_ts = px.line(ts_df, x="Date", y="CDI", markers=True)
st.plotly_chart(fig_ts, use_container_width=True)

# -------------------------------
# AI INSIGHTS (SAFE)
# -------------------------------
st.subheader("🤖 AI Insights")

if cdi < 0.3:
    st.error("🔴 Highly Centralized")
elif cdi < 0.6:
    st.warning("🟡 Moderately Decentralized")
else:
    st.success("🟢 Highly Decentralized")

st.markdown(f"""
- Ownership Score: {g:.2f}  
- Governance Score: {h:.2f}  
- Usage Score: {e:.2f}  

👉 Overall system shows **{'strong' if cdi>0.6 else 'moderate' if cdi>0.3 else 'weak'} decentralization**
""")

# -------------------------------
# FORMULA
# -------------------------------
st.subheader("📐 Formula")

st.latex(r"CDI = \frac{G + H + E}{3}")
