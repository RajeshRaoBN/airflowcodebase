from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.bash import BashOperator
from datetime import datetime


with DAG(
    "taskgroup_dag",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    with TaskGroup("group1") as group1:
        t1 = BashOperator(task_id="t1", bash_command="echo 'Task 1'")
        t2 = BashOperator(task_id="t2", bash_command="echo 'Task 2'")


    with TaskGroup("group2") as group2:
        t3 = BashOperator(task_id="t3", bash_command="echo 'Task 3'")
        t4 = BashOperator(task_id="t4", bash_command="echo 'Task 4'")


    group1 >> group2