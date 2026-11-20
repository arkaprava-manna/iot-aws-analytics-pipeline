import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
num_rows = 500
start_time = datetime(2026, 10, 1, 9, 0, 0)

data = {
    "timestamp": [start_time + timedelta(minutes=5 * i) for i in range(num_rows)],
    "sensor_id": np.random.choice([501, 502, 503, 504, 505], size=num_rows),
    "temperature": np.round(np.random.normal(loc=29.0, scale=2.5, size=num_rows), 1),
    "humidity": np.random.randint(50, 75, size=num_rows),
}

df = pd.DataFrame(data)

# Add 5 missing values and 5 duplicate rows to demonstrate ETL cleaning later
df.loc[10:14, "temperature"] = np.nan
df = pd.concat([df, df.iloc[:5]], ignore_index=True)

df.to_csv("sensor_data.csv", index=False)
print(f"Done! Generated sensor_data.csv with {len(df)} rows.")