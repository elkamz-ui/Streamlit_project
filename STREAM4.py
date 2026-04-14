import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

df = pd.read_csv("Pandas Project.csv")
st.title("STREAMLIT PROJECT")

st.markdown("## About ")
st.markdown("### This is a dashboard showing a companies shipment data. It contains relevant KPIs and Charts")


# CLEANING
df["Amount"] = pd.to_numeric(df["Amount"].replace({r'[\$,]': ''}, regex=True))
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
df["Month_name"] = df["Date"].dt.month_name()

# ------------------- SLICERS -------------------
st.sidebar.header("Data Filter")

# -------- COUNTRY --------
country_temp = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].dropna().unique(),
    default=st.session_state.get("country", [])
)

if st.sidebar.button("Select Country"):
    st.session_state["country"] = country_temp


# -------- PRODUCT --------
product_temp = st.sidebar.multiselect(
    "Select Product",
    options=df["Product"].dropna().unique(),
    default=st.session_state.get("product", [])
)

if st.sidebar.button("Select Product"):
    st.session_state["product"] = product_temp


# -------- SALES PERSON --------
salesperson_temp = st.sidebar.multiselect(
    "Select Sales Person",
    options=df["Sales Person"].dropna().unique(),
    default=st.session_state.get("salesperson", [])
)

if st.sidebar.button("Select Sales Person"):
    st.session_state["salesperson"] = salesperson_temp


# -------- DATE --------
date_temp = st.sidebar.date_input(
    "Select Date Range",
    st.session_state.get("date", [])
)

if st.sidebar.button("Select Date"):
    st.session_state["date"] = date_temp
#              start date and end date above

# ------------------- FILTERING -------------------
# ------------------- FILTERING -------------------

filtered_df = df.copy()

country_filter = st.session_state.get("country", df["Country"].dropna().unique())
product_filter = st.session_state.get("product", df["Product"].dropna().unique())
salesperson_filter = st.session_state.get("salesperson", df["Sales Person"].dropna().unique())
date_range = st.session_state.get("date", [df["Date"].min(), df["Date"].max()])

filtered_df = df[
    (df["Country"].isin(country_filter)) &
    (df["Product"].isin(product_filter)) &
    (df["Sales Person"].isin(salesperson_filter)) &
    (df["Date"] >= pd.to_datetime(date_range[0]))
    # Compares every row’s date with the start date
    # Keep rows on or after the start date
    &
    (df["Date"] <= pd.to_datetime(date_range[1]))
    # Compares every row’s date with the end date
    # Keep rows on or before the end date
]

# Add a Reset All Filters button:
if st.sidebar.button("Reset All Filters"):
    st.session_state.clear()


filtered_df['Revenue_per_box'] = filtered_df['Amount'] / filtered_df['Boxes Shipped']
avg_revenue_per_box = round(filtered_df['Revenue_per_box'].mean())

# CALCULATIONSs
revenue_per_salesperson = filtered_df.groupby("Sales Person")["Amount"].sum().sort_values(ascending=False)

boxes_shipped_per_product = filtered_df.groupby("Product")["Boxes Shipped"].sum().sort_values(ascending=False)

total_sales_per_month = filtered_df.groupby("Month_name")["Month_name"].count()

total_revenue_per_country = filtered_df.groupby("Country")["Amount"].sum().sort_values(ascending=False)

revenue_per_product = filtered_df.groupby("Product")["Amount"].sum().sort_values(ascending=False)

# CLEANING
total_sales_per_month.index = pd.to_datetime(total_sales_per_month.index, format="%B")
total_sales_per_month = total_sales_per_month.sort_index()


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Revenue Generated", value=round(filtered_df["Amount"].sum()))

with col2:
    st.metric(label="Total Products Sampled", value=filtered_df["Product"].nunique())

with col3:
    st.metric(label="Average Revenue per Box", value=avg_revenue_per_box)

top_10_sales_person = filtered_df["Sales Person"].value_counts().head(10).index.to_list()
top_10_products = filtered_df["Product"].value_counts().head(10).index.to_list()

chart1, chart2 = st.columns(2)

with chart1:
    fig, ax = plt.subplots()
    ax = revenue_per_salesperson[top_10_sales_person].plot(kind="bar", color="orange")
    plt.title("Revenue Generated per Salesperson")
    plt.ylabel("Revenue")
    ax.ticklabel_format(style='plain', axis='y')
    st.pyplot(fig)



with chart2:
    fig, ax = plt.subplots()
    ax = boxes_shipped_per_product[top_10_products].plot(kind= "bar", color="purple")
    plt.title("Boxes Shipped per Product")
    plt.ylabel("Boxes Shipped")
    st.pyplot(fig)

chart3, chart4= st.columns(2)

with chart3:
    fig, ax = plt.subplots()
    ax = total_sales_per_month.plot(kind="line", marker="o", color="green")
    plt.ylabel("Month Count")
    plt.title("Total Sales per Month")
    st.pyplot(fig)

with chart4:
    fig, ax = plt.subplots()
    ax = total_revenue_per_country.plot(kind="bar", color="brown")
    ax.ticklabel_format(style='plain', axis='y')
    plt.title("Revenue per Country")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    st.pyplot(fig)

chart5 = st.container()

with chart5:
    fig, ax = plt.subplots()
    ax = revenue_per_product.plot(kind="bar", color= "yellow")
    ax.ticklabel_format(style='plain', axis='y')
    plt.title("Revenue per product")
    plt.ylabel("Revenue")
    st.pyplot(fig)

#----------------------------------------GEOPANDAS
# LOADING WORLD MAP DATA
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
world = gpd.read_file(url)

# MERGING MY DATA WITH GEOPANDAS
merged = world.merge(
    total_revenue_per_country,
    how="left",
    left_on="name",
    right_on="Country"
)

# CREATING THE MAP
fig, ax = plt.subplots(figsize=(15, 8))
# ax.set_facecolor("lightblue")
fig.patch.set_facecolor("lightblue")# sets the background of the map as blue

# PLOTTING THE MAP
merged.plot(
    column="Amount",
    cmap="coolwarm",
    #Color scheme: Orange → Red-Light = low revenue-Dark = high revenue
    linewidth=0.5,
    #Border thickness of countries
    ax=ax,
    edgecolor="black",
    #Country borders are black
    legend=True
)
# CUSTOMIZING THE MAP
# Set ocean color

ax.set_title("Total Revenue by Country", fontsize=16)
ax.set_axis_off()  #Removes axes (makes it look like a real map)

#----------------------STREAMLIT SETUP
# st.set_page_config(layout="wide")
st.title("🌍 Revenue Distribution by Country")
st.pyplot(fig)

st.markdown("### Sample Dataframe")
st.dataframe(data=df.head(20))

st.markdown("""
-----------------------------------------------
Designed by Ibrahim Kambari\\
[🐙 GitHub](https://github.com/elkamz-ui)  
[💼 LinkedIn](https://www.linkedin.com/in/ibrahimkambari)
""")





