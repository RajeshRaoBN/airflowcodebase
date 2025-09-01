from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime


def query_db():
    hook = PostgresHook(postgres_conn_id="pg_meta")
    result = hook.get_first("SELECT version();")
    print(result)


with DAG(
    "hook_dag",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    PythonOperator(task_id="query_db", python_callable=query_db)