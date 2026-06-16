import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Phone Market Analysis",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Sidebar */
  section[data-testid="stSidebar"] { background: #111111 !important; }
  section[data-testid="stSidebar"] *,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span { color: #f1f5f9 !important; }
  section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: #3b82f6 !important;
  }

  /* KPI Cards — high contrast cho dark mode */
  .kpi-card {
    background: #1e3a5f;
    border: 1px solid #3b82f6;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
  }
  .kpi-label { font-size: 12px; color: #93c5fd; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
  .kpi-value { font-size: 26px; font-weight: 700; color: #ffffff; }
  .kpi-sub   { font-size: 12px; color: #bfdbfe; margin-top: 4px; }
  .kpi-accent { color: #60a5fa; }

  /* Section headers — trắng cho dark mode */
  .section-header {
    font-size: 18px; font-weight: 600; color: #f1f5f9;
    border-left: 4px solid #3b82f6;
    padding-left: 12px; margin: 1.5rem 0 1rem;
  }

  /* Tab styling */
  button[data-baseweb="tab"] { font-size: 14px !important; font-weight: 500 !important; }
  button[data-baseweb="tab"][aria-selected="true"] { color: #60a5fa !important; }

  /* Insight box — dark mode friendly */
  .insight-box {
    background: #1e3a5f;
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    font-size: 13px; color: #bfdbfe; line-height: 1.6;
    margin: .5rem 0 1rem;
  }
  .insight-box b { color: #93c5fd; }

  /* Badge */
  .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .badge-green  { background: #166534; color: #bbf7d0; }
  .badge-red    { background: #991b1b; color: #fecaca; }
  .badge-blue   { background: #1d4ed8; color: #bfdbfe; }
  .badge-yellow { background: #854d0e; color: #fef08a; }

  /* CRUD success/info messages */
  .crud-success {
    background: #14532d; border: 1px solid #16a34a;
    border-radius: 8px; padding: .75rem 1rem;
    color: #86efac; font-weight: 500; margin: .5rem 0;
  }
  .crud-info {
    background: #1e3a5f; border: 1px solid #3b82f6;
    border-radius: 8px; padding: .75rem 1rem;
    color: #93c5fd; font-size: 13px; margin: .5rem 0;
  }

  /* Sidebar filter styling */
  .stMultiSelect [data-baseweb="tag"] {
    background: #3b82f6 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    font-size: 12px !important;
  }
  .stCheckbox label {
    color: #e2e8f0 !important;
    font-size: 13px !important;
    padding: 2px 0 !important;
  }
  section[data-testid="stSidebar"] .stButton button {
    font-size: 12px !important;
    padding: 4px 8px !important;
    border-radius: 6px !important;
  }
  .stSlider label {
    color: #e2e8f0 !important;
  }
  .stSlider [data-testid="stTickBar"] {
    color: #94a3b8 !important;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOAD
# ─────────────────────────────────────────────
COLUMN_NAMES = ["id","phone_name","brand","model","ram","storage",
                "original_price","sale_price","stock_status",
                "phone_condition","source","crawl_date"]

CSV_PATH = Path("/app/clean_data/clean_data_result.csv")
LOCAL_PATH = Path("clean_data_result.csv")

@st.cache_data
def load_data():
    path = CSV_PATH if CSV_PATH.exists() else LOCAL_PATH
    df = pd.read_csv(path, header=None, names=COLUMN_NAMES)
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")
    df["sale_price"]     = pd.to_numeric(df["sale_price"],     errors="coerce")
    df["crawl_date"]     = pd.to_datetime(df["crawl_date"],    errors="coerce")
    df["discount_amt"]   = df["original_price"] - df["sale_price"]
    df["discount_pct"]   = (df["discount_amt"] / df["original_price"] * 100).round(2)
    df["ram_num"]        = df["ram"].str.replace("GB","").str.strip().astype(float, errors="ignore")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Không tìm thấy file data: {e}")
    st.info("Đặt file `clean_data_result.csv` cùng thư mục với app.py để chạy local.")
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📱 Phone Market Analysis")
    st.markdown("**Đồ án BDES333877**")
    st.markdown("---")

    st.markdown("### 🔎 Bộ lọc")

    # ── Select All / Clear All ──
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button("✅ Chọn tất cả", key="select_all_btn", use_container_width=True)
    with col_btn2:
        st.button("❌ Bỏ chọn", key="clear_all_btn", use_container_width=True)

    all_brands = sorted(df["brand"].dropna().unique())
    all_sources = sorted(df["source"].dropna().unique())
    all_conditions = sorted(df["phone_condition"].dropna().unique())
    all_stocks = sorted(df["stock_status"].dropna().unique())

    # Init session state
    for key, val in [("sel_brands", all_brands), ("sel_sources", all_sources),
                      ("sel_conditions", all_conditions), ("sel_stocks", all_stocks)]:
        if key not in st.session_state:
            st.session_state[key] = val

    if st.session_state.get("select_all_btn"):
        st.session_state.sel_brands = all_brands
        st.session_state.sel_sources = all_sources
        st.session_state.sel_conditions = all_conditions
        st.session_state.sel_stocks = all_stocks
        st.rerun()
    if st.session_state.get("clear_all_btn"):
        st.session_state.sel_brands = []
        st.session_state.sel_sources = []
        st.session_state.sel_conditions = []
        st.session_state.sel_stocks = []
        st.rerun()

    # ── Filter sections with checkboxes ──
    def filter_section(label, options, session_key, cols=2):
        with st.container():
            st.markdown(f"**{label}**")
            cols_layout = st.columns(cols)
            current = st.session_state[session_key]
            remaining = [o for o in options if o not in current]
            # Render checked items first
            for i, opt in enumerate(current):
                c = cols_layout[i % cols]
                with c:
                    if st.checkbox(opt, value=True, key=f"{session_key}_chk_{opt}"):
                        pass
                    else:
                        st.session_state[session_key] = [x for x in current if x != opt]
                        st.rerun()
            # Render unchecked items
            for i, opt in enumerate(remaining):
                c = cols_layout[i % cols]
                with c:
                    if st.checkbox(opt, value=False, key=f"{session_key}_chk_{opt}"):
                        st.session_state[session_key] = current + [opt]
                        st.rerun()

    with st.container():
        st.markdown("**🏷️ Hãng**")
        cols_b = st.columns(3)
        for i, b in enumerate(all_brands):
            with cols_b[i % 3]:
                checked = b in st.session_state.sel_brands
                if st.checkbox(b, value=checked, key=f"brand_{b}"):
                    if b not in st.session_state.sel_brands:
                        st.session_state.sel_brands.append(b)
                else:
                    if b in st.session_state.sel_brands:
                        st.session_state.sel_brands.remove(b)

    with st.container():
        st.markdown("**📡 Nguồn**")
        cols_s = st.columns(2)
        for i, s in enumerate(all_sources):
            with cols_s[i % 2]:
                checked = s in st.session_state.sel_sources
                if st.checkbox(s, value=checked, key=f"source_{s}"):
                    if s not in st.session_state.sel_sources:
                        st.session_state.sel_sources.append(s)
                else:
                    if s in st.session_state.sel_sources:
                        st.session_state.sel_sources.remove(s)

    with st.container():
        st.markdown("**📱 Tình trạng máy**")
        cond_map = {"Moi 100%": "🆕 Mới 100%", "Da kich hoat": "📲 Đã kích hoạt", "Hang trung bay": "🏪 Trưng bày"}
        cols_c = st.columns(1)
        for i, (k, v) in enumerate(cond_map.items()):
            with cols_c[i % 1]:
                checked = k in st.session_state.sel_conditions
                if st.checkbox(v, value=checked, key=f"cond_{k}"):
                    if k not in st.session_state.sel_conditions:
                        st.session_state.sel_conditions.append(k)
                else:
                    if k in st.session_state.sel_conditions:
                        st.session_state.sel_conditions.remove(k)

    with st.container():
        st.markdown("**📦 Tình trạng kho**")
        stock_map = {"Con hang": "✅ Còn hàng", "Het hang": "🚫 Hết hàng"}
        cols_st = st.columns(2)
        for i, (k, v) in enumerate(stock_map.items()):
            with cols_st[i % 2]:
                checked = k in st.session_state.sel_stocks
                if st.checkbox(v, value=checked, key=f"stock_{k}"):
                    if k not in st.session_state.sel_stocks:
                        st.session_state.sel_stocks.append(k)
                else:
                    if k in st.session_state.sel_stocks:
                        st.session_state.sel_stocks.remove(k)

    # Price range
    st.markdown("**💰 Khoảng giá (VNĐ)**")
    price_min = int(df["sale_price"].min())
    price_max = int(df["sale_price"].max())
    price_range = st.slider("", price_min, price_max,
                            (price_min, price_max), step=500000,
                            format="%d")

    brands = st.session_state.sel_brands
    sources = st.session_state.sel_sources
    conditions = st.session_state.sel_conditions
    stocks = st.session_state.sel_stocks

    st.markdown("---")
    st.markdown("### 📌 Nhóm thực hiện")
    st.markdown("""
    - **TV4** Phan Hoàng An  
    - **TV1** Phạm Tuấn Minh  
    - **TV2** Nguyễn Đình Bảo  
    - **TV3** Huỳnh Minh Hải  
    """)

# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────
fdf = df[
    df["brand"].isin(brands) &
    df["source"].isin(sources) &
    df["phone_condition"].isin(conditions) &
    df["stock_status"].isin(stocks) &
    df["sale_price"].between(price_range[0], price_range[1])
].copy()

if len(fdf) == 0:
    st.warning("Không có dữ liệu phù hợp với bộ lọc. Vui lòng điều chỉnh.")
    st.stop()

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tổng quan",
    "💰 Phân tích giá",
    "🏪 So sánh nguồn",
    "📦 Tồn kho & Tình trạng",
    "🗃️ Dữ liệu & CRUD"
])

# ══════════════════════════════════════════════
# TAB 1 — TỔNG QUAN
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Chỉ số thị trường</div>', unsafe_allow_html=True)

    # KPI row 1
    k1, k2, k3, k4 = st.columns(4)
    total = len(fdf)
    avg_sale = fdf["sale_price"].mean()
    avg_disc_pct = fdf["discount_pct"].mean()
    out_of_stock = (fdf["stock_status"] == "Het hang").sum()
    oos_rate = out_of_stock / total * 100

    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Tổng sản phẩm</div>
            <div class="kpi-value">{total:,}</div>
            <div class="kpi-sub">{len(fdf["brand"].unique())} thương hiệu</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Giá bán trung bình</div>
            <div class="kpi-value kpi-accent">{avg_sale/1e6:.1f}M</div>
            <div class="kpi-sub">VNĐ</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Tỷ lệ giảm giá TB</div>
            <div class="kpi-value">{avg_disc_pct:.2f}%</div>
            <div class="kpi-sub">avg discount rate</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Tỷ lệ hết hàng</div>
            <div class="kpi-value">{oos_rate:.1f}%</div>
            <div class="kpi-sub">{out_of_stock:,} / {total:,} sản phẩm</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # KPI row 2 — kinh tế
    k5, k6, k7, k8 = st.columns(4)

    total_inventory = fdf[fdf["stock_status"]=="Con hang"]["sale_price"].sum()

    # HHI
    brand_shares = fdf["brand"].value_counts(normalize=True) * 100
    hhi = (brand_shares ** 2).sum()

    avg_saving = fdf["discount_amt"].mean()
    cv = fdf["sale_price"].std() / fdf["sale_price"].mean() * 100

    with k5:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Tổng giá trị kho</div>
            <div class="kpi-value">{total_inventory/1e9:.1f}B</div>
            <div class="kpi-sub">tỷ VNĐ (còn hàng)</div>
        </div>""", unsafe_allow_html=True)
    with k6:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">HHI Index</div>
            <div class="kpi-value">{hhi:.0f}</div>
            <div class="kpi-sub">Tập trung vừa phải</div>
        </div>""", unsafe_allow_html=True)
    with k7:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Tiết kiệm TB / SP</div>
            <div class="kpi-value">{avg_saving/1e3:.0f}K</div>
            <div class="kpi-sub">nghìn VNĐ</div>
        </div>""", unsafe_allow_html=True)
    with k8:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Hệ số biến động giá (CV)</div>
            <div class="kpi-value">{cv:.1f}%</div>
            <div class="kpi-sub">Coefficient of Variation</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="section-header">Phân phối thị trường</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        brand_dist = fdf["brand"].value_counts().reset_index()
        brand_dist.columns = ["brand", "count"]
        fig = px.bar(brand_dist, x="brand", y="count",
                     color="brand", title="Số lượng sản phẩm theo hãng",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False, height=320,
                          plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(t=40,b=20,l=20,r=20),
                          font=dict(color="#111111", size=12),
                          title=dict(font=dict(color="#111111", size=14)),
                          xaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")),
                          yaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Phân khúc giá
        fdf2 = fdf.copy()
        fdf2["price_segment"] = pd.cut(fdf2["sale_price"],
            bins=[0,32e6,37e6,41e6,float("inf")],
            labels=["Tầm trung\n28-32tr","Khá\n32-37tr","Cao cấp\n37-41tr","Flagship\n41tr+"])
        seg = fdf2["price_segment"].value_counts().sort_index().reset_index()
        seg.columns = ["segment","count"]
        fig2 = px.pie(seg, names="segment", values="count",
                      title="Cơ cấu thị trường theo phân khúc giá",
                      color_discrete_sequence=["#3b82f6","#60a5fa","#93c5fd","#bfdbfe"])
        fig2.update_traces(textfont=dict(color="#111111"), hovertemplate="%{label}<extra></extra>")
        fig2.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(t=40,b=20,l=20,r=20),
                          font=dict(color="#111111", size=12),
                          title=dict(font=dict(color="#111111", size=14)),
                          legend=dict(font=dict(color="#111111")))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> HHI = {:.0f} cho thấy thị trường ở mức tập trung vừa phải (1500–2500) — cạnh tranh có tính cân bằng giữa 6 thương hiệu, chưa có dấu hiệu độc quyền. CV = {:.1f}% phản ánh thị trường tập trung vào phân khúc cận cao cấp với biên độ giá hẹp.</div>'.format(hhi, cv), unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — PHÂN TÍCH GIÁ
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Chiến lược giá theo thương hiệu</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Discount rate & on_sale_rate
        brand_disc = fdf.groupby("brand").agg(
            avg_discount_pct=("discount_pct","mean"),
            on_sale_rate=("discount_amt", lambda x: (x>0).mean()*100),
            avg_saving=("discount_amt","mean"),
            total=("brand","count")
        ).round(2).reset_index()

        fig = px.bar(brand_disc.sort_values("on_sale_rate", ascending=True),
                     x="on_sale_rate", y="brand", orientation="h",
                     title="Tỷ lệ sản phẩm đang giảm giá (%) theo hãng",
                     color="on_sale_rate",
                     color_continuous_scale=["#eff6ff","#bfdbfe","#3b82f6"],
                     text="on_sale_rate")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                          textfont=dict(color="#111111"))
        fig.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False, margin=dict(t=40,b=20,l=20,r=60),
                          font=dict(color="#111111", size=12),
                          title=dict(font=dict(color="#111111", size=14)),
                          xaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")),
                          yaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Avg saving per brand
        fig2 = px.bar(brand_disc.sort_values("avg_saving", ascending=True),
                      x="avg_saving", y="brand", orientation="h",
                      title="Tiết kiệm trung bình (VNĐ) theo hãng",
                      color="avg_saving",
                      color_continuous_scale=["#f0fdf4","#86efac","#16a34a"],
                      text="avg_saving")
        fig2.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                          textfont=dict(color="#111111"))
        fig2.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False, margin=dict(t=40,b=20,l=20,r=80),
                           font=dict(color="#111111", size=12),
                           title=dict(font=dict(color="#111111", size=14)),
                           xaxis=dict(title=dict(font=dict(color="#111111")),
                                      tickfont=dict(color="#111111")),
                           yaxis=dict(title=dict(font=dict(color="#111111")),
                                      tickfont=dict(color="#111111")))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Phân tích giá theo RAM & Storage</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)

    with c3:
        ram_price = fdf.groupby("ram").agg(
            avg_price=("sale_price","mean"),
            min_price=("sale_price","min"),
            max_price=("sale_price","max"),
            std_price=("sale_price","std"),
            count=("ram","count")
        ).reset_index()
        ram_price["ram_num"] = ram_price["ram"].str.replace("GB","").astype(float)
        ram_price = ram_price.sort_values("ram_num")
        ram_price["avg_price_m"] = ram_price["avg_price"] / 1e6

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=ram_price["ram"], y=ram_price["avg_price_m"],
            mode="lines+markers+text",
            text=ram_price["avg_price_m"].apply(lambda x: f"{x:.1f}M"),
            textposition="top center",
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=10, color="#3b82f6"),
            textfont=dict(color="#111111"),
            name="Giá TB"
        ))
        fig3.add_trace(go.Scatter(
            x=ram_price["ram"], y=ram_price["max_price"]/1e6,
            mode="lines", line=dict(color="#93c5fd", dash="dot"), name="Giá cao nhất"
        ))
        fig3.add_trace(go.Scatter(
            x=ram_price["ram"], y=ram_price["min_price"]/1e6,
            mode="lines", line=dict(color="#bfdbfe", dash="dot"), name="Giá thấp nhất",
            fill="tonexty", fillcolor="rgba(59,130,246,0.08)"
        ))
        fig3.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                           yaxis_title="Triệu VNĐ", margin=dict(t=40,b=20,l=40,r=20),
                           title=dict(text="Giá trung bình theo RAM (triệu VNĐ)",
                                      font=dict(color="#111111", size=14)),
                           font=dict(color="#111111", size=12),
                           legend=dict(font=dict(color="#111111")),
                           xaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")),
                           yaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        storage_order = {"64GB":0,"128GB":1,"256GB":2,"512GB":3,"1TB":4}
        stor_price = fdf.groupby("storage").agg(
            avg_price=("sale_price","mean"),
            count=("storage","count")
        ).reset_index()
        stor_price["order"] = stor_price["storage"].map(storage_order)
        stor_price = stor_price.sort_values("order")
        stor_price["avg_price_m"] = stor_price["avg_price"] / 1e6

        fig4 = px.bar(stor_price, x="storage", y="avg_price_m",
                      title="Giá trung bình theo Storage (triệu VNĐ)",
                      color="avg_price_m", color_continuous_scale=["#faf5ff","#c4b5fd","#7c3aed"],
                      text="avg_price_m")
        fig4.update_traces(texttemplate="%{text:.1f}M", textposition="outside",
                          textfont=dict(color="#111111"))
        fig4.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False, margin=dict(t=40,b=20,l=40,r=20),
                           yaxis_title="Triệu VNĐ",
                           font=dict(color="#111111", size=12),
                           title=dict(font=dict(color="#111111", size=14)),
                           xaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")),
                           yaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")))
        st.plotly_chart(fig4, use_container_width=True)

    # Price distribution per brand — box plot style with plotly
    st.markdown('<div class="section-header">Phân phối giá theo hãng</div>', unsafe_allow_html=True)
    fig5 = px.box(fdf, x="brand", y="sale_price", color="brand",
                  title="Phân phối giá bán theo thương hiệu (VNĐ)",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig5.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                       showlegend=False, yaxis_title="Giá bán (VNĐ)",
                       margin=dict(t=40,b=20,l=60,r=20),
                       font=dict(color="#111111", size=12),
                       title=dict(font=dict(color="#111111", size=14)),
                       xaxis=dict(title=dict(font=dict(color="#111111")),
                                  tickfont=dict(color="#111111")),
                       yaxis=dict(title=dict(font=dict(color="#111111")),
                                  tickfont=dict(color="#111111")))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Xiaomi có tỷ lệ sản phẩm đang giảm giá cao nhất (77.7%) — chiến lược phủ rộng khuyến mãi để kích cầu. Apple thấp nhất (70%) nhưng mức tiết kiệm tuyệt đối lớn — giảm ít nhưng giảm mạnh để duy trì định vị cao cấp.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — SO SÁNH NGUỒN
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">CellphoneS vs Thế Giới Di Động</div>', unsafe_allow_html=True)

    src = fdf.groupby(["source","brand"]).agg(
        total=("brand","count"),
        avg_price=("sale_price","mean"),
        avg_discount=("discount_pct","mean"),
        avg_saving=("discount_amt","mean"),
        price_std=("sale_price","std")
    ).reset_index()

    c1, c2 = st.columns(2)

    with c1:
        fig = px.line(src, x="brand", y="total", color="source",
                      markers=True, title="Phủ sóng sản phẩm theo hãng",
                      color_discrete_map={"CellphoneS":"#3b82f6","TGDD":"#f59e0b"})
        fig.update_traces(line_width=2.5, marker_size=9)
        fig.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(t=40,b=20,l=40,r=20), yaxis_title="Số sản phẩm",
                          font=dict(color="#111111", size=12),
                          title=dict(font=dict(color="#111111", size=14)),
                          legend=dict(font=dict(color="#111111")),
                          xaxis=dict(title=dict(font=dict(color="#111111")),
                                    tickfont=dict(color="#111111")),
                          yaxis=dict(title=dict(font=dict(color="#111111")),
                                    tickfont=dict(color="#111111")))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Heatmap saving
        hm = src.pivot(index="source", columns="brand", values="avg_saving") / 1000
        fig2 = px.imshow(hm, text_auto=".0f",
                         title="Mức tiết kiệm TB (nghìn VNĐ) — Brand × Source",
                         color_continuous_scale=["#f0f9ff","#93c5fd","#1e40af"],
                         aspect="auto")
        fig2.update_traces(textfont=dict(color="#111111"))
        fig2.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(t=40,b=20,l=80,r=20),
                          font=dict(color="#111111", size=12),
                          title=dict(font=dict(color="#111111", size=14)),
                          xaxis=dict(title=dict(font=dict(color="#111111")),
                                    tickfont=dict(color="#111111")),
                          yaxis=dict(title=dict(font=dict(color="#111111")),
                                    tickfont=dict(color="#111111")))
        st.plotly_chart(fig2, use_container_width=True)

    # Grouped bar — avg price by source × brand
    fig3 = px.bar(src, x="brand", y="avg_price", color="source", barmode="group",
                  title="Giá trung bình theo hãng × nguồn (VNĐ)",
                  color_discrete_map={"CellphoneS":"#3b82f6","TGDD":"#f59e0b"},
                  text="avg_price")
    fig3.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                       textfont=dict(color="#111111"))
    fig3.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=40,b=20,l=60,r=20), yaxis_title="Giá (VNĐ)",
                       font=dict(color="#111111", size=12),
                       title=dict(font=dict(color="#111111", size=14)),
                       legend=dict(font=dict(color="#111111")),
                       xaxis=dict(title=dict(font=dict(color="#111111")),
                                 tickfont=dict(color="#111111")),
                       yaxis=dict(title=dict(font=dict(color="#111111")),
                                  tickfont=dict(color="#111111")))
    st.plotly_chart(fig3, use_container_width=True)

    # Summary table
    st.markdown('<div class="section-header">Bảng tổng hợp chỉ số theo nguồn</div>', unsafe_allow_html=True)
    src_sum = fdf.groupby("source").agg(
        Tổng_SP=("source","count"),
        Giá_TB=("sale_price", lambda x: f"{x.mean()/1e6:.2f}M"),
        Discount_TB=("discount_pct", lambda x: f"{x.mean():.2f}%"),
        Tiết_kiệm_TB=("discount_amt", lambda x: f"{x.mean()/1e3:.0f}K"),
    ).reset_index().rename(columns={"source":"Nguồn"})
    st.dataframe(src_sum, use_container_width=True, hide_index=True)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> TGDD phủ rộng hơn ở Realme, Xiaomi, Oppo (phân khúc tầm trung đại chúng). CellphoneS tập trung vào Samsung & Apple (phân khúc cao cấp). Apple tại TGDD có mức tiết kiệm cao nhất 1.293K VNĐ — TGDD dùng Apple như công cụ thu hút khách hàng cao cấp.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — TỒN KHO & TÌNH TRẠNG
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Tình trạng tồn kho</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Treemap stock
        tree = fdf.groupby(["brand","stock_status"]).size().reset_index(name="count")
        fig = px.treemap(tree, path=["brand","stock_status"], values="count",
                         title="Treemap tồn kho theo hãng",
                         color="count", color_continuous_scale=["#eff6ff","#bfdbfe","#1e40af"])
        fig.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white",
                         margin=dict(t=40,b=10,l=10,r=10),
                         font=dict(color="#111111", size=12),
                         title=dict(font=dict(color="#111111", size=14)))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Out of stock rate per brand
        oos = fdf.groupby("brand").apply(
            lambda x: pd.Series({
                "oos_rate": (x["stock_status"]=="Het hang").mean()*100,
                "total": len(x)
            })
        ).reset_index()
        fig2 = px.bar(oos.sort_values("oos_rate", ascending=False),
                      x="brand", y="oos_rate",
                      title="Tỷ lệ hết hàng (%) theo hãng",
                      color="oos_rate", color_continuous_scale=["#fef2f2","#fca5a5","#dc2626"],
                      text="oos_rate")
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                          textfont=dict(color="#111111"))
        fig2.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False, margin=dict(t=40,b=20,l=40,r=20),
                           yaxis_title="%",
                           font=dict(color="#111111", size=12),
                           title=dict(font=dict(color="#111111", size=14)),
                           xaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")),
                           yaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Phân tích tình trạng máy</div>', unsafe_allow_html=True)

    cond = fdf.groupby("phone_condition").agg(
        total=("phone_condition","count"),
        avg_price=("sale_price","mean"),
        avg_saving=("discount_amt","mean"),
        contribution=("phone_condition","count")
    ).reset_index()
    cond["contribution_pct"] = cond["total"] / cond["total"].sum() * 100

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.pie(cond, names="phone_condition", values="total",
                      title="Tỷ lệ sản phẩm theo tình trạng máy",
                      color="phone_condition",
                      color_discrete_map={
                          "Moi 100%": "#60a5fa",
                          "Da kich hoat": "#f59e0b",
                          "Hang trung bay": "#86efac"
                      })
        fig3.update_traces(textfont=dict(color="#111111"))
        fig3.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(t=40,b=20,l=20,r=20),
                          font=dict(color="#111111", size=12),
                          title=dict(font=dict(color="#111111", size=14)),
                          legend=dict(font=dict(color="#111111")))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = px.bar(cond, x="phone_condition", y="avg_price",
                      title="Giá trung bình theo tình trạng máy (VNĐ)",
                      color="phone_condition",
                      color_discrete_sequence=["#3b82f6","#f59e0b","#10b981"],
                      text="avg_price")
        fig4.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                          textfont=dict(color="#111111"))
        fig4.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                           showlegend=False, margin=dict(t=40,b=20,l=60,r=20),
                           font=dict(color="#111111", size=12),
                           title=dict(font=dict(color="#111111", size=14)),
                           xaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")),
                           yaxis=dict(title=dict(font=dict(color="#111111")),
                                     tickfont=dict(color="#111111")))
        st.plotly_chart(fig4, use_container_width=True)

    # Funnel
    st.markdown('<div class="section-header">Phễu tình trạng hàng theo phân khúc giá</div>', unsafe_allow_html=True)
    fdf3 = fdf.copy()
    fdf3["price_segment"] = pd.cut(fdf3["sale_price"],
        bins=[0,32e6,37e6,41e6,float("inf")],
        labels=["Tầm trung\n(28-32tr)", "Khá\n(32-37tr)", "Cao cấp\n(37-41tr)", "Flagship\n(41tr+)"])
    funnel = fdf3.groupby("price_segment").agg(
        total=("sale_price","count"),
        in_stock=("stock_status", lambda x: (x=="Con hang").sum())
    ).reset_index()
    funnel["out_stock"] = funnel["total"] - funnel["in_stock"]
    funnel["avail_rate"] = (funnel["in_stock"] / funnel["total"] * 100).round(1)
    # Sort by total descending so largest is at TOP of funnel
    funnel = funnel.sort_values("total", ascending=False).reset_index(drop=True)

    fig5 = go.Figure(go.Funnel(
        y=funnel["price_segment"].astype(str),
        x=funnel["total"],
        textinfo="value+percent initial",
        marker_color=["#1e40af","#3b82f6","#60a5fa","#93c5fd"],
        textfont=dict(color="#111111")
    ))
    fig5.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(t=40,b=20,l=20,r=20),
                       title=dict(text="Phễu phân khúc giá thị trường",
                                  font=dict(color="#111111", size=14)),
                       font=dict(color="#111111", size=12),
                       yaxis=dict(tickfont=dict(color="#111111")))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Phân khúc 32-37tr có availability rate thấp nhất (82.7%) dù có nhiều sản phẩm nhất — tín hiệu cho thấy đây là vùng cạnh tranh nóng nhất, nhu cầu vượt cung. Máy trưng bày và đã kích hoạt chiếm ~10% thị trường, thể hiện phân khúc secondhand đang tồn tại song song.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 — DỮ LIỆU & CRUD
# ══════════════════════════════════════════════

display_cols = ["id","phone_name","brand","ram","storage",
                "original_price","sale_price","discount_pct",
                "stock_status","phone_condition","source","crawl_date"]

# Init crud_df từ TOÀN BỘ df (không filter) — đảm bảo luôn đủ 1500+ records
if "crud_df" not in st.session_state:
    st.session_state.crud_df = df.copy()

# Dùng key trong session_state để giữ tab active sau khi CRUD
if "crud_tab" not in st.session_state:
    st.session_state.crud_tab = 0
if "crud_msg" not in st.session_state:
    st.session_state.crud_msg = None

with tab5:
    st.markdown('<div class="section-header">Truy vấn & Thao tác dữ liệu</div>', unsafe_allow_html=True)

    # Hiển thị message từ lần thao tác trước (giữ nguyên tab)
    if st.session_state.crud_msg:
        msg_type, msg_text = st.session_state.crud_msg
        if msg_type == "success":
            st.markdown(f'<div class="crud-success">✅ {msg_text}</div>', unsafe_allow_html=True)
        elif msg_type == "warning":
            st.warning(msg_text)
        st.session_state.crud_msg = None

    sub1, sub2, sub3 = st.tabs(["🔍 Tìm kiếm", "✏️ Chỉnh sửa", "📥 Xuất dữ liệu"])

    # ── SUB TAB 1: TÌM KIẾM ──
    with sub1:
        sc1, sc2, sc3 = st.columns(3)
        search_name   = sc1.text_input("Tên sản phẩm", placeholder="vd: iPhone 15")
        search_brand  = sc2.selectbox("Hãng", ["Tất cả"] + sorted(st.session_state.crud_df["brand"].dropna().unique().tolist()))
        search_source = sc3.selectbox("Nguồn", ["Tất cả"] + sorted(st.session_state.crud_df["source"].dropna().unique().tolist()))

        result = st.session_state.crud_df.copy()
        if search_name:
            result = result[result["phone_name"].str.contains(search_name, case=False, na=False)]
        if search_brand != "Tất cả":
            result = result[result["brand"] == search_brand]
        if search_source != "Tất cả":
            result = result[result["source"] == search_source]

        st.markdown(f"**{len(result):,} kết quả** / tổng {len(st.session_state.crud_df):,} sản phẩm")
        show_cols = [c for c in display_cols if c in result.columns]
        st.dataframe(result[show_cols].reset_index(drop=True),
                     use_container_width=True, height=460)

    # ── SUB TAB 2: CRUD ──
    with sub2:
        st.markdown('<div class="crud-info">💡 Thao tác được lưu trong session. Sau mỗi thao tác trang <b>không reload</b> — dữ liệu cập nhật ngay bên dưới.</div>', unsafe_allow_html=True)

        crud_col1, crud_col2 = st.columns([1, 2])

        with crud_col1:
            action = st.radio("Chọn thao tác", ["➕ Thêm", "✏️ Sửa", "🗑️ Xóa"], label_visibility="collapsed")

        with crud_col2:

            if action == "➕ Thêm":
                with st.form("add_form", clear_on_submit=True):
                    st.markdown("**Thêm sản phẩm mới**")
                    fc1, fc2 = st.columns(2)
                    new_name  = fc1.text_input("Tên sản phẩm *")
                    new_brand = fc2.selectbox("Hãng", sorted(df["brand"].dropna().unique()))
                    new_ram   = fc1.selectbox("RAM", ["4GB","6GB","8GB","12GB","16GB"])
                    new_stor  = fc2.selectbox("Storage", ["64GB","128GB","256GB","512GB","1TB"])
                    new_orig  = fc1.number_input("Giá gốc (VNĐ)", min_value=0, value=35000000, step=500000)
                    new_sale  = fc2.number_input("Giá bán (VNĐ)", min_value=0, value=34000000, step=500000)
                    new_stock = fc1.selectbox("Tình trạng kho", ["Con hang","Het hang"])
                    new_cond  = fc2.selectbox("Tình trạng máy", ["Moi 100%","Da kich hoat","Hang trung bay"])
                    new_src   = st.selectbox("Nguồn", ["CellphoneS","TGDD"])
                    submitted = st.form_submit_button("➕ Thêm sản phẩm", type="primary", use_container_width=True)
                    if submitted:
                        if not new_name.strip():
                            st.session_state.crud_msg = ("warning", "Vui lòng nhập tên sản phẩm.")
                        else:
                            disc = new_orig - new_sale
                            new_row = {
                                "id": f"PROD_NEW_{len(st.session_state.crud_df)+1}",
                                "phone_name": new_name.strip(),
                                "brand": new_brand, "model": new_brand,
                                "ram": new_ram, "storage": new_stor,
                                "original_price": new_orig, "sale_price": new_sale,
                                "stock_status": new_stock, "phone_condition": new_cond,
                                "source": new_src,
                                "crawl_date": pd.Timestamp.now().date(),
                                "discount_amt": disc,
                                "discount_pct": round(disc/new_orig*100, 2) if new_orig > 0 else 0,
                                "ram_num": float(new_ram.replace("GB",""))
                            }
                            st.session_state.crud_df = pd.concat(
                                [st.session_state.crud_df, pd.DataFrame([new_row])],
                                ignore_index=True
                            )
                            st.session_state.crud_msg = ("success", f"Đã thêm: {new_name} | Tổng: {len(st.session_state.crud_df):,} sản phẩm")
                            st.rerun()

            elif action == "✏️ Sửa":
                st.markdown("**Sửa thông tin sản phẩm**")
                prod_id = st.text_input("Product ID cần sửa", placeholder="vd: PROD_CEL_100002")
                if prod_id.strip():
                    mask = st.session_state.crud_df["id"] == prod_id.strip()
                    match = st.session_state.crud_df[mask]
                    if len(match):
                        row = match.iloc[0]
                        st.dataframe(match[["id","phone_name","brand","sale_price","stock_status"]],
                                     use_container_width=True, hide_index=True)
                        with st.form("edit_form"):
                            ec1, ec2 = st.columns(2)
                            new_price  = ec1.number_input("Giá bán mới (VNĐ)",
                                                           value=int(row["sale_price"]), step=100000)
                            new_status = ec2.selectbox("Tình trạng kho", ["Con hang","Het hang"],
                                                        index=0 if row["stock_status"]=="Con hang" else 1)
                            new_cond2  = ec1.selectbox("Tình trạng máy",
                                                        ["Moi 100%","Da kich hoat","Hang trung bay"],
                                                        index=["Moi 100%","Da kich hoat","Hang trung bay"].index(row["phone_condition"]) if row["phone_condition"] in ["Moi 100%","Da kich hoat","Hang trung bay"] else 0)
                            save = st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True)
                            if save:
                                st.session_state.crud_df.loc[mask, "sale_price"]     = new_price
                                st.session_state.crud_df.loc[mask, "stock_status"]   = new_status
                                st.session_state.crud_df.loc[mask, "phone_condition"]= new_cond2
                                st.session_state.crud_df.loc[mask, "discount_amt"]   = st.session_state.crud_df.loc[mask, "original_price"] - new_price
                                st.session_state.crud_msg = ("success", f"Đã cập nhật {prod_id.strip()}")
                                st.rerun()
                    else:
                        st.warning(f"Không tìm thấy ID: {prod_id}")

            elif action == "🗑️ Xóa":
                st.markdown("**Xóa sản phẩm**")
                del_id = st.text_input("Product ID cần xóa", placeholder="vd: PROD_CEL_100002")
                if del_id.strip():
                    mask = st.session_state.crud_df["id"] == del_id.strip()
                    match = st.session_state.crud_df[mask]
                    if len(match):
                        st.dataframe(match[["id","phone_name","brand","sale_price","stock_status"]],
                                     use_container_width=True, hide_index=True)
                        with st.form("del_form"):
                            confirmed = st.form_submit_button("🗑️ Xác nhận xóa", type="primary", use_container_width=True)
                            if confirmed:
                                name_deleted = match["phone_name"].iloc[0]
                                st.session_state.crud_df = st.session_state.crud_df[~mask].reset_index(drop=True)
                                st.session_state.crud_msg = ("success", f"Đã xóa: {name_deleted} | Còn lại: {len(st.session_state.crud_df):,} sản phẩm")
                                st.rerun()
                    else:
                        st.warning(f"Không tìm thấy ID: {del_id}")

        # Bảng dữ liệu hiện tại — luôn hiển thị phía dưới
        st.markdown("---")
        st.markdown(f"**📋 Dữ liệu hiện tại: {len(st.session_state.crud_df):,} sản phẩm**")
        show_cols2 = [c for c in display_cols if c in st.session_state.crud_df.columns]
        st.dataframe(
            st.session_state.crud_df[show_cols2].reset_index(drop=True),
            use_container_width=True, height=380
        )

    # ── SUB TAB 3: XUẤT DỮ LIỆU ──
    with sub3:
        st.markdown("#### Xuất toàn bộ dữ liệu (bao gồm thay đổi CRUD)")

        export_source = st.radio(
            "Xuất từ",
            ["Dữ liệu hiện tại (sau CRUD)", "Dữ liệu đã lọc (sidebar filter)"],
            horizontal=True
        )

        if export_source == "Dữ liệu hiện tại (sau CRUD)":
            export_df = st.session_state.crud_df.copy()
        else:
            export_df = fdf.copy()

        avail_cols = export_df.columns.tolist()
        default_exp = [c for c in display_cols if c in avail_cols]
        export_cols = st.multiselect("Chọn cột xuất", avail_cols, default=default_exp)
        export_df_out = export_df[export_cols] if export_cols else export_df

        st.markdown(f"**{len(export_df_out):,} dòng × {len(export_cols)} cột**")

        # Preview
        with st.expander("Xem trước 10 dòng đầu"):
            st.dataframe(export_df_out.head(10), use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            csv_bytes = export_df_out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Tải CSV", csv_bytes,
                "phones_data.csv", "text/csv",
                use_container_width=True
            )
        with col_b:
            json_bytes = export_df_out.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")
            st.download_button(
                "📥 Tải JSON", json_bytes,
                "phones_data.json", "application/json",
                use_container_width=True
            )