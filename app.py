import streamlit as st
import pandas as pd
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Pak-US Dollar & Local Payroll SaaS Engine",
    page_icon="💵",
    layout="wide"
)

# ---------------- DATABASE INITIALIZATION (SQLite) ----------------
def init_db():
    conn = sqlite3.connect('payroll_database.db')
    cursor = conn.cursor()
    
    # Employees Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            emp_name TEXT,
            designation TEXT,
            base_salary REAL,
            currency TEXT
        )
    ''')
    
    # Users Table for SaaS Management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            status TEXT,
            expiry TEXT
        )
    ''')
    
    # Insert default testing accounts if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('danish@gmail.com', 'mypassword123', 'Ali Tech Agency', 'Active', '2026-12-31')")
        cursor.execute("INSERT INTO users VALUES ('expired@company.com', 'password123', 'Expired Client', 'Expired', '2026-01-01')")
    
    conn.commit()
    conn.close()

init_db()

# Helper function to fetch users from DB
def get_user_from_db(email):
    conn = sqlite3.connect('payroll_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email, password, name, status, expiry FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "password": row[1],
            "name": row[2],
            "status": row[3],
            "expiry": row[4]
        }
    return None

# ---------------- BUSINESS & ADMIN CONFIGURATION ----------------
WHATSAPP_NUMBER = "923185396067"
SUBSCRIPTION_FEE = "Rs. 5,000 / month"

BANK_DETAILS = {
    "Payment Gateway / Mobile Wallet": "Upiasa Account",
    "Account Title": "Muhammad Danish",
    "Account / Mobile Number": "03239767818",
    "WhatsApp Support": "+92 318 5396067"
}

# Session State Initializer
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# ---------------- 1. LOGIN SCREEN ----------------
if not st.session_state["logged_in"]:
    st.title("🔐 Client Login Portal - Payroll SaaS Engine")
    st.write("Welcome back! Please sign in to manage your payroll calculations.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        email = st.text_input("Email Address", placeholder="client@company.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        login_btn = st.button("Log In to Portal", use_container_width=True)
        
        if login_btn:
            db_user = get_user_from_db(email)
            if db_user and db_user["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.rerun()
            else:
                st.error("❌ Invalid Email or Password. Please try again.")
        
        st.markdown("---")
        st.caption("💬 **Need help, account setup, or forgot password?**")
        st.markdown(f"[👉 Contact Admin Support on WhatsApp](https://wa.me/{WHATSAPP_NUMBER}?text=Hi%20Muhammad%20Danish,%20I%20need%20help%20with%20my%20Payroll%20Account)")

    with col2:
        st.stop()

# ---------------- 2. SUBSCRIPTION CONTROL BLOCK ----------------
user_info = get_user_from_db(st.session_state["user_email"])

# Sidebar Header & User Profile
st.sidebar.markdown(f"👤 **User:** `{user_info['name']}`")
st.sidebar.markdown(f"📌 **Status:** `{user_info['status']}`")

if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.rerun()

st.sidebar.markdown("---")

# Lock screen if subscription is expired
if user_info["status"] != "Active":
    st.error("⚠️ **Account Access Suspended / Plan Expired**")
    st.warning(f"Your plan expired on **{user_info['expiry']}**. Access to the Payroll Engine is currently locked.")
    
    st.markdown("### 💳 Renew Your Monthly Subscription")
    st.write(f"Please transfer **{SUBSCRIPTION_FEE}** to reactivate your account instant access:")
    
    for key, val in BANK_DETAILS.items():
        st.write(f"* **{key}:** {val}")
        
    st.markdown("---")
    st.markdown(f"[👉 Send Payment Proof via WhatsApp (+92-318-5396067)](https://wa.me/{WHATSAPP_NUMBER}?text=Hi%20Muhammad%20Danish,%20I%20have%20paid%20the%20subscription%20fee.%20Please%20activate%20my%20account.)")
    st.stop()

# ---------------- 3. MAIN PAYROLL DASHBOARD ----------------
st.title("💵 Pak-US Dollar & Enterprise Payroll Engine")
st.caption("Automated Tax (FBR Slabs), EOBI, Provident Fund, Attendance Tracking & Database Integration")

# Sidebar Exchange & Deductions Settings
st.sidebar.header("⚙️ Exchange Rates & Settings")
usd_rate = st.sidebar.number_input("USD to PKR Rate:", value=277.86, step=0.5)
aed_rate = st.sidebar.number_input("AED to PKR Rate:", value=75.60, step=0.25)
sar_rate = st.sidebar.number_input("SAR to PKR Rate:", value=74.00, step=0.25)

st.sidebar.subheader("📌 Mandatory Deductions")
eobi_deduction = st.sidebar.number_input("EOBI Monthly Amount (PKR):", value=300, step=50)
pf_percentage = st.sidebar.number_input("Provident Fund Deduction (% of Base):", value=5.0, step=1.0)

# Main Application Tabs
tab1, tab2, tab3 = st.tabs(["⚡ Single Employee & Attendance", "📁 Bulk Payroll Processing (CSV)", "❓ How To Use & Tax Info"])

# --- TAB 1: SINGLE CALCULATION & ATTENDANCE ---
with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Employee Details & Attendance")
        emp_name = st.text_input("Employee Name:", "Muhammad Danish")
        emp_id = st.text_input("Designation / ID:", "EMP-101 (Software Engineer)")
        
        currency = st.radio("Salary Currency:", ["USD ($)", "PKR (Rs)", "AED (Dirham)", "SAR (Riyal)"], horizontal=True)
        base_salary = st.number_input("Monthly Base Salary:", value=700.0, step=50.0)
        
        st.markdown("#### 🕒 Attendance & Leaves Control")
        total_working_days = st.number_input("Total Working Days in Month:", value=22, step=1)
        days_present = st.number_input("Days Attended / Present:", value=22, step=1)
        
        st.markdown("#### Additional Allowances (Monthly PKR)")
        medical_allowance = st.number_input("Medical Allowance:", value=5000.0, step=500.0)
        house_rent = st.number_input("House Rent Allowance:", value=15000.0, step=1000.0)
        bonus = st.number_input("Overtime / Bonus:", value=0.0, step=500.0)
        
        # Save to Database Button
        if st.button("💾 Save Employee to Database"):
            conn = sqlite3.connect('payroll_database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO employees (emp_id, emp_name, designation, base_salary, currency)
                VALUES (?, ?, ?, ?, ?)
            ''', (emp_id, emp_name, emp_id, base_salary, currency))
            conn.commit()
            conn.close()
            st.success("Employee data successfully saved to SQLite database!")
        
    with col2:
        st.subheader("📊 Monthly Salary Breakdown")
        
        # Currency Conversion Logic to PKR
        if currency == "USD ($)":
            base_pkr = base_salary * usd_rate
        elif currency == "AED (Dirham)":
            base_pkr = base_salary * aed_rate
        elif currency == "SAR (Riyal)":
            base_pkr = base_salary * sar_rate
        else:
            base_pkr = base_salary
            
        # Attendance Pro-rata Calculation
        if total_working_days > 0:
            per_day_salary = base_pkr / total_working_days
            adjusted_base_pkr = per_day_salary * days_present
        else:
            adjusted_base_pkr = base_pkr
            
        # Provident Fund Calculation
        pf_deduction = adjusted_base_pkr * (pf_percentage / 100.0)
            
        # Total Gross Calculation based on attendance
        gross_pkr = adjusted_base_pkr + medical_allowance + house_rent + bonus
        
        # Standard FBR Income Tax Calculation (Annual Slabs)
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
        net_payable = gross_pkr - monthly_tax - eobi_deduction - pf_deduction
        
        st.info(f"**Adjusted Base (Attendance):** Rs. {adjusted_base_pkr:,.2f}")
        st.write(f"**Gross Salary (PKR):** Rs. {gross_pkr:,.2f}")
        st.write(f"**FBR Income Tax (Deduction):** Rs. {monthly_tax:,.2f}")
        st.write(f"**EOBI Pension (Deduction):** Rs. {eobi_deduction:,.2f}")
        st.write(f"**Provident Fund (Deduction):** Rs. {pf_deduction:,.2f}")
        st.markdown("---")
        st.success(f"### Net In-Hand Transfer: Rs. {net_payable:,.2f}")
        
        # PDF Generator Functionality
        def generate_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1f4e78'),
                spaceAfter=12
            )
            
            elements.append(Paragraph("Official Payslip - Enterprise Payroll Engine", title_style))
            elements.append(Paragraph(f"<b>Employee Name:</b> {emp_name}", styles['Normal']))
            elements.append(Paragraph(f"<b>Designation/ID:</b> {emp_id}", styles['Normal']))
            elements.append(Paragraph(f"<b>Attendance:</b> {days_present} / {total_working_days} Days", styles['Normal']))
            elements.append(Spacer(1, 12))
            
            data = [
                ["Description", "Amount (PKR)"],
                ["Adjusted Base Salary", f"Rs. {adjusted_base_pkr:,.2f}"],
                ["Medical Allowance", f"Rs. {medical_allowance:,.2f}"],
                ["House Rent", f"Rs. {house_rent:,.2f}"],
                ["Bonus / Overtime", f"Rs. {bonus:,.2f}"],
                ["Gross Salary", f"Rs. {gross_pkr:,.2f}"],
                ["FBR Tax Deduction", f"- Rs. {monthly_tax:,.2f}"],
                ["EOBI Deduction", f"- Rs. {eobi_deduction:,.2f}"],
                ["Provident Fund", f"- Rs. {pf_deduction:,.2f}"],
                ["Net Payable", f"Rs. {net_payable:,.2f}"]
            ]
            
            t = Table(data, colWidths=[250, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d9ead3')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            elements.append(t)
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_file = generate_pdf()
        st.download_button(
            label="📄 Download Official Payslip (PDF)",
            data=pdf_file,
            file_name=f"{emp_name}_payslip.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# --- TAB 2: BULK CSV PROCESSING ---
with tab2:
    st.subheader("📁 Process Multiple Employees via CSV & Database Auto-Save")
    st.write("Upload a CSV file containing columns: `emp_id`, `emp_name`, `designation`, `base_salary`, `currency` to save them directly to the database.")
    
    uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:", df)
        
        if st.button("📥 Import & Save CSV Data to Database"):
            try:
                conn = sqlite3.connect('payroll_database.db')
                df.to_sql('employees', conn, if_exists='append', index=False)
                conn.close()
                st.success("✅ All employee records from CSV have been successfully saved to the database!")
            except Exception as e:
                st.error(f"❌ Error saving to database: {e}")
        
    st.markdown("---")
    st.subheader("🗄️ Saved Employees in Database")
    if st.button("Load Database Records"):
        conn = sqlite3.connect('payroll_database.db')
        db_df = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        if not db_df.empty:
            st.dataframe(db_df)
        else:
            st.info("No records found in database yet.")

# --- TAB 3: HELP & DOCUMENTATION ---
with tab3:
    st.subheader("💡 Enterprise Tool Usage Guide")
    st.markdown("""
    1. **SQLite Database Authentication & Storage:** Client credentials and employee data are securely stored in a local SQLite database (`payroll_database.db`).
    2. **Provident Fund (PF):** Automatically calculates corporate provident fund deductions based on custom sidebar percentages.
    3. **Attendance & Leaves:** Base salary dynamically updates based on the number of days attended vs total working days.
    4. **Multi-Currency Support:** Calculate salaries seamlessly across USD, AED, SAR, and PKR with live exchange controls.
    5. **PDF Payslips:** Instant generation of professional PDF salary slips for corporate auditing.
    """)
