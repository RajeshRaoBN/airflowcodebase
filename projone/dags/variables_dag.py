from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime


def print_city():
    city = Variable.get("city")
    print(f"City: {city}")


with DAG(
    "variables_dag",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    PythonOperator(task_id="print_city", python_callable=print_city)