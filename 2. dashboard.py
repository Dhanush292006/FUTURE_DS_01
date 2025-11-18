import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide", page_title="E-commerce Sales Dashboard")

@st.cache_data
def load_data(path="sample_data.csv"):
    df = pd.read_csv(path, parse_dates=["order_date"])
    df["revenue"] = df["revenue"].astype(float)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["is_returned"] = df["is_returned"].astype(bool)
    return df

df = load_data(st.sidebar.text_input("CSV path", "sample_data.csv"))

# Top KPI row
total_revenue = df.loc[~df["is_returned"], "revenue"].sum()
total_orders = df["order_id"].nunique()
total_customers = df["user_id"].nunique()
aov = total_revenue / total_orders if total_orders else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Total Orders", f"{total_orders}")
kpi3.metric("Total Customers", f"{total_customers}")
kpi4.metric("AOV (Avg Order Value)", f"${aov:,.2f}")

# Filters
st.sidebar.header("Filters")
with st.sidebar.form("filters"):
    date_min = st.date_input("From", value=df["order_date"].min())
    date_max = st.date_input("To", value=df["order_date"].max())
    categories = st.multiselect("Category", df["category"].unique(), df["category"].unique())
    channels = st.multiselect("Channel", df["channel"].unique(), df["channel"].unique())
    submit = st.form_submit_button("Apply")

mask = (
    (df["order_date"] >= date_min) &
    (df["order_date"] <= date_max) &
    (df["category"].isin(categories)) &
    (df["channel"].isin(channels))
)
dff = df.loc[mask].copy()

# Revenue over time
st.markdown("## Revenue Over Time")
rev_ts = dff.groupby("order_date", as_index=False).agg(revenue=("revenue", "sum"))
fig_ts = px.bar(rev_ts, x="order_date", y="revenue", title="Revenue by Day")
st.plotly_chart(fig_ts, use_container_width=True)

# Sales by category & channel
st.markdown("## Sales Breakdown")
col1, col2 = st.columns(2)

with col1:
    cat = dff.groupby("category", as_index=False).agg(revenue=("revenue", "sum"))
    fig_cat = px.pie(cat, values="revenue", names="category", title="Revenue by Category")
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    ch = dff.groupby("channel", as_index=False).agg(revenue=("revenue","sum"))
    fig_ch = px.bar(ch.sort_values("revenue", ascending=False), x="channel", y="revenue", title="Revenue by Channel")
    st.plotly_chart(fig_ch, use_container_width=True)

# Top products
st.markdown("## Top Products")
topn = st.slider("Select Top N", 5, 20, 10)
prod = dff.groupby(["product_id","product_name"], as_index=False).agg(
    revenue=("revenue","sum"),
    qty=("quantity","sum"),
    orders=("order_id","nunique")
)
prod = prod.sort_values("revenue", ascending=False).head(topn)
st.dataframe(prod.style.format({"revenue": "${:,.2f}"}))

# Country wise
st.markdown("## Revenue by Country")
country = dff.groupby("country", as_index=False).agg(revenue=("revenue","sum"))
fig_country = px.bar(country.sort_values("revenue", ascending=False), x="country", y="revenue")
st.plotly_chart(fig_country, use_container_width=True)

# Returns
st.markdown("## Returns & Refunds")
returns = dff[dff["is_returned"]]
st.write(f"Return rate: {(returns.shape[0]/max(1, dff.shape[0])):.1%}")
if not returns.empty:
    st.dataframe(returns)

# Customer metrics
st.markdown("## Top Customers by Revenue")
cust = dff.groupby("user_id", as_index=False).agg(
    orders=("order_id","nunique"),
    revenue=("revenue","sum")
)
cust = cust.sort_values("revenue", ascending=False).head(20)
st.dataframe(cust.style.format({"revenue":"${:,.2f}"}))

st.markdown("---")
st.caption("Streamlit E-commerce Dashboard – Replace sample_data.csv with your dataset.")
