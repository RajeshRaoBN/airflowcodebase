from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime


with DAG(
    "external_sensor_dag", 
    start_date=datetime(2023,1,1), 
    schedule=None, 
    catchup=False
) as dag:
    wait_for_dag = ExternalTaskSensor(
        task_id="wait_for_other_dag",
        external_dag_id="hello1_dag",
        external_task_id="say_hello",
        timeout=300
    )