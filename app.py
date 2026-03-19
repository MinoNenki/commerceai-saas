import os
import json
import base64
import random
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
with st.expander("DEBUG KEY"):
    key_env = os.getenv("OPENAI_API_KEY")
    key_secret = None
    try:
        if "OPENAI_API_KEY" in st.secrets:
            key_secret = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    st.write("ENV exists:", key_env is not None)
    st.write("SECRETS exists:", key_secret is not None)

    if key_env:
        st.write("ENV prefix:", key_env[:12])
        st.write("ENV suffix:", key_env[-6:])

    if key_secret:
        st.write("SECRETS prefix:", key_secret[:12])
        st.write("SECRETS suffix:", key_secret[-6:])
from PIL import Image

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ============================================================
# BOOTSTRAP
# ============================================================
if load_dotenv is not None:
    load_dotenv()

st.set_page_config(
    page_title="CommerceAI Production MVP",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = None
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []
if "uploaded_image_preview" not in st.session_state:
    st.session_state.uploaded_image_preview = None
if "selected_store_name" not in st.session_state:
    st.session_state.selected_store_name = "CommerceAI Flagship Store"
if "selected_plan" not in st.session_state:
    st.session_state.selected_plan = "Scale"
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False


# ============================================================
# THEME
# ============================================================
THEMES = [
    {
        "name": "Aurora Luxe",
        "hero": "linear-gradient(135deg, rgba(59,130,246,0.40), rgba(168,85,247,0.26))",
        "accent": "#60a5fa",
        "accent_soft": "rgba(96,165,250,0.14)",
        "success": "#34d399",
        "warning": "#f59e0b",
    },
    {
        "name": "Emerald Elite",
        "hero": "linear-gradient(135deg, rgba(16,185,129,0.38), rgba(6,182,212,0.24))",
        "accent": "#34d399",
        "accent_soft": "rgba(52,211,153,0.14)",
        "success": "#22c55e",
        "warning": "#fbbf24",
    },
    {
        "name": "Sunset Prestige",
        "hero": "linear-gradient(135deg, rgba(249,115,22,0.38), rgba(236,72,153,0.24))",
        "accent": "#fb923c",
        "accent_soft": "rgba(251,146,60,0.14)",
        "success": "#4ade80",
        "warning": "#f59e0b",
    },
]

if st.session_state.selected_theme is None:
    st.session_state.selected_theme = random.choice(THEMES)

THEME = st.session_state.selected_theme


# ============================================================
# STYLE
# ============================================================
st.markdown(
    f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.04), transparent 25%),
                linear-gradient(180deg, #07101d 0%, #0f172a 45%, #111827 100%);
        }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #08111f 0%, #0f172a 50%, #111827 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}
        .block-container {{
            max-width: 1480px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }}
        .hero-card {{
            background: {THEME['hero']};
            padding: 34px;
            border-radius: 28px;
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 18px 45px rgba(0,0,0,0.30);
            margin-bottom: 1rem;
            overflow: hidden;
        }}
        .section-card {{
            background: rgba(255,255,255,0.045);
            padding: 22px;
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 28px rgba(0,0,0,0.18);
            margin-bottom: 16px;
        }}
        .section-card-strong {{
            background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
            padding: 22px;
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 28px rgba(0,0,0,0.18);
            margin-bottom: 16px;
        }}
        .badge {{
            display: inline-block;
            padding: 7px 13px;
            border-radius: 999px;
            background: {THEME['accent_soft']};
            border: 1px solid rgba(255,255,255,0.16);
            color: #eff6ff;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-bottom: 14px;
        }}
        .subtle {{
            color: #dbeafe;
            opacity: 0.92;
        }}
        .small-muted {{
            color: #94a3b8;
            font-size: 0.92rem;
        }}
        .kpi-card {{
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 18px;
            border-radius: 20px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.18);
            min-height: 124px;
        }}
        .kpi-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }}
        .kpi-value {{
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.15;
        }}
        .kpi-delta {{
            color: {THEME['success']};
            font-size: 0.88rem;
            margin-top: 8px;
        }}
        .pill {{
            display: inline-block;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 8px 12px;
            border-radius: 999px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.9rem;
            color: #e5e7eb;
        }}
        .insight-box {{
            background: rgba(255,255,255,0.03);
            border-left: 4px solid {THEME['accent']};
            padding: 14px 16px;
            border-radius: 12px;
            margin-bottom: 10px;
        }}
        .price-card {{
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 22px;
            border-radius: 24px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
            min-height: 260px;
        }}
        .price-card.featured {{
            outline: 2px solid {THEME['accent']};
            transform: translateY(-4px);
        }}
        .footer-box {{
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 16px;
            border-radius: 18px;
            margin-top: 14px;
        }}
        div[data-testid="metric-container"] {{
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.07);
            padding: 8px 14px;
            border-radius: 18px;
        }}
        .stAlert {{ border-radius: 14px; }}
        h1, h2, h3, h4, h5, h6, p, li, label, div, span {{ color: #f8fafc; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================
def get_openai_api_key() -> str | None:
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def init_openai_client():
    api_key = get_openai_api_key()
    if not api_key:
        return None, "Brak OPENAI_API_KEY w Streamlit Secrets lub zmiennych środowiskowych."
    if OpenAI is None:
        return None, "Biblioteka openai nie jest zainstalowana. Zainstaluj dependencies z requirements.txt."
    return OpenAI(api_key=api_key), None


def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)


def load_excel(file) -> pd.DataFrame:
    return pd.read_excel(file)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def find_column(df: pd.DataFrame, candidates):
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        for col_lower, original in lower_map.items():
            if candidate in col_lower:
                return original
    return None


def get_demo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=30, freq="D"),
            "product": [
                "Sneakers", "Backpack", "Sneakers", "Watch", "T-shirt", "Sneakers",
                "Backpack", "Watch", "Headphones", "T-shirt", "Sneakers", "Headphones",
                "Sneakers", "Watch", "Backpack", "T-shirt", "Sunglasses", "Sneakers",
                "Socks", "Headphones", "Backpack", "Watch", "Sneakers", "T-shirt",
                "Sneakers", "Sunglasses", "Backpack", "Headphones", "Watch", "Sneakers"
            ],
            "category": [
                "Footwear", "Accessories", "Footwear", "Accessories", "Apparel", "Footwear",
                "Accessories", "Accessories", "Electronics", "Apparel", "Footwear", "Electronics",
                "Footwear", "Accessories", "Accessories", "Apparel", "Accessories", "Footwear",
                "Apparel", "Electronics", "Accessories", "Accessories", "Footwear", "Apparel",
                "Footwear", "Accessories", "Accessories", "Electronics", "Accessories", "Footwear"
            ],
            "country": [
                "USA", "Germany", "USA", "UK", "France", "Canada",
                "Germany", "USA", "Poland", "France", "USA", "Poland",
                "Spain", "Italy", "Germany", "France", "USA", "Netherlands",
                "Poland", "USA", "Germany", "Italy", "Canada", "France",
                "USA", "Spain", "Germany", "Poland", "Italy", "Canada"
            ],
            "orders": [10, 5, 12, 6, 8, 15, 7, 4, 9, 6, 14, 10, 11, 8, 6, 7, 9, 13, 5, 11, 7, 8, 16, 9, 17, 8, 7, 12, 9, 15],
            "revenue": [1200, 550, 1420, 860, 420, 1850, 680, 520, 990, 390, 1710, 1200, 1450, 920, 640, 470, 760, 1660, 240, 1310, 710, 890, 1950, 510, 2100, 820, 690, 1410, 940, 1880],
        }
    )


def compute_ecommerce_metrics(df: pd.DataFrame) -> dict:
    df = clean_columns(df)
    revenue_col = find_column(df, ["revenue", "sales", "total", "amount", "gmv", "income"])
    orders_col = find_column(df, ["orders", "transactions", "qty_orders", "order_count"])
    product_col = find_column(df, ["product", "item", "sku", "name"])
    category_col = find_column(df, ["category", "collection", "segment"])
    date_col = find_column(df, ["date", "day", "order_date", "created"])
    region_col = find_column(df, ["country", "region", "market"])

    metrics = {
        "revenue": 0.0,
        "orders": 0,
        "avg_order_value": 0.0,
        "top_products": pd.DataFrame(),
        "top_categories": pd.DataFrame(),
        "revenue_by_date": pd.DataFrame(),
        "revenue_by_region": pd.DataFrame(),
        "top_region_name": "-",
        "top_region_revenue": 0.0,
        "top_product_name": "-",
        "top_product_revenue": 0.0,
        "diagnostics": {
            "revenue_col": revenue_col,
            "orders_col": orders_col,
            "product_col": product_col,
            "category_col": category_col,
            "date_col": date_col,
            "region_col": region_col,
        },
    }

    if revenue_col:
        df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce").fillna(0)
        metrics["revenue"] = float(df[revenue_col].sum())

    if orders_col:
        df[orders_col] = pd.to_numeric(df[orders_col], errors="coerce").fillna(0)
        metrics["orders"] = int(df[orders_col].sum())
    else:
        metrics["orders"] = len(df)

    if metrics["orders"] > 0:
        metrics["avg_order_value"] = metrics["revenue"] / metrics["orders"]

    if product_col and revenue_col:
        metrics["top_products"] = (
            df.groupby(product_col, dropna=False)[revenue_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        if not metrics["top_products"].empty:
            metrics["top_product_name"] = str(metrics["top_products"].iloc[0, 0])
            metrics["top_product_revenue"] = float(metrics["top_products"].iloc[0, 1])

    if category_col and revenue_col:
        metrics["top_categories"] = (
            df.groupby(category_col, dropna=False)[revenue_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

    if date_col and revenue_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            temp = df.dropna(subset=[date_col]).groupby(df[date_col].dt.date)[revenue_col].sum().reset_index()
            temp.columns = ["date", "revenue"]
            metrics["revenue_by_date"] = temp
        except Exception:
            pass

    if region_col and revenue_col:
        metrics["revenue_by_region"] = (
            df.groupby(region_col, dropna=False)[revenue_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        if not metrics["revenue_by_region"].empty:
            metrics["top_region_name"] = str(metrics["revenue_by_region"].iloc[0, 0])
            metrics["top_region_revenue"] = float(metrics["revenue_by_region"].iloc[0, 1])

    return metrics


def dataframe_summary_for_ai(df: pd.DataFrame, max_rows: int = 20) -> str:
    sample = df.head(max_rows).copy()
    summary = {
        "columns": list(sample.columns),
        "row_count": int(len(df)),
        "sample_rows": sample.astype(str).to_dict(orient="records"),
        "missing_values": df.isna().sum().to_dict(),
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


def save_report_to_history(title: str, content: str):
    st.session_state.analysis_history.insert(
        0,
        {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "content": content,
        },
    )
    st.session_state.analysis_history = st.session_state.analysis_history[:10]


def analyze_with_openai(df: pd.DataFrame, business_goal: str, extra_notes: str) -> str:
    client, error = init_openai_client()
    if error:
        return f"Błąd konfiguracji OpenAI: {error}"

    prompt = f"""
Jesteś starszym konsultantem e-commerce i analitykiem wzrostu.
Przeanalizuj dane sklepu internetowego i przygotuj profesjonalny raport po polsku.

Cel biznesowy:
{business_goal}

Dodatkowe uwagi:
{extra_notes}

Podsumowanie danych:
{dataframe_summary_for_ai(df)}

Zwróć odpowiedź w sekcjach:
1. Podsumowanie zarządcze
2. Najważniejsze insighty
3. Problemy i ryzyka
4. Szanse wzrostu
5. Rekomendowane działania na 7 dni
6. Rekomendowane działania na 30 dni
7. Jakich danych jeszcze brakuje
8. Propozycje wdrożeń dla firmy

Pisz konkretnie, profesjonalnie i praktycznie.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Jesteś precyzyjnym doradcą biznesowym e-commerce."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content


def analyze_image_with_openai(image_bytes: bytes, business_goal: str) -> str:
    client, error = init_openai_client()
    if error:
        return f"Błąd konfiguracji OpenAI: {error}"

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Przeanalizuj profesjonalnie ten obraz związany z e-commerce. "
                            f"Cel biznesowy: {business_goal}. "
                            "Opisz co widać, jakie są możliwe problemy, szanse, wnioski i rekomendowane działania."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}},
                ],
            }
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def render_kpi_card(label: str, value: str, delta: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_box(text: str):
    st.markdown(f"<div class='insight-box'>{text}</div>", unsafe_allow_html=True)


def render_price_card(plan_name: str, price: str, featured: bool, features: list[str]):
    cls = "price-card featured" if featured else "price-card"
    items = "".join([f"<li>{item}</li>" for item in features])
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="badge">{plan_name.upper()}</div>
            <h3>{plan_name}</h3>
            <h2>{price}</h2>
            <ul>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## CommerceAI Production MVP")
st.sidebar.markdown("<p class='small-muted'>AI Growth Intelligence Platform</p>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Nawigacja",
    ["Home", "Executive Dashboard", "AI Analysis", "File Center", "Reports", "Pricing", "Roadmap"],
)

st.sidebar.markdown("---")
st.sidebar.text_input("Nazwa sklepu", key="selected_store_name")
st.sidebar.selectbox("Plan abonamentowy", ["Starter", "Scale", "Enterprise"], key="selected_plan")
st.sidebar.checkbox("Debug mode", key="debug_mode")
st.sidebar.success(f"Plan {st.session_state.selected_plan} · Active")
st.sidebar.caption(f"Theme: {THEME['name']}")
st.sidebar.caption("Deploy-ready MVP for modern commerce")
st.sidebar.markdown("### Core modules")
st.sidebar.markdown("- Sales analytics")
st.sidebar.markdown("- AI strategy")
st.sidebar.markdown("- Product intelligence")
st.sidebar.markdown("- Market expansion")
st.sidebar.markdown("- Visual analysis")

if st.sidebar.button("Clear current report", use_container_width=True):
    st.session_state.analysis_result = None

if st.sidebar.button("Clear uploaded data", use_container_width=True):
    st.session_state.uploaded_df = None
    st.session_state.uploaded_image_preview = None

if st.session_state.debug_mode:
    with st.sidebar.expander("Debug"):
        try:
            secrets_has_key = "OPENAI_API_KEY" in st.secrets
        except Exception:
            secrets_has_key = False
        st.write("OpenAI package:", OpenAI is not None)
        st.write("Key in secrets:", secrets_has_key)
        st.write("Key in env:", os.getenv("OPENAI_API_KEY") is not None)
        st.write("Uploaded df:", st.session_state.uploaded_df is not None)
        st.write("Uploaded image:", st.session_state.uploaded_image_preview is not None)
        st.write("History items:", len(st.session_state.analysis_history))


# ============================================================
# HOME
# ============================================================
if page == "Home":
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="badge">COMMERCEAI PRODUCTION MVP</div>
            <h1>{st.session_state.selected_store_name}</h1>
            <p class="subtle">
                Executive-grade e-commerce analytics platform with AI-powered recommendations,
                premium dashboarding, growth intelligence, visual analysis, and deployment-ready UX.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("MRR", "$48,900", "+18.2% vs last month")
    with c2:
        render_kpi_card("Active Stores", "284", "+21 new accounts")
    with c3:
        render_kpi_card("AI Reports", "6,142", "+404 this week")
    with c4:
        render_kpi_card("Estimated ROI Lift", "22%", "+4.8 pp optimization")

    demo_metrics = compute_ecommerce_metrics(get_demo_data())
    a, b, c = st.columns(3)
    a.metric("Top Market", demo_metrics["top_region_name"], format_currency(demo_metrics["top_region_revenue"]))
    b.metric("Top Product", demo_metrics["top_product_name"], format_currency(demo_metrics["top_product_revenue"]))
    c.metric("Average Order Value", format_currency(demo_metrics["avg_order_value"]))

    left, right = st.columns([1.45, 1])
    with left:
        st.markdown("<div class='section-card-strong'>", unsafe_allow_html=True)
        st.subheader("Executive value proposition")
        render_insight_box("Transform raw store data into strategic recommendations for growth, margin, product mix, and market expansion.")
        render_insight_box("Designed as a premium SaaS layer for founders, growth teams, e-commerce managers, and agencies.")
        render_insight_box("Ready for evolution into a commercial platform with authentication, subscriptions, database storage, and integrations.")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Suggested workflow")
        st.markdown("<span class='pill'>Upload data</span><span class='pill'>Review KPIs</span><span class='pill'>Run AI report</span><span class='pill'>Export decisions</span>", unsafe_allow_html=True)
        st.write("")
        st.info("This version is cleaned for local work and deployment to Streamlit Cloud.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-box'>For online deployment, add requirements.txt and OPENAI_API_KEY in Streamlit Secrets.</div>", unsafe_allow_html=True)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================
elif page == "Executive Dashboard":
    st.title("Executive Dashboard")
    st.caption("Premium overview of revenue, orders, products, categories, and market performance")

    source_option = st.radio("Data source", ["Demo data", "Uploaded data"], horizontal=True)
    if source_option == "Demo data":
        df = get_demo_data()
    else:
        df = st.session_state.uploaded_df
        if df is None:
            st.warning("No uploaded file found. Go to File Center and upload CSV or Excel.")
            st.stop()

    metrics = compute_ecommerce_metrics(df)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Revenue", format_currency(metrics["revenue"]))
    m2.metric("Orders", f"{metrics['orders']:,}")
    m3.metric("AOV", format_currency(metrics["avg_order_value"]))
    m4.metric("Top market", metrics["top_region_name"])

    row1_left, row1_right = st.columns([1.15, 1])
    with row1_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Revenue trend")
        if not metrics["revenue_by_date"].empty:
            st.line_chart(metrics["revenue_by_date"].set_index("date"))
        else:
            st.info("No suitable date column detected.")
        st.markdown("</div>", unsafe_allow_html=True)
    with row1_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Revenue by market")
        if not metrics["revenue_by_region"].empty:
            region_df = metrics["revenue_by_region"].copy().set_index(metrics["revenue_by_region"].columns[0])
            st.bar_chart(region_df)
        else:
            st.info("No country/region/market column detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    row2_left, row2_right = st.columns(2)
    with row2_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Top products")
        if not metrics["top_products"].empty:
            st.dataframe(metrics["top_products"], use_container_width=True)
        else:
            st.info("No product + revenue columns detected.")
        st.markdown("</div>", unsafe_allow_html=True)
    with row2_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Top categories")
        if not metrics["top_categories"].empty:
            st.dataframe(metrics["top_categories"], use_container_width=True)
        else:
            st.info("No category + revenue columns detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card-strong'>", unsafe_allow_html=True)
    st.subheader("Board-level insights")
    render_insight_box(f"Top market is <b>{metrics['top_region_name']}</b>, indicating a strong candidate for budget concentration or localization expansion.")
    render_insight_box(f"Best-selling product is <b>{metrics['top_product_name']}</b>; use it for upsell, bundle strategy, and retargeting campaigns.")
    render_insight_box("If most revenue depends on one market or one product, diversification should be part of the next 30-day risk mitigation plan.")
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Data diagnostics"):
        st.json(metrics["diagnostics"])
        st.dataframe(df.head(25), use_container_width=True)


# ============================================================
# AI ANALYSIS
# ============================================================
elif page == "AI Analysis":
    st.title("AI Analysis Center")
    st.caption("Strategy-grade analysis for datasets, dashboards, creatives, and product visuals")

    mode = st.radio("Analysis mode", ["Dataset analysis", "Image analysis"], horizontal=True)
    business_goal = st.text_area("Business goal", placeholder="Example: Increase margin, improve product mix, scale EU markets, reduce dependency on low-performing categories.", height=100)
    extra_notes = st.text_area("Extra notes", placeholder="Example: Focus on repeat purchases, CAC efficiency, bundle offers, retention, seasonality.", height=100)

    t1, t2 = st.columns([1.35, 1])
    with t1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("AI report scope")
        st.markdown("<span class='pill'>Executive summary</span><span class='pill'>Risks</span><span class='pill'>Growth opportunities</span><span class='pill'>7-day actions</span><span class='pill'>30-day roadmap</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Advisory mode")
        st.write("This section behaves like an AI e-commerce strategist focused on practical actions, not generic summaries.")
        st.markdown("</div>", unsafe_allow_html=True)

    if mode == "Dataset analysis":
        source_option = st.radio("Dataset source", ["Demo data", "Uploaded data"], horizontal=True)
        if source_option == "Demo data":
            df = get_demo_data()
        else:
            df = st.session_state.uploaded_df
            if df is None:
                st.warning("Upload a file in File Center first.")
                st.stop()

        if st.button("Run AI dataset analysis", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing the dataset..."):
                result = analyze_with_openai(df, business_goal, extra_notes)
                st.session_state.analysis_result = result
                save_report_to_history("Dataset analysis", result)
    else:
        uploaded_image = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None:
            image_bytes = uploaded_image.getvalue()
            st.session_state.uploaded_image_preview = image_bytes
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption="Image preview", use_container_width=True)

        if st.button("Run AI image analysis", type="primary", use_container_width=True):
            if not st.session_state.uploaded_image_preview:
                st.warning("Upload an image first.")
            else:
                with st.spinner("AI is analyzing the image..."):
                    result = analyze_image_with_openai(st.session_state.uploaded_image_preview, business_goal)
                    st.session_state.analysis_result = result
                    save_report_to_history("Image analysis", result)

    st.markdown("<div class='section-card-strong'>", unsafe_allow_html=True)
    st.subheader("AI Report")
    if st.session_state.analysis_result:
        st.markdown(st.session_state.analysis_result)
        st.download_button(
            "Download report",
            data=st.session_state.analysis_result.encode("utf-8"),
            file_name=f"commerceai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            "Download report as JSON",
            data=json.dumps({
                "created_at": datetime.now().isoformat(),
                "store_name": st.session_state.selected_store_name,
                "content": st.session_state.analysis_result,
            }, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"commerceai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )
    else:
        st.info("No report generated yet.")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FILE CENTER
# ============================================================
elif page == "File Center":
    st.title("File Center")
    st.caption("Upload operational, sales, and market files to power dashboard analytics and AI recommendations")

    uploaded_data = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded_data is not None:
        try:
            if uploaded_data.name.lower().endswith(".csv"):
                df = load_csv(uploaded_data)
            else:
                df = load_excel(uploaded_data)
            st.session_state.uploaded_df = clean_columns(df)
            st.success(f"File uploaded successfully: {uploaded_data.name}")

            i1, i2, i3, i4 = st.columns(4)
            i1.metric("Rows", len(df))
            i2.metric("Columns", len(df.columns))
            i3.metric("Missing values", int(df.isna().sum().sum()))
            i4.metric("Import status", "Ready")

            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Data preview")
            st.dataframe(df.head(30), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception as exc:
            st.error(f"File could not be read: {exc}")

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Recommended schema")
    st.write("Best results usually come from files containing columns similar to: date, product, category, country, orders, revenue.")
    st.markdown("<span class='pill'>date</span><span class='pill'>product</span><span class='pill'>category</span><span class='pill'>country</span><span class='pill'>orders</span><span class='pill'>revenue</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# REPORTS
# ============================================================
elif page == "Reports":
    st.title("Reports Center")
    st.caption("Premium reporting space for decision-ready outputs and stakeholder summaries")

    r1, r2, r3 = st.columns(3)
    with r1:
        render_kpi_card("Weekly reports", str(len(st.session_state.analysis_history)), "+ history enabled")
    with r2:
        render_kpi_card("Current plan", st.session_state.selected_plan, "active")
    with r3:
        render_kpi_card("Export readiness", "100%", "Markdown + JSON")

    st.markdown("<div class='section-card-strong'>", unsafe_allow_html=True)
    st.subheader("Suggested report types")
    render_insight_box("CEO summary: revenue risks, growth opportunities, and recommended priorities.")
    render_insight_box("Growth report: best products, markets, upsell candidates, and acquisition scaling opportunities.")
    render_insight_box("Operations report: weak categories, data gaps, market imbalance, and recommended fixes.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Saved reports")
    if st.session_state.analysis_history:
        for idx, item in enumerate(st.session_state.analysis_history, start=1):
            with st.expander(f"{idx}. {item['title']} · {item['created_at']}"):
                st.markdown(item["content"])
    else:
        st.info("Run AI Analysis first to populate this area.")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PRICING
# ============================================================
elif page == "Pricing":
    st.title("Pricing")
    st.caption("Subscription-ready view for SaaS commercialization")

    p1, p2, p3 = st.columns(3)
    with p1:
        render_price_card("Starter", "$29 / month", False, [
            "3 AI reports / month",
            "Basic analytics dashboard",
            "CSV & Excel uploads",
            "Single workspace",
        ])
    with p2:
        render_price_card("Scale", "$99 / month", True, [
            "25 AI reports / month",
            "Executive dashboard",
            "Image analysis",
            "Priority support",
            "Reports center",
        ])
    with p3:
        render_price_card("Enterprise", "Custom", False, [
            "Unlimited reports",
            "Multi-user access",
            "Database integrations",
            "Custom onboarding",
            "Dedicated success manager",
        ])

    st.markdown("<div class='section-card-strong'>", unsafe_allow_html=True)
    st.subheader("Positioning recommendation")
    st.write(
        "Sell this product as an AI Growth Intelligence Platform for e-commerce, not just a dashboard tool. "
        "That positioning supports higher pricing because the value comes from decisions, prioritization, and measurable business action."
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# ROADMAP
# ============================================================
elif page == "Roadmap":
    st.title("Product Roadmap")
    st.caption("Upgrade path from premium MVP to production SaaS")

    road1, road2 = st.columns(2)

    with road1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Phase 1 · Production MVP+")
        st.write(
            "1. User authentication\n"
            "2. Saved report history in database\n"
            "3. PDF export\n"
            "4. Account settings\n"
            "5. Per-client dashboards"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with road2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Phase 2 · Commercial SaaS")
        st.write(
            "1. Stripe subscriptions\n"
            "2. PostgreSQL database\n"
            "3. Multi-tenant architecture\n"
            "4. Admin panel\n"
            "5. Shopify and WooCommerce integrations"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card-strong'>", unsafe_allow_html=True)
    st.subheader("Strategic recommendation")
    st.write(
        "The strongest business model is to start with a premium AI analytics MVP, validate demand with agencies or store owners, "
        "and then add recurring subscription logic, database persistence, and native store integrations."
    )
    st.markdown("</div>", unsafe_allow_html=True)
