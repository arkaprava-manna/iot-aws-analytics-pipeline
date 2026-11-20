# End-to-End IoT Data Processing & Analytics Pipeline (AWS + Python)

A cloud-based IoT data analytics pipeline that simulates sensor telemetry, stores raw data in **Amazon S3**, runs a **Python ETL** workflow to clean and load records into **Amazon RDS (MySQL)**, and visualizes descriptive analytics through an interactive **Streamlit** dashboard.

## System Architecture

```text
IoT Data Simulator (Python)
        │
        ▼ (sensor_data.csv)
   Amazon S3 Bucket
        │
        ▼ (Extract via boto3)
   Python ETL Pipeline (Clean nulls, drop duplicates, enforce types)
        │
        ▼ (Load via mysql-connector)
 Amazon RDS (MySQL 8.4)
        │
        ▼ (SQL Descriptive Analytics)
Streamlit & Plotly Dashboard
```

## Tech Stack
* **Cloud Services:** Amazon S3, Amazon RDS (MySQL `db.t4g.micro`), AWS IAM
* **Language & ETL:** Python (`boto3`, `pandas`, `numpy`, `mysql-connector-python`, `python-dotenv`)
* **Visualization:** Streamlit, Plotly

## Key Pipeline Highlights
1. **IoT Dataset Generation (`generate_data.py`):** Simulates 505 raw telemetry rows across 5 sensors (`501`–`505`) with timestamps, temperature, and humidity, including intentional missing values and duplicate rows to validate the ETL layer.
2. **Cloud Storage (Amazon S3):** Stores raw CSV data securely in S3.
3. **ETL Processing (`etl_pipeline.py`):** Extracts the CSV directly from S3 into memory, removes 5 duplicate records and 5 null temperature rows, formats timestamps, and loads **495 cleaned records** into the `sensor_readings` table in Amazon RDS.
4. **Descriptive Analytics & Dashboard (`dashboard.py`):** Queries Amazon RDS using SQL aggregations (`COUNT`, `AVG`, `MIN`, `MAX`, `GROUP BY`) to display live KPIs, temperature trends over time, sensor-wise averages, humidity distribution, and sample database records.

## Project Structure
```text
iot-aws-project/
├── generate_data.py    # Simulates IoT sensor readings (sensor_data.csv)
├── etl_pipeline.py     # Extracts from S3, transforms data, loads into RDS
├── dashboard.py        # Streamlit & Plotly analytics dashboard
├── sensor_data.csv     # Sample generated IoT dataset
├── requirements.txt    # Python dependencies
├── .gitignore          # Excludes .env and cache files
└── README.md           # Project documentation
```

## Setup & Usage

### 1. Clone the Repository & Install Dependencies
```bash
git clone [https://github.com/arkaprava-manna/iot-aws-analytics-pipeline.git](https://github.com/arkaprava-manna/iot-aws-analytics-pipeline.git)
cd iot-aws-analytics-pipeline
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory with your AWS and RDS credentials:
```env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
BUCKET_NAME=your_s3_bucket_name
FILE_KEY=sensor_data.csv

RDS_HOST=your_rds_endpoint.rds.amazonaws.com
RDS_USER=admin
RDS_PASS=your_rds_password
RDS_DB=iot_db
```

### 3. Run the Pipeline
```bash
# 1. Generate sample IoT dataset
python generate_data.py

# 2. Upload sensor_data.csv to your S3 bucket, then run the ETL pipeline
python etl_pipeline.py

# 3. Launch the interactive dashboard
python -m streamlit run dashboard.py
```

## Sample Analytics Output
* **Total Cleaned Readings:** 495
* **Active Sensors:** 5 (`501`–`505`)
* **Average Temperature:** 28.96 °C (Min: 22.3 °C | Max: 36.7 °C)
* **Average Humidity:** 61.8%