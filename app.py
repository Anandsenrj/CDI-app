st.subheader("📘 Metric Explanations")

with st.expander("📊 Gini Coefficient (Ownership Distribution)"):
    st.markdown("""
**What it is:**  
Measures inequality in token distribution among users.

**Range:** 0 → perfectly equal, 1 → highly unequal

**In CDI:** We use (1 - Gini)  
👉 Lower inequality = higher decentralization

**Impact:**  
- Low score → few whales dominate  
- High score → fair distribution

**Effect on Result:**  
If Gini is high → CDI decreases significantly
""")

with st.expander("🏛️ HHI (Governance Concentration)"):
    st.markdown("""
**What it is:**  
Measures how concentrated voting power is.

**Range:**  
- Low → distributed governance  
- High → centralized control

**In CDI:** We normalize as (1 - HHI)

**Impact:**  
- Low score → few people control decisions  
- High score → democratic governance

**Effect on Result:**  
High concentration → reduces CDI
""")

with st.expander("🔄 Entropy (Transaction Distribution)"):
    st.markdown("""
**What it is:**  
Measures how evenly transactions are spread among users.

**High entropy:** Many active participants  
**Low entropy:** Few dominant users

**In CDI:** Higher entropy = higher decentralization

**Impact:**  
- High score → strong ecosystem usage  
- Low score → weak participation

**Effect on Result:**  
High entropy → increases CDI
""")

with st.expander("🧠 CDI (Composite Score)"):
    st.markdown(f"""
**Formula:**  
CDI = (Gini + HHI + Entropy) / 3

**Your Score:** **{cdi:.3f}**

**Interpretation:**
- 0 – 0.3 → Highly Centralized  
- 0.3 – 0.6 → Moderate  
- 0.6 – 1 → Highly Decentralized  

**Insight:**  
CDI balances ownership, governance, and usage.

👉 Even if usage is high, governance concentration can reduce CDI  
(This is called the *Decentralization Paradox*)
""")
