import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="lesson1_hello_dag",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["lesson1"],
) as dag:


    say_hello = BashOperator(
    task_id="say_hello",
    bash_command="echo 'Hello, Airflow from Docker!'"
    )


    print_date = BashOperator(
    task_id="print_date",
    bash_command="date"
    )


    say_hello >> print_date