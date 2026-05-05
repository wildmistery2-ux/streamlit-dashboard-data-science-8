import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Setup
st.set_page_config(page_title="Retail Intelligence v2", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #00FFAA; }
    .stChart { border-radius: 15px; border: 1px solid #444; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading
@st.cache_data
def load_data():
    # Referencing the file name verbatim: project1_df.csv
    df = pd.read_csv("project1_df.csv")
    df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Purchase Date'])
    return df

try:
    df = load_data()

    # --- INTERACTIVE SELECTIONS ---
    # brush: Click and drag on the timeline to filter by date
    brush = alt.selection_interval(encodings=['x'], empty='all')
    # click: Click a category bar to highlight it across all charts
    click = alt.selection_point(fields=['Product Category'], empty='all')

    # --- SIDEBAR FILTERS ---
    st.sidebar.title("Dashboard Filters")
    cities = st.sidebar.multiselect("Select Cities", options=sorted(df['Location'].unique()), default=sorted(df['Location'].unique())[:5])
    
    filtered_df = df[df['Location'].isin(cities)]

    # --- KPI SECTION ---
    st.title("📊 Retail Performance Dashboard")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Revenue", f"₹{filtered_df['Net Amount'].sum():,.0f}")
    kpi2.metric("Total Orders", f"{len(filtered_df):,}")
    kpi3.metric("Avg Basket", f"₹{filtered_df['Net Amount'].mean():,.2f}")

    st.divider()

    # --- MAIN CHARTS ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📅 Revenue Trend (Select time range)")
        # Area chart that reacts to category clicks
        timeline = alt.Chart(filtered_df).mark_area(
            line={'color':'#00FFAA'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#00FFAA', offset=0),
                       alt.GradientStop(color='transparent', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X("Purchase Date:T", title="Date"),
            y=alt.Y("sum(Net Amount):Q", title="Revenue"),
            opacity=alt.condition(click, alt.value(1), alt.value(0.2)), # Dims if not in clicked category
            tooltip=['sum(Net Amount)']
        ).add_params(brush).properties(height=400)
        
        st.altair_chart(timeline, use_container_width=True)

    with col2:
        st.subheader("🏷️ Sales by Category")
        # Bars that define the 'click' selection
        bars = alt.Chart(filtered_df).mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("Product Category:N", sort='-x', title=None),
            x=alt.X("sum(Net Amount):Q", title="Total Sales"),
            color=alt.condition(click, alt.value("#00FFAA"), alt.value("#333")),
            tooltip=["Product Category", "sum(Net Amount)"]
        ).transform_filter(brush).add_params(click).properties(height=400)
        
        st.altair_chart(bars, use_container_width=True)

    # --- BOTTOM SECTION ---
    st.subheader("🏙️ City & Payment Breakdown")
    heatmap = alt.Chart(filtered_df).mark_rect().encode(
        x=alt.X("Location:N", title="City"),
        y=alt.Y("Purchase Method:N", title="Payment Method"),
        color=alt.Color("count():Q", scale=alt.Scale(scheme='greens'), title="Orders"),
        tooltip=["Location", "Purchase Method", "count()"]
    ).transform_filter(brush).transform_filter(click).properties(height=350)

    st.altair_chart(heatmap, use_container_width=True)

    # --- RAW DATA ---
    with st.expander("📂 View Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True)

except FileNotFoundError:
    st.error("Missing `project1_df_2.csv`. Ensure the file is in the same folder as this script.")