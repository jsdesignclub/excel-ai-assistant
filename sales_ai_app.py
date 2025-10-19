import streamlit as st
import pandas as pd

# Load your Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month_name()

    st.subheader("📋 Sales Data Table")
    
    # Filter by Year
    years = df["Year"].dropna().unique().tolist()
    selected_year = st.selectbox("Filter by Year", ["All"] + [str(y) for y in years])
    if selected_year != "All":
        df = df[df["Year"] == int(selected_year)]

    # Filter by Product
    products = df["Product"].dropna().unique().tolist()
    selected_product = st.selectbox("Filter by Product", ["All"] + products)
    if selected_product != "All":
        df = df[df["Product"] == selected_product]

    st.dataframe(df)  # Interactive table
