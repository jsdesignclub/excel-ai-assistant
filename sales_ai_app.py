import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard")
st.write("Upload your Excel sales file to explore data and visualizations.")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month_name()

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    years = df["Year"].dropna().unique().tolist()
    selected_year = st.sidebar.selectbox("Select Year", ["All"] + [str(y) for y in years])

    products = df["Product"].dropna().unique().tolist()
    selected_product = st.sidebar.selectbox("Select Product", ["All"] + products)

    # Apply filters
    filtered_df = df.copy()
    if selected_year != "All":
        filtered_df = filtered_df[filtered_df["Year"] == int(selected_year)]
    if selected_product != "All":
        filtered_df = filtered_df[filtered_df["Product"] == selected_product]

    # --- Key Metrics ---
    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"{filtered_df['Sales'].sum():,.2f}")
    col2.metric("Total Quantity", f"{filtered_df['Quantity'].sum()}")
    if not filtered_df.empty:
        top_product = filtered_df.groupby("Product")["Sales"].sum().idxmax()
        col3.metric("Top Product", top_product)

    # --- Charts ---
    st.subheader("📊 Sales Charts")

    # 1️⃣ Monthly Sales Chart
    monthly_sales = filtered_df.groupby("Month")["Sales"].sum().reindex(
        ["January","February","March","April","May","June",
         "July","August","September","October","November","December"]
    ).dropna()
    fig1 = px.bar(x=monthly_sales.index, y=monthly_sales.values,
                  title="Monthly Sales", labels={"x": "Month", "y": "Sales"})
    st.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Yearly Sales Trend
    yearly_sales = filtered_df.groupby("Year")["Sales"].sum()
    fig2 = px.line(x=yearly_sales.index, y=yearly_sales.values, markers=True,
                   title="Yearly Sales Trend", labels={"x": "Year", "y": "Sales"})
    st.plotly_chart(fig2, use_container_width=True)

    # --- Interactive Table ---
    st.subheader("📋 Filterable Sales Table")
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_default_column(filterable=True, sortable=True)
    gb.configure_selection("single")
    grid_options = gb.build()
    AgGrid(filtered_df, gridOptions=grid_options, height=400, fit_columns_on_grid_load=True)

else:
    st.info("👆 Please upload an Excel file to start.")
