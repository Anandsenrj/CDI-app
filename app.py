import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="CDI Intelligence Dashboard",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------
# CUSTOM CSS (PREMIUM UI)
# -------------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
}
.title {
    font-size: 40px;
    font-weight: bold;
}
.subtitle {
    font-size: 18px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.markdown('<div class="title">🧠 CDI Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced Web3 Decentralization Analytics</div>', unsafe_allow_html=True)

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
# SIDEBAR INPUT
# -------------------------------
st.sidebar.header("⚙️ Configuration")

option = st.sidebar.radio("Data Source", ["Sample Data", "Upload CSV"])

if option == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        st.warning("Upload CSV file")
        st.stop()
else:
    df = pd.DataFrame({
        "tokens": [100, 200, 300, 400, 500, 1000, 2000],
        "votes": [10, 20, 30, 40, 50, 60, 70],
        "transactions": [50, 60, 70, 80, 90, 100, 110]
    })

# -------------------------------
# VALIDATION
# -------------------------------
if not {"tokens", "votes", "transactions"}.issubset(df.columns):
    st.error("CSV must contain tokens, votes, transactions")
    st.stop()

df = df.dropna()

# -------------------------------
# CALCULATIONS
# -------------------------------
tokens = np.array(df["tokens"])
votes = np.array(df["votes"])
transactions = np.array(df["transactions"])

g = gini(tokens)
h = hhi(votes)
e = entropy(transactions)

g_norm = 1 - g
h_norm = 1 - (h / 10000)
e_norm = e / np.log2(len(transactions))

cdi = (g_norm + h_norm + e_norm) / 3

# -------------------------------
# METRIC CARDS
# -------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

def card(title, value):
    st.markdown(f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

with col1:
    card("Gini (Ownership)", f"{g_norm:.3f}")
with col2:
    card("HHI (Governance)", f"{h_norm:.3f}")
with col3:
    card("Entropy (Usage)", f"{e_norm:.3f}")
with col4:
    card("CDI Score", f"{cdi:.3f}")

# -------------------------------
# CHARTS
# -------------------------------
st.subheader("📈 Visual Analytics")

colA, colB = st.columns(2)

with colA:
    fig, ax = plt.subplots()
    ax.bar(['Gini', 'HHI', 'Entropy'], [g_norm, h_norm, e_norm])
    ax.set_title("CDI Components")
    st.pyplot(fig)

with colB:
    fig2, ax2 = plt.subplots()
    ax2.pie([g_norm, h_norm, e_norm], labels=['Gini','HHI','Entropy'], autopct='%1.1f%%')
    ax2.set_title("Component Contribution")
    st.pyplot(fig2)

# -------------------------------
# AI INSIGHTS ENGINE
# -------------------------------
st.subheader("🧠 AI Insights")

def generate_insights(g, h, e, cdi):
    insights = []

    if g < 0.4:
        insights.append("⚠️ High ownership concentration detected (whales dominate token supply).")
    else:
        insights.append("✅ Token distribution is relatively fair.")

    if h < 0.4:
        insights.append("⚠️ Governance power is centralized among few participants.")
    else:
        insights.append("✅ Governance is well distributed.")

    if e > 0.6:
        insights.append("✅ Strong user participation across network.")
    else:
        insights.append("⚠️ Low transaction diversity.")

    if cdi < 0.3:
        insights.append("🔴 System is highly centralized — redesign tokenomics & governance.")
    elif cdi < 0.6:
        insights.append("🟡 System is moderately decentralized — improvements possible.")
    else:
        insights.append("🟢 System is highly decentralized — strong architecture.")

    return insights

insights = generate_insights(g_norm, h_norm, e_norm, cdi)

for i in insights:
    st.write(i)

# -------------------------------
# RECOMMENDATIONS ENGINE
# -------------------------------
st.subheader("🚀 Optimization Recommendations")

if g_norm < 0.4:
    st.write("👉 Improve token distribution (airdrops, staking incentives)")
if h_norm < 0.4:
    st.write("👉 Decentralize governance (DAO voting reforms)")
if e_norm < 0.5:
    st.write("👉 Increase user engagement (reduce fees, incentives)")

# -------------------------------
# DOWNLOAD
# -------------------------------
result_df = pd.DataFrame({
    "Metric": ["Gini", "HHI", "Entropy", "CDI"],
    "Value": [g_norm, h_norm, e_norm, cdi]
})

st.download_button("⬇️ Download Report", result_df.to_csv(index=False), "cdi_report.csv")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("💡 Premium CDI Dashboard | Built for Web3 Analytics + Data Science Portfolio")