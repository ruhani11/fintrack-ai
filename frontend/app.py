import streamlit as st
import pandas as pd
import requests
from datetime import date
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_URL = os.getenv("PROJECT_URL", "http://localhost:5000")

st.set_page_config(page_title="Fintrack AI", layout="centered")
st.title("💰 Fintrack AI – Budget Dashboard")

# ---------------- Add New Transaction ----------------
st.subheader("➕ Add a Transaction")

amount = st.number_input("Amount", min_value=0.0, format="%.2f")
category = st.selectbox("Category", [
    "Income", "Food", "Transport", "Shopping", "Utilities", "Health",
    "Entertainment", "Rent", "Savings", "Education", "Others"
])
date_input = st.date_input("Date", value=date.today())
month = date_input.strftime("%B")

if st.button("Add Transaction"):
    if amount and category and date_input:
        payload = {
            "amount": float(amount),
            "category": category,
            "date": date_input.strftime("%Y-%m-%d"),
            "month": month
        }
        try:
            res = requests.post(f"{API_URL}/api/transactions", json=payload)
            if res.status_code == 200:
                st.success("✅ Transaction added successfully!")
            else:
                st.error(f"❌ Failed to add: {res.text}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    else:
        st.warning("⚠️ Please fill all fields.")

st.divider()

# ---------------- View Transactions ----------------
st.subheader("📋 Transaction History")

try:
    res = requests.get(f"{API_URL}/api/transactions")
    if res.status_code == 200:
        data = res.json()
        if data:
            df = pd.DataFrame(data)
            df["amount"] = df["amount"].astype(float)
            df = df.sort_values(by="date", ascending=False)
            st.dataframe(df, use_container_width=True)

            total_income = df[df["category"] == "Income"]["amount"].sum()
            total_expense = df[df["category"] != "Income"]["amount"].sum()
            savings = total_income - total_expense

            st.markdown(f"""
                ### 💼 Financial Overview
                - **Total Income**: ₹{total_income:,.2f}
                - **Total Expenses**: ₹{total_expense:,.2f}
                - **Estimated Savings**: ₹{savings:,.2f}
            """)
        else:
            st.info("ℹ️ No transactions yet.")
    else:
        st.error("❌ Failed to load transactions.")
except Exception as e:
    st.error(f"⚠️ Error: {e}")

st.divider()

# ---------------- Monthly Summary & AI Tip ----------------
st.subheader("📊 Monthly Summary & AI Budget Tip")

selected_month = st.selectbox("📅 Select Month", [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

if st.button("Generate Summary"):
    try:
        summary_res = requests.post(f"{API_URL}/api/summary", json={"month": selected_month})

        if summary_res.status_code == 200:
            summary = summary_res.json()
            if summary:
                st.write("📊 Category-wise Breakdown")
                st.bar_chart(pd.Series(summary))

                income_amount = summary.get("Income", 0)
                expense_summary = {k: v for k, v in summary.items() if k != "Income"}

                tip_res = requests.post(f"{API_URL}/api/tip", json={
                    "summary": expense_summary,
                    "income": income_amount
                })

                if tip_res.status_code == 200:
                    st.success(f"💡 AI Tip: {tip_res.json()['tip']}")
                else:
                    st.warning("⚠️ Failed to load AI tip.")
            else:
                st.info("ℹ️ No data for selected month.")
        else:
            st.error("❌ Error loading summary.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
