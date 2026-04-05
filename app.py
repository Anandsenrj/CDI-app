import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Dashboard", layout="wide")

# -------------------------------
# DARK MODE
# -------------------------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode", True)

bg = "#0f172a" if dark_mode else "#f8fafc"
text = "white" if dark_mode else "black"
card = "rgba(255,255,255,0.08)" if dark_mode else "rgba(255,255,255,0.6)"

st.markdown(f"""
<style>
body {{ background:{bg}; color:{text}; }}
.card {{
    background:{card};
    backdrop-filter:blur(12px);
    border-radius:20px;
    padding:20px;
    transition:0.3s;
}}
.card:hover {{
    transform:translateY(-6px);
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("🧠 CDI Intelligence Dashboard")

# -------------------------------
# INPUT SECTION (FIXED)
# -------------------------------
st.sidebar.header("📂 Data Input")

mode = st.sidebar.radio("Select Input Type", ["Sample Data", "Upload CSV"])

uploaded_file = None
if mode == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# -------------------------------
# DATA LOAD (FIXED LOGIC)
# -------------------------------
if mode == "Upload CSV" and uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
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
    if np.sum(x) == 0:
        return 0
    return (2*np.sum((np.arange(1,n+1)*x)))/(n*np.sum(x)) - (n+1)/n

def hhi(x):
    if np.sum(x)==0: return 0
    s = x/np.sum(x)
    return np.sum(s**2)*10000

def entropy(x):
    if np.sum(x)==0: return 0
    p = x/np.sum(x)
    return -np.sum(p*np.log2(p+1e-9))

# -------------------------------
# CALCULATE
# -------------------------------
tokens = np.array(df["tokens"])
votes = np.array(df["votes"])
tx = np.array(df["transactions"])

g = 1 - gini(tokens)
h = 1 - (hhi(votes)/10000)
e = entropy(tx)/np.log2(len(tx))
cdi = (g+h+e)/3

# -------------------------------
# METRICS
# -------------------------------
st.subheader("📊 Metrics")

c1,c2,c3,c4 = st.columns(4)

def card_ui(title,val):
    st.markdown(f"""
    <div class="card">
    <h4>{title}</h4>
    <h2>{val}</h2>
    </div>
    """, unsafe_allow_html=True)

with c1: card_ui("Gini", f"{g:.3f}")
with c2: card_ui("HHI", f"{h:.3f}")
with c3: card_ui("Entropy", f"{e:.3f}")
with c4: card_ui("CDI", f"{cdi:.3f}")

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
# AI INSIGHTS (ALWAYS VISIBLE)
# -------------------------------
st.subheader("🧠 AI Insights")

insights = []

if g < 0.4:
    insights.append("⚠️ Ownership is concentrated (whales dominate)")
else:
    insights.append("✅ Ownership distribution is fair")

if h < 0.4:
    insights.append("⚠️ Governance is centralized")
else:
    insights.append("✅ Governance is decentralized")

if e > 0.6:
    insights.append("✅ Strong network activity")
else:
    insights.append("⚠️ Low user participation")

if cdi < 0.3:
    level = "Highly Centralized"
elif cdi < 0.6:
    level = "Moderately Decentralized"
else:
    level = "Highly Decentralized"

st.markdown(f"### 📊 Overall: {level}")

for i in insights:
    st.write(i)

# -------------------------------
# RECOMMENDATIONS
# -------------------------------
st.subheader("🚀 Recommendations")

if g < 0.4:
    st.write("👉 Improve token distribution (airdrops, staking)")
if h < 0.4:
    st.write("👉 Improve governance decentralization")
if e < 0.5:
    st.write("👉 Increase user engagement")

# -------------------------------
# DOWNLOAD
# -------------------------------
result = pd.DataFrame({
    "Metric":["Gini","HHI","Entropy","CDI"],
    "Value":[g,h,e,cdi]
})

st.download_button("⬇️ Download Results", result.to_csv(index=False), "cdi.csv")
