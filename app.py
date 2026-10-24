import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import datetime as dt

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Product Demand Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. COLOUR PALETTE
# ==================================================

BG = "#F3F6FA"
WHITE = "#FFFFFF"
NAVY = "#17324D"
TEAL = "#0D9488"
BLUE = "#4776C5"
PURPLE = "#8972C8"
TEXT = "#26384A"
MUTED = "#64748B"
BORDER = "#E2E8F0"
GRID = "#E9EEF4"

# ==================================================
# 3. LIGHT THEME AND ALIGNMENT
# ==================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background-color: {BG};
    }}

    .block-container {{
        max-width: 1500px;
        padding: 1.8rem 2rem 3rem 2rem;
    }}

    [data-testid="stSidebar"] {{
        background-color: {WHITE};
        border-right: 1px solid {BORDER};
    }}

    h1, h2, h3 {{
        color: {NAVY} !important;
        letter-spacing: -0.3px;
    }}

    p, label, .stMarkdown {{
        color: {TEXT};
    }}

    [data-testid="stMetric"] {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 120px;
        box-shadow: 0 2px 6px rgba(23, 50, 77, 0.035);
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
        font-size: 0.88rem;
    }}

    [data-testid="stMetricValue"] {{
        color: {NAVY} !important;
        font-weight: 700;
    }}

    [data-testid="stMetricDelta"] {{
        color: {TEAL} !important;
    }}

    /* FIX 1: the chart card caused the inner scrollbar and clipped toolbar.
       - padding is removed (the figure has its own margins)
       - box-sizing makes border + size fit inside the container
       - overflow hidden removes the scrollbar */
    [data-testid="stPlotlyChart"] {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 0;
        box-sizing: border-box;
        overflow: hidden !important;
        box-shadow: 0 2px 6px rgba(23, 50, 77, 0.025);
    }}

    [data-testid="stPlotlyChart"] > div {{
        width: 100% !important;
        box-sizing: border-box;
        overflow: hidden !important;
    }}

    [data-testid="stDataFrame"] {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        overflow: hidden;
    }}

    [data-testid="stVerticalBlock"] > div {{
        min-width: 0;
    }}

    .hero {{
        background: linear-gradient(115deg, #FFFFFF 0%, #E5F5F3 100%);
        border: 1px solid #D5EAE7;
        border-left: 5px solid {TEAL};
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }}

    .hero-title {{
        color: {NAVY};
        font-size: 30px;
        font-weight: 750;
        line-height: 1.3;
        margin-bottom: 8px;
    }}

    .hero-subtitle {{
        color: {MUTED};
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 0;
    }}

    .summary-panel {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 18px 22px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 6px rgba(23, 50, 77, 0.025);
    }}

    .summary-title {{
        color: {NAVY};
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 6px;
    }}

    .summary-item {{
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-top: 1px solid {BORDER};
    }}

    .summary-label {{
        color: {MUTED};
        font-size: 0.88rem;
        margin-bottom: 2px;
    }}

    .summary-value {{
        color: {NAVY};
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.2;
    }}

    .section-caption {{
        color: {MUTED};
        font-size: 14px;
        margin-top: -8px;
        margin-bottom: 16px;
    }}

    div.stButton > button {{
        background-color: {TEAL};
        color: white;
        border: 1px solid {TEAL};
        border-radius: 8px;
        font-weight: 600;
    }}

    div.stButton > button:hover {{
        background-color: #0F766E;
        color: white;
        border-color: #0F766E;
    }}

    hr {{
        border-color: {BORDER};
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 4. LOAD DATA
# ==================================================

DATA_PATH = Path(__file__).parent / "cleaned_product_demand.csv"


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    required = [
        "Product_Code",
        "Warehouse",
        "Product_Category",
        "Date",
        "Order_Demand"
    ]

    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    # Remove formatting characters from demand values.
    # Parentheses are treated as formatting, not as negative values.
    data["Order_Demand"] = (
        data["Order_Demand"]
        .astype(str)
        .str.replace(r"[(),]", "", regex=True)
        .str.strip()
    )

    data["Order_Demand"] = pd.to_numeric(
        data["Order_Demand"], errors="coerce"
    )

    data = data.dropna(
        subset=[
            "Date",
            "Order_Demand",
            "Product_Code",
            "Warehouse",
            "Product_Category"
        ]
    ).copy()

    return data


@st.cache_data
def compute_findings(data):
    """Key findings computed on the FULL dataset (not the date filter),
    so they match the README and do not change with the slider."""
    by_product = (
        data.groupby("Product_Code")["Order_Demand"]
        .sum()
        .sort_values(ascending=False)
    )
    total = by_product.sum()
    cum_share = by_product.cumsum() / total

    # Number of products needed to reach 80% of total demand
    n80 = int((cum_share < 0.80).sum()) + 1
    top10_share = by_product.head(10).sum() / total

    by_cat = (
        data.groupby("Product_Category")["Order_Demand"]
        .sum()
        .sort_values(ascending=False)
    )
    by_wh = (
        data.groupby("Warehouse")["Order_Demand"]
        .sum()
        .sort_values(ascending=False)
    )

    # Biggest month-over-month jump in number of records (data coverage)
    monthly_records = data.set_index("Date")["Order_Demand"].resample("MS").size()
    prev = monthly_records.shift(1)
    ratio = (monthly_records / prev).where(prev > 0)

    jump = None
    if ratio.notna().any():
        jump_month = ratio.idxmax()
        jump = {
            "month": jump_month,
            "prev_month": jump_month - pd.offsets.MonthBegin(1),
            "prev_records": int(prev.loc[jump_month]),
            "records": int(monthly_records.loc[jump_month]),
        }

    return {
        "n_products": len(by_product),
        "n80": n80,
        "pct80": n80 / len(by_product),
        "top10_share": top10_share,
        "top_cat": by_cat.index[0],
        "top_cat_share": by_cat.iloc[0] / total,
        "top_wh": by_wh.index[0],
        "top_wh_share": by_wh.iloc[0] / total,
        "jump": jump,
    }


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        "Dataset not found. Place cleaned_product_demand.csv "
        "in the same folder as this Python file."
    )
    st.stop()
except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

if df.empty:
    st.error("No usable records were found in the dataset.")
    st.stop()

# ==================================================
# 5. CONSISTENT CHART STYLING
# ==================================================

# Shared plotly config: keeps the toolbar from overlapping titles
PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}


def style_chart(fig, height=380):
    fig.update_layout(
        height=height,
        autosize=True,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Arial, sans-serif",
            color=TEXT,
            size=12
        ),
        title=dict(
            font=dict(size=17, color=NAVY),
            x=0.02,
            xanchor="left"
        ),
        # FIX 2: slightly larger bottom margin so axis titles never
        # touch the card edge
        margin=dict(l=20, r=25, t=65, b=50),
        hoverlabel=dict(
            bgcolor=NAVY,
            font_color=WHITE
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(color=TEXT)
        )
    )

    fig.update_xaxes(
        gridcolor=GRID,
        zerolinecolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
        title_standoff=10,
        automargin=True
    )

    fig.update_yaxes(
        gridcolor=GRID,
        zerolinecolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
        title_standoff=10,
        automargin=True
    )

    return fig


# ==================================================
# 6. HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Product Demand Analytics</div>
        <p class="hero-subtitle">
            Explore historical demand patterns, identify high-demand
            products, compare product categories, and analyse demand
            across warehouses.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 7. SIDEBAR FILTERS
# ==================================================

st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Adjust the date range to explore the data.")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# Default to 2012-2016 (earlier data is sparse, Jan 2017 is partial),
# clamped to the dates that actually exist in the dataset.
default_start = min(max(dt.date(2012, 1, 1), min_date), max_date)
default_end = max(min(dt.date(2016, 12, 31), max_date), min_date)

date_range = st.sidebar.date_input(
    "Date range",
    value=(default_start, default_end),
    min_value=min_date,
    max_value=max_date
)

st.sidebar.caption(
    "Defaults to 2012-2016. Data before late 2011 is sparse and "
    "January 2017 is a partial month."
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    if start_date > end_date:
        st.sidebar.error("Start date must not be after end date.")
        st.stop()

    filtered_df = df[
        (df["Date"].dt.date >= start_date) &
        (df["Date"].dt.date <= end_date)
    ].copy()

elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    selected_date = date_range[0]
    filtered_df = df[
        df["Date"].dt.date == selected_date
    ].copy()

else:
    filtered_df = df[
        df["Date"].dt.date == date_range
    ].copy()

st.sidebar.divider()
st.sidebar.metric("Filtered records", f"{len(filtered_df):,}")
st.sidebar.caption(f"Full dataset: {len(df):,} records")

if filtered_df.empty:
    st.warning("No records found for this date range. Select another range.")
    st.stop()

# ==================================================
# 8. KPI CARDS
# ==================================================

st.subheader("Overview")
st.caption("Key figures for the selected period.")

total_demand = filtered_df["Order_Demand"].sum()
unique_products = filtered_df["Product_Code"].nunique()
active_warehouses = filtered_df["Warehouse"].nunique()

monthly_totals = (
    filtered_df.assign(Month=filtered_df["Date"].dt.to_period("M"))
    .groupby("Month")["Order_Demand"]
    .sum()
)

peak_month = (
    monthly_totals.idxmax().strftime("%b %Y")
    if not monthly_totals.empty else "N/A"
)

k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.metric("Total Order Demand", f"{total_demand:,.0f}")

with k2:
    st.metric("Unique Products", f"{unique_products:,}")

with k3:
    st.metric("Peak Demand Month", peak_month)

with k4:
    st.metric("Active Warehouses", f"{active_warehouses:,}")

st.divider()

# ==================================================
# 8B. KEY FINDINGS (FULL DATASET)
# ==================================================

st.subheader("Key Findings")
st.caption(
    "Calculated on the full dataset, so these figures do not change "
    "with the date filter."
)

findings = compute_findings(df)

f1, f2, f3, f4 = st.columns(4, gap="medium")

with f1:
    st.metric(
        "Products driving 80% of demand",
        f"{findings['n80']:,}",
        delta=f"{findings['pct80']:.1%} of {findings['n_products']:,} products",
        delta_color="off"
    )

with f2:
    st.metric("Top 10 products' share", f"{findings['top10_share']:.1%}")

with f3:
    st.metric(
        f"Top category ({findings['top_cat']})",
        f"{findings['top_cat_share']:.1%}"
    )

with f4:
    st.metric(
        f"Top warehouse ({findings['top_wh']})",
        f"{findings['top_wh_share']:.1%}"
    )

st.divider()

# ==================================================
# 9. MONTHLY DEMAND TREND
# ==================================================

st.subheader("Demand Over Time")
st.caption("Track how recorded demand changes from month to month.")

monthly_demand = (
    filtered_df.set_index("Date")["Order_Demand"]
    .resample("MS")
    .sum()
    .rename("Order_Demand")
    .reset_index()
)

fig_trend = go.Figure()

fig_trend.add_trace(
    go.Scatter(
        x=monthly_demand["Date"],
        y=monthly_demand["Order_Demand"],
        mode="lines",
        name="Monthly demand",
        line=dict(color=TEAL, width=3),
        fill="tozeroy",
        fillcolor="rgba(13,148,136,0.10)",
        hovertemplate=(
            "%{x|%b %Y}<br>"
            "Demand: %{y:,.0f}<extra></extra>"
        )
    )
)

fig_trend.update_layout(
    title="Monthly Demand Trend",
    xaxis_title="Month",
    yaxis_title="Total Demand",
    showlegend=False
)

style_chart(fig_trend, 410)
st.plotly_chart(
    fig_trend,
    use_container_width=True,
    config=PLOT_CONFIG
)

st.divider()

# ==================================================
# 9B. DATA COVERAGE (FULL DATASET)
# ==================================================

st.subheader("Data Coverage")
st.caption(
    "Number of records per month versus average demand per record, "
    "across the full dataset."
)

coverage = (
    df.set_index("Date")["Order_Demand"]
    .resample("MS")
    .agg(Records="size", Avg_Demand="mean")
    .reset_index()
)

# Months with no records have no meaningful average
coverage.loc[coverage["Records"] == 0, "Avg_Demand"] = None

fig_cov = make_subplots(specs=[[{"secondary_y": True}]])

fig_cov.add_trace(
    go.Bar(
        x=coverage["Date"],
        y=coverage["Records"],
        name="Records per month",
        marker_color="rgba(71,118,197,0.55)",
        hovertemplate="%{x|%b %Y}<br>Records: %{y:,.0f}<extra></extra>"
    ),
    secondary_y=False
)

fig_cov.add_trace(
    go.Scatter(
        x=coverage["Date"],
        y=coverage["Avg_Demand"],
        name="Avg demand per record",
        mode="lines",
        line=dict(color=TEAL, width=3),
        hovertemplate="%{x|%b %Y}<br>Avg demand: %{y:,.0f}<extra></extra>"
    ),
    secondary_y=True
)

fig_cov.update_layout(
    title="Records per Month vs Average Demand per Record",
    legend=dict(orientation="h", y=1.08, x=0.02)
)
fig_cov.update_xaxes(title_text="Month")
fig_cov.update_yaxes(title_text="Records", secondary_y=False)
fig_cov.update_yaxes(
    title_text="Avg demand per record",
    secondary_y=True,
    showgrid=False
)

style_chart(fig_cov, 410)
st.plotly_chart(fig_cov, use_container_width=True, config=PLOT_CONFIG)

jump = findings["jump"]
if jump is not None:
    st.caption(
        f"Monthly records jump from {jump['prev_records']:,} in "
        f"{jump['prev_month'].strftime('%b %Y')} to {jump['records']:,} in "
        f"{jump['month'].strftime('%b %Y')}, while average demand per record "
        "stays broadly steady. This points to a change in data coverage "
        "rather than real demand growth."
    )

st.divider()

# ==================================================
# 10. PRODUCT DEMAND EXPLORER
# ==================================================

st.subheader("Product Demand Explorer")
st.caption("Select a product to view its historical demand pattern.")

product_totals = (
    filtered_df.groupby("Product_Code")["Order_Demand"]
    .sum()
    .sort_values(ascending=False)
)

product_options = product_totals.index.tolist()

selected_product = st.selectbox(
    "Select product",
    options=product_options,
    format_func=lambda p: f"{p} — {product_totals[p]:,.0f} demand"
)

product_df = filtered_df[
    filtered_df["Product_Code"] == selected_product
].copy()

product_monthly = (
    product_df.set_index("Date")["Order_Demand"]
    .resample("MS")
    .sum()
    .rename("Order_Demand")
    .reset_index()
)

PRODUCT_CHART_HEIGHT = 420

common_category = product_df["Product_Category"].mode()
common_category_name = (
    common_category.iloc[0] if not common_category.empty else "N/A"
)

left, right = st.columns([2, 1], gap="medium")

with left:
    fig_product = px.line(
        product_monthly,
        x="Date",
        y="Order_Demand",
        markers=True,
        title=f"Monthly Demand — {selected_product}"
    )

    fig_product.update_traces(
        line=dict(color=TEAL, width=3),
        marker=dict(color=BLUE, size=6)
    )

    fig_product.update_layout(
        xaxis_title="Month",
        yaxis_title="Demand",
        showlegend=False
    )

    style_chart(fig_product, PRODUCT_CHART_HEIGHT)
    st.plotly_chart(fig_product, use_container_width=True, config=PLOT_CONFIG)

with right:
    # One panel with the same top edge and the same height as the chart
    # card, so both sides start and end together. Written without blank
    # lines or indentation so Streamlit's markdown renders it as HTML.
    summary_items = [
        ("Total Demand", f"{product_df['Order_Demand'].sum():,.0f}"),
        ("Categories Recorded", f"{product_df['Product_Category'].nunique():,}"),
        ("Warehouses Recorded", f"{product_df['Warehouse'].nunique():,}"),
        ("Most Common Category", html.escape(str(common_category_name))),
    ]

    items_html = "".join(
        f'<div class="summary-item">'
        f'<div class="summary-label">{label}</div>'
        f'<div class="summary-value">{value}</div>'
        f'</div>'
        for label, value in summary_items
    )

    st.markdown(
        f'<div class="summary-panel" style="height:{PRODUCT_CHART_HEIGHT + 2}px">'
        f'<div class="summary-title">Product Summary</div>'
        f'{items_html}'
        f'</div>',
        unsafe_allow_html=True
    )

st.divider()

# ==================================================
# 11. PRODUCT PERFORMANCE
# ==================================================

st.subheader("Product Performance Analysis")
st.caption("Identify products and categories with the highest recorded demand.")

top_products = (
    filtered_df.groupby("Product_Code", as_index=False)["Order_Demand"]
    .sum()
    .nlargest(10, "Order_Demand")
    .sort_values("Order_Demand", ascending=True)
)

fig_top = px.bar(
    top_products,
    x="Order_Demand",
    y="Product_Code",
    orientation="h",
    title="Top 10 Products by Demand",
    text="Order_Demand"
)

fig_top.update_traces(
    marker_color=TEAL,
    texttemplate="%{text:,.0f}",
    textposition="outside",
    cliponaxis=False
)

fig_top.update_layout(
    xaxis_title="Total Demand",
    yaxis_title="Product Code"
)

style_chart(fig_top, 430)

# --- Category chart: top 10 categories + "Other" for readability ---
category_demand = (
    filtered_df.groupby("Product_Category", as_index=False)["Order_Demand"]
    .sum()
    .sort_values("Order_Demand", ascending=False)
)

TOP_N_CATEGORIES = 10
top_categories = category_demand.head(TOP_N_CATEGORIES).copy()
other_categories = category_demand.iloc[TOP_N_CATEGORIES:]

if not other_categories.empty:
    other_row = pd.DataFrame({
        "Product_Category": [f"Other ({len(other_categories)} categories)"],
        "Order_Demand": [other_categories["Order_Demand"].sum()]
    })
    category_plot = pd.concat([top_categories, other_row], ignore_index=True)
else:
    category_plot = top_categories

category_total = category_plot["Order_Demand"].sum()
category_plot["Share"] = category_plot["Order_Demand"] / category_total
category_plot["Label"] = category_plot.apply(
    lambda r: f"{r['Order_Demand']:,.0f} ({r['Share']:.1%})", axis=1
)

# Teal for named categories, muted grey for the "Other" bar
bar_colors = [
    MUTED if str(name).startswith("Other (") else TEAL
    for name in category_plot["Product_Category"]
]

fig_category = px.bar(
    category_plot,
    x="Order_Demand",
    y="Product_Category",
    orientation="h",
    title="Demand by Product Category (Top 10 + Other)",
    text="Label"
)

fig_category.update_traces(
    marker_color=bar_colors,
    textposition="outside",
    cliponaxis=False
)

fig_category.update_layout(
    xaxis_title="Total Demand",
    yaxis_title="Product Category",
    showlegend=False
)

style_chart(fig_category, 430)

# Largest category at the top, "Other" at the bottom
fig_category.update_yaxes(autorange="reversed")
# Extra right margin so the outside labels are not clipped
fig_category.update_layout(margin=dict(l=20, r=90, t=65, b=50))

# Both charts have identical heights and aligned column boundaries.
left, right = st.columns(2, gap="medium")

with left:
    st.plotly_chart(fig_top, use_container_width=True, config=PLOT_CONFIG)

with right:
    st.plotly_chart(fig_category, use_container_width=True, config=PLOT_CONFIG)

st.markdown("#### Top 10 Product Summary")

top_table = (
    filtered_df.groupby("Product_Code")
    .agg(
        Total_Demand=("Order_Demand", "sum"),
        Number_of_Records=("Order_Demand", "size"),
        Warehouses=("Warehouse", "nunique")
    )
    .sort_values("Total_Demand", ascending=False)
    .head(10)
    .reset_index()
)

top_table["Total_Demand"] = top_table["Total_Demand"].round(0).astype("int64")

st.dataframe(
    top_table,
    use_container_width=True,
    hide_index=True,
    height=380
)

st.divider()

# ==================================================
# 12. WAREHOUSE ANALYSIS
# ==================================================

st.subheader("Warehouse Analysis")
st.caption("Compare demand across warehouses and explore their product mix.")

warehouse_demand = (
    filtered_df.groupby("Warehouse", as_index=False)["Order_Demand"]
    .sum()
    .sort_values("Order_Demand", ascending=False)
)

warehouse_options = sorted(
    filtered_df["Warehouse"].unique().tolist()
)

# FIX 3: the selector now sits ABOVE the two columns (in its own narrow
# row), so both charts start at exactly the same height.
select_col, _spacer = st.columns([1, 2], gap="medium")

with select_col:
    selected_warehouse = st.selectbox(
        "Choose warehouse (for the chart on the right)",
        options=warehouse_options
    )

WH_CHART_HEIGHT = 420

left, right = st.columns(2, gap="medium")

with left:
    fig_wh = px.bar(
        warehouse_demand,
        x="Warehouse",
        y="Order_Demand",
        title="Total Demand by Warehouse",
        color="Warehouse",
        color_discrete_sequence=[TEAL, BLUE, PURPLE, "#D99A38", "#D977A8"]
    )

    fig_wh.update_layout(
        xaxis_title="Warehouse",
        yaxis_title="Total Demand",
        showlegend=False
    )

    style_chart(fig_wh, WH_CHART_HEIGHT)
    st.plotly_chart(fig_wh, use_container_width=True, config=PLOT_CONFIG)

with right:
    warehouse_products = (
        filtered_df[filtered_df["Warehouse"] == selected_warehouse]
        .groupby("Product_Code", as_index=False)["Order_Demand"]
        .sum()
        .nlargest(10, "Order_Demand")
        .sort_values("Order_Demand", ascending=True)
    )

    fig_wh_products = px.bar(
        warehouse_products,
        x="Order_Demand",
        y="Product_Code",
        orientation="h",
        title=f"Top Products — Warehouse {selected_warehouse}"
    )

    fig_wh_products.update_traces(marker_color=BLUE)

    fig_wh_products.update_layout(
        xaxis_title="Total Demand",
        yaxis_title="Product Code"
    )

    # Same height as the left chart so the cards end together
    style_chart(fig_wh_products, WH_CHART_HEIGHT)
    st.plotly_chart(
        fig_wh_products,
        use_container_width=True,
        config=PLOT_CONFIG
    )

st.divider()

# ==================================================
# 13. PRODUCT-WAREHOUSE HEATMAP
# ==================================================

st.subheader("Product Demand Across Warehouses")
st.caption(
    "Compare demand for the top 15 products across the warehouses "
    "where their demand was recorded."
)

top_15_codes = (
    filtered_df.groupby("Product_Code")["Order_Demand"]
    .sum()
    .nlargest(15)
    .index
)

heatmap_data = filtered_df[
    filtered_df["Product_Code"].isin(top_15_codes)
].pivot_table(
    index="Product_Code",
    columns="Warehouse",
    values="Order_Demand",
    aggfunc="sum",
    fill_value=0
)

heatmap_data = heatmap_data.loc[
    heatmap_data.sum(axis=1).sort_values(ascending=False).index
]

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns.astype(str),
        y=heatmap_data.index.astype(str),
        colorscale=[
            [0, "#F0F7F6"],
            [0.4, "#8DD9D0"],
            [0.75, "#2DB6A7"],
            [1, "#0F766E"]
        ],
        colorbar=dict(title="Demand"),
        hovertemplate=(
            "Product: %{y}<br>"
            "Warehouse: %{x}<br>"
            "Demand: %{z:,.0f}<extra></extra>"
        )
    )
)

fig_heatmap.update_layout(
    title="Top 15 Products Across Warehouses",
    xaxis_title="Warehouse",
    yaxis_title="Product Code"
)

style_chart(fig_heatmap, 520)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True,
    config=PLOT_CONFIG
)

# ==================================================
# 14. NOTES AND FOOTER
# ==================================================

st.divider()

st.subheader("Reading the Results")

st.markdown(
    """
    - **Key findings:** summarise demand concentration across the full dataset.
    - **Demand trend:** shows how historical recorded demand changes over time.
    - **Data coverage:** shows how many records exist each month, so jumps caused by data collection are not mistaken for demand growth.
    - **Product performance:** compares total recorded demand across products.
    - **Category analysis:** shows the top 10 categories; the rest are grouped as "Other".
    - **Warehouse analysis:** compares demand recorded at each warehouse.
    - **Heatmap:** highlights differences in product demand across warehouses.
    """
)

st.warning(
    "Data limitation: values originally written in brackets, such as (500), "
    "are treated as positive 500. Their original meaning has not been verified, "
    "so demand totals and rankings are provisional. The dataset does not provide "
    "current inventory levels; historical demand alone cannot establish how much "
    "stock a warehouse should hold."
)

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:{MUTED};
        padding:24px 0 8px 0;
        font-size:13px;
        border-top:1px solid {BORDER};
        margin-top:24px;
    ">
        Product Demand Analytics
        &nbsp;·&nbsp; Python
        &nbsp;·&nbsp; Pandas
        &nbsp;·&nbsp; Plotly
        &nbsp;·&nbsp; Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
