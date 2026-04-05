import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Intelligence Dashboard", layout="wide")

# -------------------------------
# PREMIUM DARK UI + FLOAT CARDS
# -------------------------------
st.markdown("""
<style>
body {
    background:#0f172a;
    color:white;
}

/* FLOATING CARD */
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

.metric-title {
    font-size: 16px;
    color: #9ca3af;
}

.metric-value {
    font-size: 30px;
    font-weight: bold;
}

/* BUTTON FIX */
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
# CLICKABLE FLOAT CARDS
# -------------------------------
if "metric" not in st.session_state:
    st.session_state.metric = None

def floating_card(title, value, key):
    if st.button("", key=key):
        st.session_state.metric = key

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("📊 Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    floating_card("Gini", f"{g:.3f}", "gini")
with col2:
    floating_card("HHI", f"{h:.3f}", "hhi")
with col3:
    floating_card("Entropy", f"{e:.3f}", "entropy")
with col4:
    floating_card("CDI", f"{cdi:.3f}", "cdi")

# -------------------------------
# POPUP EXPLANATION
# -------------------------------
if st.session_state.metric == "gini":
    st.info("📊 Gini → Measures token inequality. Lower = better decentralization.")
elif st.session_state.metric == "hhi":
    st.info("🏛️ HHI → Measures governance concentration. Lower = better.")
elif st.session_state.metric == "entropy":
    st.info("🔄 Entropy → Measures activity spread. Higher = better.")
elif st.session_state.metric == "cdi":
    st.success(f"🧠 CDI Score = {cdi:.3f}")

# -------------------------------
# CHARTS
# -------------------------------
st.subheader("📈 Analytics")

colA, colB = st.columns(2)

with colA:
    fig, ax = plt.subplots()
    ax.bar(["Gini","HHI","Entropy"], [g,h,e])
    st.pyplot(fig)

with colB:
    fig2, ax2 = plt.subplots()
    ax2.pie([g,h,e], labels=["Gini","HHI","Entropy"], autopct="%1.1f%%")
    st.pyplot(fig2)

# -------------------------------
# GRAPH INSIGHTS
# -------------------------------
st.subheader("📊 Graph Insights")

st.markdown("""
- Bar chart shows contribution strength  
- Pie chart shows proportional contribution  
- High entropy + lower governance = decentralization paradox
""")

# -------------------------------
# GPT AI (SAFE VERSION)
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
                "role": "user",
                "content": f"Explain decentralization with G={g:.2f}, H={h:.2f}, E={e:.2f}, CDI={cdi:.2f}"
            }]
        )
        st.write(response.choices[0].message.content)

    except Exception as err:
        st.error(f"API Error: {err}")

else:
    if not gpt_available:
        st.warning("⚠️ GPT not available (install openai & add API key)")
    elif cdi < 0.3:
        st.error("Highly Centralized")
    elif cdi < 0.6:
        st.warning("Moderately Decentralized")
    else:
        st.success("Highly Decentralized")

# -------------------------------
# FORMULA
# -------------------------------
st.subheader("📐 CDI Formula")

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
