import streamlit as st
import pandas as pd
from pathlib import Path

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Phones Data Analysis Dashboard",
    layout="wide"
)

st.title("📱 Phones Data Analysis Dashboard")

# ==================================================
# FILE CONFIG
# ==================================================
CSV_PATH = Path("/app/clean_data/clean_data_result.csv")

COLUMN_NAMES = [
    "id",
    "phone_name",
    "brand",
    "model",
    "ram",
    "rom",
    "price_original",
    "price",
    "stock_status",
    "condition",
    "source",
    "date"
]

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find file: {CSV_PATH}"
        )

    df = pd.read_csv(
        CSV_PATH,
        header=None,
        names=COLUMN_NAMES
    )

    # Convert numeric columns
    df["price_original"] = pd.to_numeric(
        df["price_original"],
        errors="coerce"
    )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    # Convert date column
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    return df


# ==================================================
# LOAD DATASET
# ==================================================
try:

    df = load_data()

    st.success(
        f"✅ Loaded successfully: {CSV_PATH}"
    )

except Exception as e:

    st.error(str(e))
    st.stop()


# ==================================================
# DEBUG SECTION
# ==================================================
with st.expander("System Information"):

    st.write("CSV Path:", CSV_PATH)
    st.write("Rows:", len(df))
    st.write("Columns:", len(df.columns))


# ==================================================
# SIDEBAR FILTERS
# ==================================================
st.sidebar.header("Filters")

selected_brands = st.sidebar.multiselect(
    "Brand",
    options=sorted(df["brand"].dropna().unique()),
    default=sorted(df["brand"].dropna().unique())
)

selected_stock = st.sidebar.multiselect(
    "Stock Status",
    options=sorted(df["stock_status"].dropna().unique()),
    default=sorted(df["stock_status"].dropna().unique())
)

selected_sources = st.sidebar.multiselect(
    "Source",
    options=sorted(df["source"].dropna().unique()),
    default=sorted(df["source"].dropna().unique())
)

filtered_df = df[
    (df["brand"].isin(selected_brands))
    &
    (df["stock_status"].isin(selected_stock))
    &
    (df["source"].isin(selected_sources))
]


# ==================================================
# KPI CARDS
# ==================================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "Total Products",
    f"{len(filtered_df):,}"
)

if len(filtered_df) > 0:

    kpi2.metric(
        "Average Original Price",
        f"{filtered_df['price_original'].mean():,.0f} VND"
    )

    kpi3.metric(
        "Average Sale Price",
        f"{filtered_df['price'].mean():,.0f} VND"
    )

    avg_discount = (
        filtered_df["price_original"] -
        filtered_df["price"]
    ).mean()

    kpi4.metric(
        "Average Discount",
        f"{avg_discount:,.0f} VND"
    )

else:

    kpi2.metric("Average Original Price", "0")
    kpi3.metric("Average Sale Price", "0")
    kpi4.metric("Average Discount", "0")

st.divider()


# ==================================================
# CHARTS - ROW 1
# ==================================================
col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Products by Brand")

    if len(filtered_df) > 0:

        brand_counts = (
            filtered_df["brand"]
            .value_counts()
        )

        st.bar_chart(brand_counts)

with col2:

    st.subheader("📈 Average Sale Price by Brand")

    if len(filtered_df) > 0:

        avg_price = (
            filtered_df
            .groupby("brand")["price"]
            .mean()
            .sort_values(ascending=False)
        )

        st.line_chart(avg_price)

st.divider()


# ==================================================
# CHARTS - ROW 2
# ==================================================
col3, col4 = st.columns(2)

with col3:

    st.subheader("📦 Stock Status Distribution")

    if len(filtered_df) > 0:

        stock_counts = (
            filtered_df["stock_status"]
            .value_counts()
        )

        st.bar_chart(stock_counts)

with col4:

    st.subheader("🏪 Products by Source")

    if len(filtered_df) > 0:

        source_counts = (
            filtered_df["source"]
            .value_counts()
        )

        st.bar_chart(source_counts)

st.divider()


# ==================================================
# PRICE SEGMENT ANALYSIS
# ==================================================
st.subheader("💰 Price Segment Analysis")

if len(filtered_df) > 0:

    segment_df = filtered_df.copy()

    segment_df["price_segment"] = pd.cut(
        segment_df["price"],
        bins=[
            0,
            32000000,
            37000000,
            41000000,
            float("inf")
        ],
        labels=[
            "Mid-range (28-32M)",
            "Upper Mid (32-37M)",
            "Premium (37-41M)",
            "Flagship (41M+)"
        ]
    )

    segment_counts = (
        segment_df["price_segment"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(segment_counts)

st.divider()


# ==================================================
# DATA TABLE
# ==================================================
st.subheader("📋 Product Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# DOWNLOAD CSV
# ==================================================
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_phones_data.csv",
    mime="text/csv"
)

