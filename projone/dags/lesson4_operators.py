import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


def do_python():
    print("Processing in Python…")


with DAG(
    dag_id="lesson4_operators",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args={"retries": 2},
    tags=["lesson4"],
) as dag:

    start = EmptyOperator(task_id="start")

    bash = BashOperator(
        task_id="bash1",
        bash_command="echo 'Bash step OK'",
    )

    bash_task = BashOperator(
        task_id="bash2", 
        bash_command="echo 'Error: Failed to copy the file.' && exit 1"
    )

    py = PythonOperator(
        task_id="python",
        python_callable=do_python,
    )

    end = EmptyOperator(task_id="end")

    start >> [bash, py] >> end
