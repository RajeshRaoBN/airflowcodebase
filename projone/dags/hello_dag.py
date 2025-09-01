from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Define DAG
with DAG(
    dag_id="hello_dag",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",  # Run daily
    catchup=False,
) as dag:

    # Define tasks
    task1 = BashOperator(task_id="print_hello", bash_command="echo 'Hello, Airflow!'")

    task2 = BashOperator(task_id="print_date", bash_command="date")

    # Set dependencies
    task1 >> task2
