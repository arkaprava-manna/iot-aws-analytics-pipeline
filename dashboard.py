import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

st.set_page_config(page_title="IoT Sensor Analytics", layout="wide")
st.title("IoT Data Analytics Dashboard (AWS S3 + RDS)")

# --- CONFIGURATION ---
import os
from dotenv import load_dotenv

load_dotenv()

RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASS = os.getenv("RDS_PASS")
RDS_DB = os.getenv("RDS_DB")

# Connect to Amazon RDS
conn = mysql.connector.connect(
    host=RDS_HOST,
    user=RDS_USER,
    password=RDS_PASS,
    database=RDS_DB
)

# 1. Descriptive Analytics SQL Queries
kpi_df = pd.read_sql("""
    SELECT 
        COUNT(*) AS total_readings,
        ROUND(AVG(temperature), 2) AS avg_temp,
        MIN(temperature) AS min_temp,
        MAX(temperature) AS max_temp,
        ROUND(AVG(humidity), 1) AS avg_humidity,
        COUNT(DISTINCT sensor_id) AS active_sensors
    FROM sensor_readings
""", conn)

sensor_summary_df = pd.read_sql("""
    SELECT 
        sensor_id,
        COUNT(*) AS reading_count,
        ROUND(AVG(temperature), 2) AS avg_temperature,
        MIN(temperature) AS min_temperature,
        MAX(temperature) AS max_temperature,
        ROUND(AVG(humidity), 1) AS avg_humidity
    FROM sensor_readings
    GROUP BY sensor_id
    ORDER BY sensor_id
""", conn)

raw_df = pd.read_sql("SELECT * FROM sensor_readings ORDER BY timestamp ASC", conn)
conn.close()

# 2. KPI Metrics Row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Readings", int(kpi_df["total_readings"][0]))
c2.metric("Avg Temperature", f"{kpi_df['avg_temp'][0]} °C")
c3.metric("Min / Max Temp", f"{kpi_df['min_temp'][0]} / {kpi_df['max_temp'][0]} °C")
c4.metric("Avg Humidity", f"{kpi_df['avg_humidity'][0]} %")
c5.metric("Active Sensors", int(kpi_df["active_sensors"][0]))

st.divider()

# 3. Charts Row
col1, col2 = st.columns(2)
with col1:
    st.subheader("Temperature Trend Over Time")
    fig_trend = px.line(
        raw_df.head(100),
        x="timestamp",
        y="temperature",
        color="sensor_id",
        labels={"timestamp": "Timestamp", "temperature": "Temperature (°C)", "sensor_id": "Sensor ID"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("Average Temperature by Sensor")
    fig_bar = px.bar(
        sensor_summary_df,
        x="sensor_id",
        y="avg_temperature",
        text="avg_temperature",
        labels={"sensor_id": "Sensor ID", "avg_temperature": "Avg Temp (°C)"}
    )
    fig_bar.update_xaxes(type="category")
    st.plotly_chart(fig_bar, use_container_width=True)

# 4. Humidity Distribution & Tables Row
col3, col4 = st.columns(2)
with col3:
    st.subheader("Humidity Distribution by Sensor")
    fig_pie = px.pie(
        sensor_summary_df,
        names="sensor_id",
        values="avg_humidity",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col4:
    st.subheader("Sensor-Wise Descriptive Analytics (SQL GROUP BY)")
    st.dataframe(sensor_summary_df, use_container_width=True)

st.subheader("Sample Database Records (Amazon RDS)")
st.dataframe(raw_df.head(15), use_container_width=True)