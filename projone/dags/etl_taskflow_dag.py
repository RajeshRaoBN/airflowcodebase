import requests
import pandas as pd
from airflow.decorators import dag, task
from datetime import datetime


@dag(
    dag_id="etl_taskflow_pipeline",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["lesson15"],
)
def etl_pipeline():

    @task()
    def extract():
        url = "https://jsonplaceholder.typicode.com/users"
        response = requests.get(url)
        data = response.json()
        return data

    @task()
    def transform(data):
        df = pd.DataFrame(data)
        df = df[["id", "name", "email"]]
        return df.to_dict(orient="records")

    @task()
    def load(data):
        df = pd.DataFrame(data)
        output_path = "/opt/airflow/dags/data/users.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ Data written to {output_path}")

    raw_data = extract()
    cleaned = transform(raw_data)
    load(cleaned)


dag = etl_pipeline()
