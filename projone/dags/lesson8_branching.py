import pendulum
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator


def choose_path(**context):
    # Example: pick based on weekday (Mon=0)
    weekday = context["logical_date"].weekday()
    return "monday_path" if weekday == 0 else "other_days"


with DAG(
    dag_id="lesson8_branching",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson8"],
) as dag:

    branch = BranchPythonOperator(
        task_id="branch",
        python_callable=choose_path,
    )

    monday_path = EmptyOperator(task_id="monday_path")
    other_days = EmptyOperator(task_id="other_days")
    join = EmptyOperator(task_id="join", trigger_rule="none_failed_min_one_success")

    branch >> [monday_path, other_days] >> join
