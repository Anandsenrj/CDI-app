import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="CDI Dashboard", layout="wide")

# -------------------------------
# DARK MODE TOGGLE
# -------------------------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

# -------------------------------
# DYNAMIC CSS (GLASS + ANIMATION)
# -------------------------------
if dark_mode:
    bg_color = "#0f172a"
    text_color = "white"
    card_bg = "rgba(255, 255, 255, 0.08)"
else:
    bg_color = "#f8fafc"
    text_color = "black"
    card_bg = "rgba(255, 255, 255, 0.6)"

st.markdown(f"""
<style>
body {{
    background: {bg_color};
    color: {text_color};
}}

.card {{
    background: {card_bg};
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}}

.card:hover {{
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}}

.title {{
    font-size: 42px;
    font-weight: 700;
}}

.subtitle {{
    color: gray;
    margin-bottom: 20px;
}}

.fade-in {{
    animation: fadeIn 1s ease-in;
}}

@keyframes fadeIn {{
    from {{opacity: 0; transform: translateY(20px);}}
    to {{opacity: 1; transform: translateY(0);}}
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.markdown('<div class="title fade-in">🧠 CDI Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced Web3 Analytics with AI Insights</div>', unsafe_allow_html=True)

# -------------------------------
# FUNCTIONS
# -------------------------------
def gini(arr):
    arr = np.sort(arr)
    n = len(arr)
    if np.sum(arr) == 0:
        return 0
    return (2 * np.sum((np.arange(1, n+1) * arr))) / (n * np.sum(arr)) - (n + 1) / n

def hhi(arr):
    total = np.sum(arr)
    if total == 0:
        return 0
    shares = arr / total
    return np.sum(shares**2) * 10000

def entropy(arr):
    total = np.sum(arr)
    if total == 0:
        return 0
    prob = arr / total
    return -np.sum(prob * np.log2(prob + 1e-9))

# -------------------------------
# DATA
# -------------------------------
df = pd.DataFrame({
    "tokens": [5000,4200,3900,3500,3000,2500,2000],
    "votes": [300,250,200,180,160,140,120],
    "transactions": [1200,1100,1050,980,900,850,780]
})

tokens = np.array(df["tokens"])
votes = np.array(df["votes"])
transactions = np.array(df["transactions"])

# -------------------------------
# CALCULATIONS
# -------------------------------
g = gini(tokens)
h = hhi(votes)
e = entropy(transactions)

g_norm = 1 - g
h_norm = 1 - (h / 10000)
e_norm = e / np.log2(len(transactions))
cdi = (g_norm + h_norm + e_norm) / 3

# -------------------------------
# METRIC CARDS (ANIMATED)
# -------------------------------
st.subheader("📊 Metrics")

col1, col2, col3, col4 = st.columns(4)

def card(title, value):
    st.markdown(f"""
    <div class="card fade-in">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

with col1:
    card("Gini", f"{g_norm:.3f}")
with col2:
    card("HHI", f"{h_norm:.3f}")
with col3:
    card("Entropy", f"{e_norm:.3f}")
with col4:
    card("CDI", f"{cdi:.3f}")

# -------------------------------
# CHARTS
# -------------------------------
st.subheader("📈 Analytics")

colA, colB = st.columns(2)

with colA:
    fig, ax = plt.subplots()
    ax.bar(['Gini','HHI','Entropy'], [g_norm, h_norm, e_norm])
    st.pyplot(fig)

with colB:
    fig2, ax2 = plt.subplots()
    ax2.pie([g_norm, h_norm, e_norm], labels=['Gini','HHI','Entropy'], autopct='%1.1f%%')
    st.pyplot(fig2)

# -------------------------------
# AI INSIGHTS (ENHANCED STYLE)
# -------------------------------
st.subheader("🧠 AI Insights")

if cdi < 0.3:
    st.error("🔴 Highly Centralized System")
elif cdi < 0.6:
    st.warning("🟡 Moderate Decentralization — Governance needs improvement")
else:
    st.success("🟢 Strong Decentralization")

st.markdown("""
<div class="card fade-in">
<ul>
<li>Ownership is concentrated among large holders.</li>
<li>Governance participation is limited.</li>
<li>Transaction activity shows strong user engagement.</li>
</ul>
</div>
""", unsafe_allow_html=True)
