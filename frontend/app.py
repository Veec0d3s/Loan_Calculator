import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Loan & Salary Advance Calculator", layout="centered")
st.title("💰 Salary Advance & Loan Calculator")

# ----------------------------
# MULTI-CURRENCY SUPPORT
# ----------------------------
currency_map = {
    "UGX": "USh",
    "USD": "$",
    "KES": "KSh"
}
currency = st.selectbox("Choose your currency", options=list(currency_map.keys()))
symbol = currency_map[currency]

# ----------------------------
# INPUT FORM
# ----------------------------
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        salary = st.number_input(f"Monthly Salary ({symbol})", min_value=0.0, step=100.0)
        loan = st.number_input(f"Loan or Advance Amount ({symbol})", min_value=0.0, step=100.0)
    with col2:
        rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
        months = st.slider("Repayment Period (Months)", 1, 24, 6)
        frequency = st.selectbox("Repayment Frequency", ["monthly", "weekly"])
    submitted = st.form_submit_button("💡 Calculate")

# ----------------------------
# BACKEND CALCULATION
# ----------------------------
if submitted:
    payload = {
        "salary": salary,
        "loan_amount": loan,
        "interest_rate": rate,
        "months": months,
        "frequency": frequency
    }

    try:
        response = requests.post("http://backend:8000/calculate_advance", json=payload)
        response.raise_for_status()
        data = response.json()

        # ----------------------------
        # FINANCIAL ADVICE
        # ----------------------------
        st.subheader("💡 Financial Advice")
        ratio = data["repayment_per_period"] / salary
        if ratio > 0.4:
            st.error("⚠️ Warning: You're spending more than 40% of your salary on loan repayments. Consider a smaller loan.")
        elif ratio > 0.3:
            st.warning("Caution: You're spending over 30% of your salary on repayments. This may be financially straining.")
        else:
            st.success("Your repayment is within a safe range.")

        # ----------------------------
        # MAIN METRICS
        # ----------------------------
        st.success(f"Repayment per {data['frequency']}: {symbol}{data['repayment_per_period']}")
        st.info(f"Total Interest: {symbol}{data['total_interest']}")
        st.warning(f"Net Salary After Deductions: {symbol}{data['net_salary']}")

        # ----------------------------
        # REPAYMENT SCHEDULE TABLE
        # ----------------------------
        df = pd.DataFrame(data["schedule"])
        st.subheader("📅 Repayment Schedule")
        st.dataframe(df)

        # ----------------------------
        # LOAN BALANCE LINE CHART
        # ----------------------------
        st.subheader("📉 Remaining Balance Over Time")
        st.line_chart(df.set_index("period")["remaining_balance"])

        # ----------------------------
        # PIE CHARTS
        # ----------------------------
        st.subheader("📊 Loan Breakdown")
        pie_df = pd.DataFrame({
            "Component": ["Loan Principal", "Interest"],
            "Amount": [loan, data["total_interest"]]
        })
        fig = px.pie(pie_df, names="Component", values="Amount", title="Loan vs Interest")
        st.plotly_chart(fig)

        st.subheader("💼 Salary Distribution After Repayment")
        salary_df = pd.DataFrame({
            "Component": ["Net Salary Remaining", "Repayment Deduction"],
            "Amount": [data["net_salary"], data["repayment_per_period"]]
        })
        fig2 = px.pie(salary_df, names="Component", values="Amount", title="Salary Breakdown")
        st.plotly_chart(fig2)

        # ----------------------------
        # CSV DOWNLOAD with Custom Filename
        # ----------------------------
        st.subheader("⬇️ Download Schedule")
        custom_filename = st.text_input("Enter a filename (without .csv)", value="repayment_schedule")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Repayment Schedule as CSV",
            data=csv,
            file_name=f"{custom_filename}.csv",
            mime="text/csv"
        )

        # ----------------------------
        # LOAN COMPARISON TOOL (Fixed with Session State)
        # ----------------------------
        if "compare_clicked" not in st.session_state:
            st.session_state.compare_clicked = False

        st.subheader("🔄 Compare with Another Loan")

        with st.expander("Compare With Another Option", expanded=True):
            with st.form("compare_form"):
                st.markdown("Use this section to compare your current loan to another offer.")

                alt_loan = st.number_input("Alt. Loan Amount", min_value=0.0, step=100.0, key="alt_loan")
                alt_rate = st.number_input("Alt. Interest Rate (%)", min_value=0.0, step=0.1, key="alt_rate")
                alt_months = st.slider("Alt. Repayment Period (Months)", 1, 24, 6, key="alt_months")
                alt_frequency = st.selectbox("Alt. Frequency", ["monthly", "weekly"], key="alt_frequency")

                compare_submitted = st.form_submit_button("🔍 Compare Loans")

                if compare_submitted:
                    # Save all inputs to session state so they persist after rerun
                    st.session_state["do_compare"] = True
                    st.session_state["alt_payload"] = {
                        "salary": salary,
                        "loan_amount": alt_loan,
                        "interest_rate": alt_rate,
                        "months": alt_months,
                        "frequency": alt_frequency
                    }

        # Only compare if session state was set
        if st.session_state.get("do_compare", False):
            alt_payload = st.session_state["alt_payload"]
            try:
                alt_response = requests.post("http://backend:8000/calculate_advance", json=alt_payload)
                alt_response.raise_for_status()
                alt_data = alt_response.json()

                st.subheader("📊 Loan Comparison")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Repayment", f"${data['repayment_per_period']} per {frequency}")
                    st.metric("Current Interest", f"${data['total_interest']}")
                with col2:
                    st.metric("Alt. Repayment", f"${alt_data['repayment_per_period']} per {alt_payload['frequency']}")
                    st.metric("Alt. Interest", f"${alt_data['total_interest']}")

                # Comparison conclusion
                if alt_data["total_interest"] < data["total_interest"]:
                    st.success("✅ The alternative loan has less total interest.")
                elif alt_data["total_interest"] > data["total_interest"]:
                    st.info("ℹ️ Your current loan has lower total interest.")
                else:
                    st.warning("⚖️ Both loans have the same total interest.")

            except Exception as e:
                st.error(f"Comparison failed: {e}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")