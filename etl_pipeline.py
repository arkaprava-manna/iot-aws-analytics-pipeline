import boto3
import pandas as pd
import mysql.connector
from io import StringIO

# --- CONFIGURATION (Fill in your 4 values below) ---
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FILE_KEY = os.getenv("FILE_KEY")

RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASS = os.getenv("RDS_PASS")
RDS_DB = os.getenv("RDS_DB")

# 1. EXTRACT from Amazon S3
print("1. Extracting data from S3...")
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name="ap-southeast-2"
)
obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
df = pd.read_csv(StringIO(obj["Body"].read().decode("utf-8")))
print(f"   Raw records extracted: {len(df)}")

# 2. TRANSFORM (Remove duplicates, drop nulls, enforce data types)
print("2. Transforming and cleaning data...")
df = df.drop_duplicates()
df = df.dropna(subset=["temperature", "humidity"])
df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
df["sensor_id"] = df["sensor_id"].astype(int)
df["temperature"] = df["temperature"].astype(float)
df["humidity"] = df["humidity"].astype(int)
print(f"   Cleaned records ready to load: {len(df)}")

# 3. LOAD into Amazon RDS (MySQL)
print("3. Connecting to Amazon RDS...")
conn = mysql.connector.connect(
    host=RDS_HOST,
    user=RDS_USER,
    password=RDS_PASS,
    database=RDS_DB
)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    sensor_id INT,
    temperature FLOAT,
    humidity INT
)
""")
cursor.execute("TRUNCATE TABLE sensor_readings")

insert_query = """
INSERT INTO sensor_readings (timestamp, sensor_id, temperature, humidity)
VALUES (%s, %s, %s, %s)
"""
records = df[["timestamp", "sensor_id", "temperature", "humidity"]].values.tolist()
cursor.executemany(insert_query, records)
conn.commit()

print(f"4. Success! Loaded {cursor.rowcount} cleaned rows into RDS table 'sensor_readings'.")

# 4. VERIFY with a quick SQL check
cursor.execute("SELECT COUNT(*), ROUND(AVG(temperature), 2), ROUND(AVG(humidity), 1) FROM sensor_readings")
count, avg_temp, avg_hum = cursor.fetchone()
print(f"   RDS Verification -> Total Rows: {count} | Avg Temp: {avg_temp}°C | Avg Humidity: {avg_hum}%")

cursor.close()
conn.close()