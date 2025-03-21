import streamlit as st
import pandas as pd

# Function to load CSV files into dataframes
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

# Load datasets
trips_df, cars_df, cities_df = load_data()

# Debugging: Check column names
st.write("Trips DataFrame Columns:", trips_df.columns)
st.write("Cars DataFrame Columns:", cars_df.columns)
st.write("Cities DataFrame Columns:", cities_df.columns)

# Merge trips with cars using car_id from trips_df and id from cars_df
trips_merged = trips_df.merge(cars_df, left_on="car_id", right_on="id", how="left")

# Merge with cities for car's city (joining on city_id)
trips_merged = trips_merged.merge(cities_df, on="city_id", how="left")

# Drop unnecessary columns
trips_merged = trips_merged.drop(columns=["car_id", "city_id", "customer_id", "id"], errors='ignore')

# Convert pickup_time to datetime format and extract date
trips_merged["pickup_time"] = pd.to_datetime(trips_merged["pickup_time"])
trips_merged["dropoff_time"] = pd.to_datetime(trips_merged["dropoff_time"])
trips_merged["pickup_date"] = trips_merged["pickup_time"].dt.date

# Sidebar filter for car brand
car_brands = trips_merged["brand"].dropna().unique()
selected_brands = st.sidebar.multiselect("Select the Car Brand", car_brands)

# Filter dataframe based on selected car brands
if selected_brands:
    trips_merged = trips_merged[trips_merged["brand"].isin(selected_brands)]

# Compute business performance metrics
total_trips = trips_merged.shape[0]  # Total number of trips
total_distance = trips_merged["distance"].sum()  # Sum of all trip distances

# Car model with the highest revenue
top_car = (
    trips_merged.groupby("model")["revenue"]
    .sum()
    .idxmax()
)

# Display metrics in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Trips", value=total_trips)
with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car)
with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

# **📊 Visualizations**

## **1️⃣ Trips Over Time**
st.write("### 📈 Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size()  # Fix for missing 'id' column
st.line_chart(trips_over_time)

## **2️⃣ Revenue Per Car Model**
st.write("### 🚗 Revenue Per Car Model")
revenue_per_model = trips_merged.groupby("model")["revenue"].sum()
st.bar_chart(revenue_per_model)

## **3️⃣ Cumulative Revenue Growth Over Time**
st.write("### 💰 Cumulative Revenue Growth Over Time")
trips_merged["cumulative_revenue"] = trips_merged.groupby("pickup_date")["revenue"].cumsum()
cumulative_revenue = trips_merged.groupby("pickup_date")["cumulative_revenue"].max()
st.area_chart(cumulative_revenue)

## **4️⃣ Bonus: Average Trip Duration by City**
st.write("### 🏙️ Average Trip Duration by City")

# Identify the correct city column
city_column = "city_name" if "city_name" in trips_merged.columns else "city"

# Compute average trip duration per city
trips_merged["trip_duration"] = (trips_merged["dropoff_time"] - trips_merged["pickup_time"]).dt.total_seconds() / 60
avg_duration_by_city = trips_merged.groupby(city_column)["trip_duration"].mean()

st.bar_chart(avg_duration_by_city)

# Preview DataFrame
st.write("### Preview of Merged Trips Data")
st.dataframe(trips_merged.head())