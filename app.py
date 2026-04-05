import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Dashboard", layout="wide")

# -------------------------------
# PREMIUM UI CSS
# -------------------------------
st.markdown("""
<style>
body {
    background:#0f172a;
    color:white;
}

.card {
    background:rgba(255,255,255,0.08);
    backdrop-filter:blur(12px);
    border-radius:20px;
    padding:20px;
    text-align:center;
    transition:0.3s;
}
.card:hover {
    transform:translateY(-8px);
}

button {
    width:100%;
    border-radius:12px !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("🧠 CDI Intelligence Dashboard")

# -------------------------------
# DATA INPUT
# -------------------------------
st.sidebar.header("📂 Data Input")

mode = st.sidebar.radio("Input Type", ["Sample Data", "Upload CSV"])
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
# VALIDATION
# -------------------------------
if not {"tokens","votes","transactions"}.issubset(df.columns):
    st.error("CSV must contain: tokens, votes, transactions")
    st.stop()

st.subheader("📊 Dataset")
st.dataframe(df, use_container_width=True)

# -------------------------------
# FUNCTIONS
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
# CALCULATIONS
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

def card(title, value, key):
    if st.button(f"{title}\n{value}", key=key):
        st.session_state.metric = key

st.subheader("📊 Metrics")

c1,c2,c3,c4 = st.columns(4)

with c1: card("Gini", f"{g:.3f}", "gini")
with c2: card("HHI", f"{h:.3f}", "hhi")
with c3: card("Entropy", f"{e:.3f}", "entropy")
with c4: card("CDI", f"{cdi:.3f}", "cdi")

# -------------------------------
# POPUP EXPLANATION
# -------------------------------
if st.session_state.metric == "gini":
    st.info("📊 Gini measures inequality. Lower = better decentralization.")
elif st.session_state.metric == "hhi":
    st.info("🏛️ HHI measures governance concentration. Lower = better.")
elif st.session_state.metric == "entropy":
    st.info("🔄 Entropy measures activity spread. Higher = better.")
elif st.session_state.metric == "cdi":
    st.success(f"🧠 CDI Score = {cdi:.3f}")

# -------------------------------
# CHARTS
# -------------------------------
st.subheader("📈 Charts")

col1,col2 = st.columns(2)

with col1:
    fig,ax = plt.subplots()
    ax.bar(["Gini","HHI","Entropy"],[g,h,e])
    st.pyplot(fig)

with col2:
    fig2,ax2 = plt.subplots()
    ax2.pie([g,h,e],labels=["Gini","HHI","Entropy"],autopct="%1.1f%%")
    st.pyplot(fig2)

# -------------------------------
# GRAPH EXPLANATION
# -------------------------------
st.subheader("📊 Graph Insights")

st.markdown("""
- Bar chart shows contribution strength  
- Pie chart shows proportion distribution  
- High entropy + low governance = decentralization paradox
""")

# -------------------------------
# SAFE GPT HANDLING
# -------------------------------
st.subheader("🤖 AI Explanation")

use_gpt = st.toggle("Use GPT AI", False)

try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gpt_available = True
except:
    gpt_available = False

if use_gpt and gpt_available:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{
                "role":"user",
                "content":f"Explain CDI with G={g:.2f}, H={h:.2f}, E={e:.2f}, CDI={cdi:.2f}"
            }]
        )
        st.write(response["choices"][0]["message"]["content"])
    except:
        st.error("API error")
else:
    if cdi < 0.3:
        st.error("Highly Centralized")
    elif cdi < 0.6:
        st.warning("Moderately Decentralized")
    else:
        st.success("Highly Decentralized")

# -------------------------------
# FORMULA SECTION
# -------------------------------
st.subheader("📐 Formula")

st.latex(r"CDI = \frac{G + H + E}{3}")

st.markdown("""
Where:
- G = (1 - Gini)
- H = (1 - normalized HHI)
- E = normalized entropy
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
