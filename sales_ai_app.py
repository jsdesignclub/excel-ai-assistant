import streamlit as st
import pandas as pd
import re
import plotly.express as px

st.set_page_config(page_title="Excel AI Assistant", page_icon="📊", layout="wide")

st.title("📊 Excel AI Sales Assistant with Charts")
st.write("Upload your Excel file and ask questions like:")
st.code("total sales in 2023\ncompare 2022 and 2023\nshow sales by month in 2024")

# --- Upload Excel File ---
uploaded_file = st.file_uploader("📂 Upload your Excel sales file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month_name()

    st.success("✅ File uploaded successfully!")

    # --- Question Input ---
    question = st.text_input("💬 Ask a question:")

    if question:
        question = question.lower()
        years = re.findall(r"20\d{2}", question)
        year = int(years[0]) if years else None

        # Detect product
        product = None
        if "product" in df.columns:
            for p in df["Product"].dropna().unique():
                if str(p).lower() in question:
                    product = p
                    break

        # Detect month
        months = ["january","february","march","april","may","june","july",
                  "august","september","october","november","december"]
        month = None
        for m in months:
            if m in question:
                month = m.capitalize()
                break

        # --- 1️⃣ Total Sales ---
        if "total" in question and "sale" in question:
            data = df.copy()
            if year:
                data = data[data["Year"] == year]
            if product:
                data = data[data["Product"].str.lower() == product.lower()]
            if month:
                data = data[data["Month"] == month]

            total = data["Sales"].sum()
            st.info(f"💰 Total sales{' for ' + str(product) if product else ''}"
                    f"{' in ' + month if month else ''}"
                    f"{' ' + str(year) if year else ''}: **{total:,.2f}**")

        # --- 2️⃣ Compare Years ---
        elif "compare" in question and "sale" in question:
            if len(years) == 2:
                y1, y2 = int(years[0]), int(years[1])
                s1 = df[df["Year"] == y1]["Sales"].sum()
                s2 = df[df["Year"] == y2]["Sales"].sum()
                change = ((s2 - s1) / s1 * 100) if s1 else 0

                st.subheader("📊 Yearly Comparison")
                comp_df = pd.DataFrame({
                    "Year": [y1, y2],
                    "Sales": [s1, s2]
                })
                fig = px.bar(comp_df, x="Year", y="Sales", text="Sales", color="Year",
                             title="Yearly Sales Comparison", height=400)
                st.plotly_chart(fig, use_container_width=True)

                st.write(f"Change: {'🔺' if s2 > s1 else '🔻'} {abs(change):.2f}%")
            else:
                st.warning("Please mention two years (e.g., 'compare 2022 and 2023').")

        # --- 3️⃣ Monthly or Yearly Chart ---
        elif "show" in question and "sale" in question:
            data = df.copy()
            if year:
                data = data[data["Year"] == year]
            if product:
                data = data[data["Product"].str.lower() == product.lower()]

            if "month" in question:
                chart_data = data.groupby("Month")["Sales"].sum().reindex(
                    ["January","February","March","April","May","June",
                     "July","August","September","October","November","December"]
                ).dropna()
                fig = px.bar(x=chart_data.index, y=chart_data.values,
                             title=f"Monthly Sales{' for ' + str(product) if product else ''}"
                                   f"{' in ' + str(year) if year else ''}",
                             labels={"x": "Month", "y": "Sales"})
                st.plotly_chart(fig, use_container_width=True)

            elif "year" in question:
                chart_data = data.groupby("Year")["Sales"].sum()
                fig = px.line(x=chart_data.index, y=chart_data.values,
                              title="Yearly Sales Trend", markers=True,
                              labels={"x": "Year", "y": "Sales"})
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Please specify 'month' or 'year' for the chart.")

        # --- 4️⃣ Top Product ---
        elif "top" in question or "best" in question:
            data = df.copy()
            if year:
                data = data[data["Year"] == year]
            top = data.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(5)
            st.success(f"🏆 Top Products{' in ' + str(year) if year else ''}")
            fig = px.bar(top, x=top.index, y=top.values, title="Top Products", text=top.values)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("🤖 Sorry, I didn't understand that question.")
else:
    st.info("👆 Please upload an Excel file to start.")
