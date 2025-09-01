import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.providers.http.operators.http import HttpOperator


with DAG(
    dag_id="lesson5_vars_conns",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson5"],
) as dag:


    api_key = Variable.get("api_key")


    get_post = HttpOperator(
        task_id="get_post",
        http_conn_id="http_demo",
        endpoint=f"/posts/1", # api_key available if your API needs it
        method="GET",
        log_response=True,
    )