""" from airflow import DAG
from airflow.operators.subdag import SubDagOperator
from airflow.operators.bash import BashOperator
from datetime import datetime


def subdag(parent_dag_name, child_dag_name, args):
    with DAG(
        f"{parent_dag_name}.{child_dag_name}", 
        default_args=args, 
        schedule="@daily"
    ) as dag:
        t1 = BashOperator(task_id="sub_task1", bash_command="echo 'Sub 1'")
        t2 = BashOperator(task_id="sub_task2", bash_command="echo 'Sub 2'")
        t1 >> t2
    return dag


args = {"start_date": datetime(2023, 1, 1)}


with DAG(
    "parent_dag", 
    default_args=args, 
    schedule="@daily", 
    catchup=False
) as dag:
    subdag_task = SubDagOperator(
        task_id="child_dag",
        subdag=subdag("parent_dag", "child_dag", args)
    ) """