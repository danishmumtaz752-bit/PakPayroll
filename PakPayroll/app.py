import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="Pak-US Dollar & Local Payroll Engine",
    page_icon="💵",
    layout="wide"
)

# Dummy User Database (Email, Password, Subscription Active Status, Expiry Date)
USERS = {
    "user@company.com": {
        "password": "password123",
        "name": "Ali Tech Agency",
        "status": "Active",
        "expiry": "2026-12-31"
    },
    "expired@company.com": {
        "password": "password123",
        "name": "Expired Client",
        "status": "Expired",
        "expiry": "2026-01-01"
    }
}

# Session State for Authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# ---------------- LOGIN SCREEN ----------------
if not st.session_state["logged_in"]:
    st.title("🔐 Client Login - Payroll Engine SaaS")
    st.write("Please log in to access your payroll dashboard.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Log In", use_container_width=True)
        
        if login_btn:
            if email in USERS and USERS[email]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.rerun()
                st.toast("Success!", icon="🎉")
            else:
                st.error("Invalid Email or Password!")

# ---------------- SUBSCRIPTION BLOCK CHECK ----------------
user_info = USERS[st.session_state["user_email"]]

# Sidebar Logout & Subscription Status
st.sidebar.write(f"👤 **Logged in as:** {user_info['name']}")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.rerun()

st.sidebar.markdown("---")

if user_info["status"] != "Active":
    st.error("⚠️ **Subscription Expired or Inactive!**")
    st.warning(f"Your plan expired on **{user_info['expiry']}**. Please renew your subscription to access the Payroll Tool.")
    
    st.markdown("""
    ### 💳 Renew Your Monthly Subscription
    Please transfer **Rs. 5,000 / month** to activate your account:
    * **Bank account:** upaisa
    * **Account Title:** MUHAMMAD DANISH
    * **IBAN/Account:** PK60UMBL0000032397678189
    * **UPAISA ACCOUNT NUMBER:** 03239767818
    
    *Send payment screenshot to WhatsApp (+92-3185396067) for instant activation.*
    """)
    st.stop()

# ---------------- MAIN PAYROLL APP ----------------
st.title("💵 Pak-US Dollar Risk & Local Payroll Auto-Deductions Engine")
st.caption("Designed for Pakistani Tech Companies & Agencies")

# Sidebar Exchange Rate
st.sidebar.header("⚙️ Exchange Rate & Settings")
usd_rate = st.sidebar.number_input("USD to PKR Exchange Rate:", value=277.86, step=0.5)
st.sidebar.success(f"Live USD/PKR Rate: Rs. {usd_rate:.2f}")

st.sidebar.subheader("📌 Fixed Deductions")
eobi_deduction = st.sidebar.number_input("EOBI Monthly Deduction (PKR):", value=300, step=50)

# Tabs
tab1, tab2 = st.tabs(["⚡ Single Calculation", "📊 Bulk Batch Payroll (CSV)"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        emp_name = st.text_input("Employee Name:", "Muhammad Danish")
        emp_id = st.text_input("Employee ID / Designation:", "EMP-101 (Software Engineer)")
        currency = st.radio("Salary Pegged In:", ["USD ($)", "PKR (Rs)"])
        base_salary = st.number_input("Base Monthly Salary Amount:", value=700.0, step=50.0)
        
    with col2:
        st.subheader("📊 Salary Breakdown Summary")
        if currency == "USD ($)":
            gross_pkr = base_salary * usd_rate
            gross_usd = base_salary
        else:
            gross_pkr = base_salary
            gross_usd = base_salary / usd_rate
            
        # Simplified Tax Calculation
        annual_pkr = gross_pkr * 12
        if annual_pkr <= 600000:
            annual_tax = 0
        elif annual_pkr <= 1200000:
            annual_tax = (annual_pkr - 600000) * 0.05
        elif annual_pkr <= 2200000:
            annual_tax = 30000 + (annual_pkr - 1200000) * 0.15
        elif annual_pkr <= 3200000:
            annual_tax = 180000 + (annual_pkr - 2200000) * 0.25
        elif annual_pkr <= 4100000:
            annual_tax = 430000 + (annual_pkr - 3200000) * 0.30
        else:
            annual_tax = 700000 + (annual_pkr - 4100000) * 0.35
            
        monthly_tax = annual_tax / 12
        net_payable = gross_pkr - monthly_tax - eobi_deduction
        
        st.write(f"**Gross Salary (USD):** ${gross_usd:,.2f}")
        st.write(f"**Gross Salary (PKR):** Rs. {gross_pkr:,.2f}")
        st.write(f"**FBR Monthly Income Tax:** Rs. {monthly_tax:,.2f}")
        st.write(f"**EOBI Contribution:** Rs. {eobi_deduction:,.2f}")
        st.markdown("---")
        st.write(f"### Net Payable Salary: Rs. {net_payable:,.2f}")

with tab2:
    st.subheader("📁 Upload Bulk Employee Data")
    st.write("Upload a CSV file with columns: `Name`, `Designation`, `Currency`, `Base_Salary`")
    
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:", df)