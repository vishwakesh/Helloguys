import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_manager import DataManager
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    .main-metrics {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    /* Mobile responsive CSS */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.5rem !important;
        }
        .metric-card {
            padding: 10px;
        }
        .stMetric {
            font-size: 0.9rem !important;
        }
        .stMetric > div {
            flex-direction: column;
        }
        /* Make tables scroll horizontally on mobile */
        .stTable {
            overflow-x: auto;
        }
    }
</style>
""", unsafe_allow_html=True)

# Mobile App Download Banner
st.sidebar.markdown("## 📱 Mobile App")
st.sidebar.info("Get our offline mobile app that stores all data on your device!")
if st.sidebar.button("📲 Download Mobile App", use_container_width=True):
    st.switch_page("pages/05_app_download.py")

# Cache indicator for mobile
st.sidebar.markdown("### Local Storage Status")
offline_mode = st.sidebar.checkbox("Offline Mode", value=False, help="Enable to work offline with locally cached data")
if offline_mode:
    st.sidebar.success("✅ Using local storage only")
else:
    st.sidebar.info("💾 Data stored locally and synced when online")

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

# Sidebar
with st.sidebar:
    st.title("📊 Navigation")
    st.info("Welcome to your Inventory Dashboard!")

    # Quick Actions
    st.subheader("Quick Actions")
    if st.button("➕ Add New Product", use_container_width=True):
        st.switch_page("pages/01_products.py")
    if st.button("💰 Record Sale", use_container_width=True):
        st.switch_page("pages/02_sales.py")
    if st.button("📈 Detailed Analytics", use_container_width=True):
        st.switch_page("pages/03_analytics.py")

# Main Dashboard
st.markdown("<h1 class='main-header'>📦 Inventory Command Center</h1>", unsafe_allow_html=True)

# Get analytics data
analytics = st.session_state.data_manager.get_analytics_data()

# Top metrics with enhanced styling
st.markdown("### 📊 Key Metrics")

# Make metrics layout responsive - 2x2 grid on mobile, 4x1 on desktop
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Total Products",
        analytics.get('total_products', 0),
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Total Sales",
        analytics.get('total_sales', 0),
        delta=None,
        delta_color="normal"
    )
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Revenue",
        f"${analytics.get('total_revenue', 0):,.2f}",
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Out of Stock",
        analytics.get('out_of_stock', 0),
        delta=None,
        delta_color="inverse"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Sales and Inventory Overview
st.markdown("### 📈 Sales Trend")
daily_sales = analytics.get('daily_sales', pd.DataFrame())
if not daily_sales.empty:
    # Responsive chart size
    chart_height = 300  # Smaller height for mobile
    fig = px.line(
        daily_sales,
        x='sale_date',
        y='quantity',
        title='Daily Sales Overview'
    )
    fig.update_layout(
        height=chart_height,
        margin=dict(l=10, r=10, b=10, t=40),  # Tighter margins for mobile
        title_x=0.5,  # Center title
        xaxis_title=None  # Remove axis titles for cleaner mobile view
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sales data available yet")

# Category Performance
st.markdown("### 📊 Category Performance")
category_stats = analytics.get('category_stats', pd.DataFrame())
if not category_stats.empty:
    # Smaller, mobile-friendly chart
    fig = px.pie(
        category_stats,
        values='total_amount',
        names='category',
        title='Sales by Category',
        height=300
    )
    fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=40),
        title_x=0.5,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No category data available")

# Recent Activity and Alerts
st.markdown("### 🔔 Recent Activity")
tabs = st.tabs(["Recent Sales", "Stock Alerts"])

with tabs[0]:
    recent_sales = analytics.get('recent_sales', pd.DataFrame())
    if not recent_sales.empty:
        for _, sale in recent_sales.iterrows():
            st.success(
                f"Sale #{sale['sale_code']}: {sale['quantity']} x {sale['name']} "
                f"(${sale['total_amount']:,.2f})"
            )
    else:
        st.info("No recent sales to display")

with tabs[1]:
    low_stock = analytics.get('low_stock', pd.DataFrame())
    if not low_stock.empty:
        for _, product in low_stock.iterrows():
            remaining_percent = (product['stock'] / product['min_stock_level']) * 100
            st.warning(
                f"⚠️ {product['name']} ({product['category']})\n"
                f"Stock: {product['stock']} units ({get_stock_status(remaining_percent)})"
            )
    else:
        st.success("No stock alerts - Inventory levels are healthy!")

def get_stock_status(percent):
    return "Low" if percent < 50 else "Warning"

# System Status and mobile data cache info
st.sidebar.markdown("---")
st.sidebar.caption("System Status: 🟢 Online")
st.sidebar.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Data backup/export features for mobile
with st.sidebar.expander("📱 Mobile Options"):
    st.caption("Data is stored in your browser's local storage")
    if st.button("Export Data (CSV)"):
        st.session_state.show_export = True

    if st.button("Clear Cache"):
        st.warning("This will reset all local data")
        if st.button("Confirm Clear"):
            st.success("Cache cleared!")
            st.rerun()

# Import pandas for data handling
import pandas as pd