import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Retention Dashboard", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>

/* Main background */
body {
    background-color: #F5F7FA;
}

/* Headings */
h1, h2, h3 {
    color: #1F2937;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

/* KPI Numbers */
[data-testid="stMetricValue"] {
    color: #2563EB !important;
    font-size: 28px;
    font-weight: bold;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 500;
}

/* Divider spacing */
hr {
    margin-top: 20px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("final_dataset.csv")

st.title("📊 Customer Retention Strategy Dashboard")
st.write("### By Yashvi Jain")

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")

age = st.sidebar.slider("Age", int(df.Age.min()), int(df.Age.max()), (25, 60))
products = st.sidebar.slider("Products", int(df.NumOfProducts.min()), int(df.NumOfProducts.max()), (1,4))
balance = st.sidebar.slider("Balance", int(df.Balance.min()), int(df.Balance.max()), (0,150000))

filtered = df[
    (df['Age']>=age[0]) & (df['Age']<=age[1]) &
    (df['NumOfProducts']>=products[0]) & (df['NumOfProducts']<=products[1]) &
    (df['Balance']>=balance[0]) & (df['Balance']<=balance[1])
]

# ---------------- KPI ----------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Churn Rate", f"{filtered['Exited'].mean()*100:.2f}%")
col2.metric("Avg Balance", f"{filtered['Balance'].mean():.0f}")
col3.metric("Active Users", f"{filtered['IsActiveMember'].mean()*100:.2f}%")
col4.metric("Products Avg", f"{filtered['NumOfProducts'].mean():.2f}")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4,tab5 = st.tabs([
    "📊 Engagement vs Churn",
    "📦 Product Utilization",
    "💰 Financial Risk",
    "🧠 Retention & Segmentation",
    "💡 Insights & Recommendations"
])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader("Engagement vs Churn")

    fig, ax = plt.subplots(figsize=(4,2.5))
    pd.crosstab(filtered['IsActiveMember'], filtered['Exited']).plot(kind='bar', ax=ax, color=['#2563EB', '#F97316'])
    ax.set_title("Customer Engagement Impact on Churn", fontsize=15)
    ax.set_xlabel("Customer Activity Status")
    ax.set_ylabel("Number of Customers")
    ax.set_xticklabels(["Inactive", "Active"],rotation=0)
    plt.rcParams.update({'font.size':8})
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.pyplot(fig, use_container_width=True)
    ax.legend(["Retained", "Churned"], title="Customer Status")
    plt.tight_layout()

    st.success("👉 Active users have lower churn.")

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("Product Utilization")

    fig, ax = plt.subplots(figsize=(4,2.5))
    pd.crosstab(filtered['NumOfProducts'], filtered['Exited']).plot(kind='bar', ax=ax, color=['#2563EB', '#F97316'])
    ax.set_title("Product Usage vs Customer Retention", fontsize=15)
    ax.set_xlabel("No. of Products used")
    ax.set_ylabel("Number of Customers")
    ax.set_xticklabels(ax.get_xticklabels(),rotation=0)
    plt.rcParams.update({'font.size':8})
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.pyplot(fig, use_container_width=True)
    ax.legend(["Retained"], ["Churned"], title="Customer Status")
    plt.tight_layout()

    st.info("👉 More products = better retention.")

# ---------------- TAB 3 ----------------
with tab3:
    st.subheader("High-Value Disengaged Customer Analysis")

    high_risk = filtered[(filtered['Balance']>filtered['Balance'].median()) & (filtered['IsActiveMember']==0)]
    st.dataframe(high_risk.head(10))
    st.metric("High Risk %", f"{(len(high_risk)/len(filtered))*100:.2f}%")

    fig, ax = plt.subplots(figsize=(5,3))
    filtered['Balance'].plot(kind='hist', bins=10, ax=ax, color='#2563EB')
    ax.set_title("Balance Distribution", fontsize=9)
    ax.set_xlabel("Account Balance (₹)")
    ax.set_ylabel("Number of Customers")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.pyplot(fig, use_container_width=True)
    st.info("Customer with high balances but low activity are most likely to churn. These should be targeted immediately.")

# ---------------- TAB 4 ----------------
with tab4:
     
    st.header("🔴 Retention & Customer Segmentation")

    # =========================
    # 1. RETENTION STRENGTH KPI
    # =========================
    st.subheader("📊 Retention Strength")

    retention_score = (filtered['IsActiveMember'].mean() + 
                       (filtered['NumOfProducts'].mean()/4)) / 2

    col1, col2 = st.columns(2)

    col1.metric("Retention Strength Index", f"{retention_score:.2f}")
    col2.metric("Avg Products per Customer", f"{filtered['NumOfProducts'].mean():.2f}")

    # =========================
    # 2. CUSTOMER SEGMENTATION
    # =========================
    st.subheader("👥 Customer Segmentation")

    def segment_customer(row):
        if row['IsActiveMember'] == 1 and row['NumOfProducts'] >= 2:
            return "High Value Active"
        elif row['IsActiveMember'] == 0 and row['Balance'] > filtered['Balance'].median():
            return "High Value At Risk"
        elif row['NumOfProducts'] == 1:
            return "Low Engagement"
        else:
            return "Moderate"

    filtered['Segment'] = filtered.apply(segment_customer, axis=1)

    # =========================
    # 3. SEGMENT DISTRIBUTION CHART
    # =========================
    fig, ax = plt.subplots(figsize=(4, 2.5))

    filtered['Segment'].value_counts().plot(
        kind='bar',
        ax=ax,
        color="#2563EB"
    )

    ax.set_title("Customer Segments Distribution", fontsize=10)
    ax.set_xlabel("Customer Segment")
    ax.set_ylabel("Number of Customers")

    plt.xticks(rotation=20)

    plt.tight_layout()
    st.pyplot(fig, use_container_width=False)

    # =========================
    # 4. HIGH VALUE RISK KPI
    # =========================
    st.subheader("⚠️ High Value At-Risk Customers")
    
    high_risk = filtered[
        (filtered['Balance'] > filtered['Balance'].median()) &
        (filtered['IsActiveMember'] == 0)
    ].shape[0]

    st.metric("Number of High Risk Customers", high_risk)

# ---------------- TAB 5 ----------------
with tab5: 
    st.header("💡Insights & Recommendations")

    # =========================
    # 5. INSIGHTS SECTION
    # =========================
    st.subheader("📌 Key Insights")

    st.markdown("""
    - Customer engagement has a stronger impact on retention than account balance  
    - Low-product customers are high churn risk  
    - High-balance inactive customers need attention  
    - Multi-product usage improves loyalty  
    """)

    # =========================
    # 6. BUSINESS RECOMMENDATIONS
    # =========================
    st.subheader("💡 Recommendations")

    st.info("""
    - Target high-value inactive customers with personalized offers  
    - Encourage customers to use multiple products  
    - Improve engagement through loyalty programs  
    - Monitor low-engagement users closely  
    """)