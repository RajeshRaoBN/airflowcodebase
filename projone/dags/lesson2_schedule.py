import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="lesson2_schedule",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="*/15 * * * *", # every hour on the hour
    catchup=True, # run only future schedules when unpaused
    tags=["lesson2"],
) as dag:


# Built-in macro examples: ds, ts, dag_run, logical_date
    print_context = BashOperator(
        task_id="print_context",
        bash_command=(
            "echo 'Run id: {{ run_id }}'; "
            "echo 'Logical date: {{ logical_date }}'; "
            "echo 'ds (YYYY-MM-DD): {{ ds }}'"
        ),
    )