import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Intelligence", layout="wide")

# -------------------------------
# PREMIUM DARK UI (NO TOGGLE)
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
    transition:0.3s;
    position:relative;
}

.card:hover {
    transform:translateY(-8px) scale(1.03);
}

/* TOOLTIP */
.tooltip {
    visibility:hidden;
    background:#111;
    color:#fff;
    padding:10px;
    border-radius:8px;
    position:absolute;
    bottom:110%;
    left:50%;
    transform:translateX(-50%);
    width:220px;
    font-size:13px;
}

.card:hover .tooltip {
    visibility:visible;
}

/* FADE */
.fade {
    animation:fadeIn 1s ease-in;
}
@keyframes fadeIn {
    from {opacity:0;}
    to {opacity:1;}
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.markdown("<h1 class='fade'>🧠 CDI Intelligence Dashboard</h1>", unsafe_allow_html=True)

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
# DATA INPUT
# -------------------------------
st.sidebar.header("📂 Data Input")

mode = st.sidebar.radio("Input", ["Sample", "Upload CSV"])

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
# CALCULATE
# -------------------------------
g = 1 - gini(df["tokens"].values)
h = 1 - (hhi(df["votes"].values)/10000)
e = entropy(df["transactions"].values)/np.log2(len(df))
cdi = (g+h+e)/3

# -------------------------------
# METRIC CARDS + TOOLTIP
# -------------------------------
st.subheader("📊 Metrics")

cols = st.columns(4)

def card(title,val,desc):
    st.markdown(f"""
    <div class="card fade">
        <h4>{title}</h4>
        <h2>{val}</h2>
        <div class="tooltip">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

with cols[0]:
    card("Gini",f"{g:.3f}","Measures token inequality (lower = better)")
with cols[1]:
    card("HHI",f"{h:.3f}","Measures governance concentration")
with cols[2]:
    card("Entropy",f"{e:.3f}","Measures activity distribution")
with cols[3]:
    card("CDI",f"{cdi:.3f}","Overall decentralization score")

# -------------------------------
# CHARTS
# -------------------------------
st.subheader("📈 Analytics")

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

st.markdown(f"""
- The **bar chart** shows relative strength of decentralization factors.  
- Higher bars = stronger decentralization contribution.

- The **pie chart** shows proportional contribution:
  - Entropy dominates → strong user activity  
  - Lower Gini/HHI → ownership/governance imbalance  

👉 This pattern suggests **Decentralization Paradox**:
High usage but centralized control.
""")

# -------------------------------
# GPT AI INSIGHTS
# -------------------------------
st.subheader("🤖 AI Explanation")

use_gpt = st.toggle("Use GPT AI (requires API key)", False)

if use_gpt:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
    Explain decentralization of a system with:
    Gini={g:.2f}, HHI={h:.2f}, Entropy={e:.2f}, CDI={cdi:.2f}.
    Give insights and recommendations.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        st.write(response["choices"][0]["message"]["content"])
    except:
        st.error("API key missing or error occurred")

else:
    # Fallback AI
    if cdi < 0.3:
        st.error("Highly centralized system")
    elif cdi < 0.6:
        st.warning("Moderately decentralized")
    else:
        st.success("Highly decentralized")

# -------------------------------
# DOWNLOAD
# -------------------------------
st.download_button("⬇️ Download Results",
    pd.DataFrame({
        "Metric":["Gini","HHI","Entropy","CDI"],
        "Value":[g,h,e,cdi]
    }).to_csv(index=False),
    "cdi.csv"
)
