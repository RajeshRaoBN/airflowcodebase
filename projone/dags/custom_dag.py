from airflow import DAG
from datetime import datetime
from custom_operator import HelloOperator


with DAG(
    dag_id="custom_dag", 
    start_date=datetime(2023,1,1), 
    schedule=None, catchup=False
) as dag:
    HelloOperator(
        task_id="hello_task", 
        name="World ProjOne"
    )