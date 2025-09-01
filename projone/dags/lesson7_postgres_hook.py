import pendulum
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator




def query_meta_db():
    hook = PostgresHook(postgres_conn_id="pg_meta")
    records = hook.get_records("SELECT COUNT(*) FROM dag")
    print("DAGs in metadata:", records[0][0])


with DAG(
    dag_id="lesson7_postgres_hook",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson7"],
) as dag:


    run_query = PythonOperator(
        task_id="run_query",
        python_callable=query_meta_db,
    )