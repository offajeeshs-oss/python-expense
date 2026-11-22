
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Database connection
conn = sqlite3.connect("expenses.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    expense_date TEXT NOT NULL
)
""")
conn.commit()

# Application heading
st.title("💰 Personal Expense Tracker")
st.write("Manage your daily expenses easily.")

# Add expense form
st.subheader("Add New Expense")

with st.form("expense_form"):
    name = st.text_input("Expense Name")
    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=10.0
    )

    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Education", "Other"]
    )

    expense_date = st.date_input(
        "Expense Date",
        value=date.today()
    )

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if name.strip() and amount > 0:
            conn.execute(
                """INSERT INTO expenses
                (name, amount, category, expense_date)
                VALUES (?, ?, ?, ?)""",
                (name.strip(), amount, category, str(expense_date))
            )
            conn.commit()
            st.success("Expense added successfully!")
            st.rerun()
        else:
            st.error("Please enter a name and valid amount.")

# Retrieve expenses
df = pd.read_sql_query(
    "SELECT * FROM expenses ORDER BY expense_date DESC",
    conn
)

st.divider()

# Dashboard metrics
total = df["amount"].sum() if not df.empty else 0
count = len(df)

col1, col2 = st.columns(2)

col1.metric("Total Expenses", f"₹{total:,.2f}")
col2.metric("Total Transactions", count)

# Expense history
st.subheader("📋 Expense History")

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Category chart
    st.subheader("📊 Spending by Category")

    category_data = df.groupby("category")["amount"].sum()

    st.bar_chart(category_data)

    # Delete expense
    st.subheader("Delete Expense")

    expense_id = st.selectbox(
        "Select Expense ID",
        df["id"].tolist()
    )

    if st.button("Delete Selected Expense"):
        conn.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )
        conn.commit()
        st.success("Expense deleted!")
        st.rerun()

else:
    st.info("No expenses added yet. Start by adding your first expense!")

conn.close()
