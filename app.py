import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Intelligence Dashboard", layout="wide")

# -------------------------------
# PREMIUM UI
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
    transition: all 0.4s ease;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    cursor: pointer;
}

.metric-card:hover {
    transform: translateY(-12px) scale(1.05);
    box-shadow: 0 20px 50px rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 CDI Intelligence Dashboard")

# -------------------------------
# FETCH UNISWAP DATA
# -------------------------------
def fetch_uniswap_data():
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

    query = """
    {
      pools(first: 10, orderBy: totalValueLockedUSD, orderDirection: desc) {
        totalValueLockedUSD
        volumeUSD
      }
    }
    """

    try:
        res = requests.post(url, json={'query': query})
        data = res.json()

        tvl = [float(p["totalValueLockedUSD"]) for p in data["data"]["pools"]]
        volume = [float(p["volumeUSD"]) for p in data["data"]["pools"]]

        return tvl, volume
    except:
        return None, None

# -------------------------------
# INPUT
# -------------------------------
st.sidebar.header("📂 Data Source")

mode = st.sidebar.radio("Choose", [
    "Sample Data",
    "Upload CSV",
    "Live Uniswap Data"
])

file = None
if mode == "Upload CSV":
    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# -------------------------------
# DATA LOADING
# -------------------------------
if mode == "Upload CSV" and file:
    df = pd.read_csv(file)

elif mode == "Live Uniswap Data":
    tvl, volume = fetch_uniswap_data()

    if tvl:
        df = pd.DataFrame({
            "tokens": tvl,
            "votes": np.random.randint(50, 500, len(tvl)),
            "transactions": volume
        })
        st.success("🌐 Using live Uniswap data")
    else:
        st.error("Failed to fetch data")
        st.stop()

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
    p = x/np.sum(x) if np.sum(x)!=0 else x
    return -np.sum(p*np.log2(p+1e-9))

# -------------------------------
# CALCULATE CDI
# -------------------------------
tokens = df["tokens"].values
votes = df["votes"].values
tx = df["transactions"].values

g = 1 - gini(tokens)
h = 1 - (hhi(votes)/10000)
e = entropy(tx)/np.log2(len(tx))
cdi = (g+h+e)/3

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
    st.info("Gini → inequality (lower is better)")
elif st.session_state.metric == "hhi":
    st.info("HHI → governance concentration")
elif st.session_state.metric == "entropy":
    st.info("Entropy → activity diversity")
elif st.session_state.metric == "cdi":
    st.success(f"CDI Score = {cdi:.3f}")

# -------------------------------
# PLOTLY CHARTS
# -------------------------------
st.subheader("📈 Interactive Analytics")

chart_df = pd.DataFrame({
    "Metric":["Gini","HHI","Entropy"],
    "Value":[g,h,e]
})

fig_bar = px.bar(chart_df, x="Metric", y="Value", color="Metric", text="Value")
fig_bar.update_layout(transition_duration=800)

fig_pie = px.pie(chart_df, names="Metric", values="Value")

st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------
# GRAPH INSIGHTS
# -------------------------------
st.subheader("📊 Insights")

st.markdown("""
- Bar chart shows strength of each decentralization component  
- Pie chart shows proportional contribution  
- High entropy + lower governance → decentralization paradox
""")

# -------------------------------
# GPT AI
# -------------------------------
st.subheader("🤖 AI Explanation")

use_gpt = st.toggle("Use GPT AI", False)

gpt_available = False
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    gpt_available = True
except:
    pass

if use_gpt and gpt_available:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role":"user",
                "content":f"Explain CDI with G={g:.2f}, H={h:.2f}, E={e:.2f}, CDI={cdi:.2f}"
            }]
        )
        st.write(response.choices[0].message.content)
    except Exception as e:
        st.error(f"API Error: {e}")

else:
    if not gpt_available:
        st.warning("GPT not available")
    elif cdi < 0.3:
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

st.markdown("""
G = ownership decentralization  
H = governance decentralization  
E = usage decentralization  
""")

# -------------------------------
# DOWNLOAD
# -------------------------------
st.download_button(
    "⬇️ Download Results",
    pd.DataFrame({
        "Metric":["Gini","HHI","Entropy","CDI"],
        "Value":[g,h,e,cdi]
    }).to_csv(index=False),
    "cdi.csv"
)
