
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Big Data Phone Analysis", layout="wide")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("clean_data_result.csv")
    except Exception:
        cols = ["product_name","brand","ram","storage","sale_price","source","crawl_date"]
        return pd.DataFrame(columns=cols)

df = load_data()

st.title("📱 Big Data Phone Market Analysis")

st.sidebar.header("Filters")

if not df.empty:
    if "brand" in df.columns:
        brands = sorted(df["brand"].dropna().astype(str).unique())
        selected_brands = st.sidebar.multiselect("Brand", brands, default=brands)
        df = df[df["brand"].astype(str).isin(selected_brands)]

    if "sale_price" in df.columns:
        df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")
        min_p = int(df["sale_price"].min()) if not df["sale_price"].isna().all() else 0
        max_p = int(df["sale_price"].max()) if not df["sale_price"].isna().all() else 100000000

        price_range = st.sidebar.slider(
            "Price Range",
            min_value=min_p,
            max_value=max_p,
            value=(min_p, max_p)
        )

        df = df[(df["sale_price"] >= price_range[0]) &
                (df["sale_price"] <= price_range[1])]

search = st.sidebar.text_input("Search Product")

if search and "product_name" in df.columns:
    df = df[df["product_name"].astype(str).str.contains(search, case=False, na=False)]

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Products", "Analytics", "Raw Data"]
)

with tab1:

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Products", len(df))

    if "brand" in df.columns:
        c2.metric("Brands", df["brand"].nunique())

    if "sale_price" in df.columns and len(df):
        c3.metric("Avg Price", f"{df['sale_price'].mean():,.0f}")
        c4.metric("Max Price", f"{df['sale_price'].max():,.0f}")

with tab2:

    st.subheader("Product List")
    st.dataframe(df, use_container_width=True)

with tab3:

    if not df.empty:

        col1, col2 = st.columns(2)

        if "brand" in df.columns:
            brand_count = (
                df.groupby("brand")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )

            fig1 = px.bar(
                brand_count,
                x="brand",
                y="count",
                title="Products by Brand"
            )

            col1.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(
                brand_count,
                names="brand",
                values="count",
                title="Brand Distribution"
            )

            col2.plotly_chart(fig2, use_container_width=True)

        if "ram" in df.columns and "sale_price" in df.columns:

            ram_price = (
                df.groupby("ram")["sale_price"]
                .mean()
                .reset_index()
            )

            fig3 = px.bar(
                ram_price,
                x="ram",
                y="sale_price",
                title="Average Price by RAM"
            )

            st.plotly_chart(fig3, use_container_width=True)

        if "brand" in df.columns and "sale_price" in df.columns:

            avg_brand = (
                df.groupby("brand")["sale_price"]
                .mean()
                .reset_index()
                .sort_values("sale_price", ascending=False)
            )

            fig4 = px.bar(
                avg_brand,
                x="brand",
                y="sale_price",
                title="Average Brand Price Ranking"
            )

            st.plotly_chart(fig4, use_container_width=True)

        if "crawl_date" in df.columns:

            try:
                temp = df.copy()
                temp["crawl_date"] = pd.to_datetime(temp["crawl_date"])

                ts = (
                    temp.groupby(temp["crawl_date"].dt.date)
                    .size()
                    .reset_index(name="count")
                )

                fig5 = px.line(
                    ts,
                    x="crawl_date",
                    y="count",
                    title="Time Series Aggregation"
                )

                st.plotly_chart(fig5, use_container_width=True)

            except Exception:
                pass

with tab4:
    st.subheader("Dataset Preview")
    st.write(df.head(50))

st.sidebar.markdown("---")
st.sidebar.info("Big Data Phone Analysis System")
