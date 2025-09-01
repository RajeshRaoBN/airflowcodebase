import pendulum
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
import os


DATA_PATH = os.path.join(
    os.environ.get("AIRFLOW_HOME", "/opt/airflow"), "dags", "data", "ready.txt"
)


with DAG(
    dag_id="lesson6_sensor",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson6"],
) as dag:

    echo_pwd_task = BashOperator(
        task_id="echo_current_directory",
        bash_command='echo "Current working directory: $PWD"',
    )

    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath=DATA_PATH,
        poke_interval=30,
        mode="reschedule",
        timeout=60 * 60,
    )

    process = BashOperator(
        task_id="process",
        bash_command=f"wc -c {DATA_PATH}"
    )

    echo_pwd_task >> wait_for_file >> process
