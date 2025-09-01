from airflow.decorators import dag, task
from datetime import datetime


@dag(
    dag_id="taskflow_api_example",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["lesson14"],
)
def taskflow_example():

    @task()
    def extract():
        data = {"order_id": 101, "amount": 400}
        return data

    @task()
    def transform(order):
        order["amount_gst"] = order["amount"] * 1.1
        return order

    @task()
    def load(order):
        print(f"✅ Loading order: {order}")

    order = extract()
    transformed = transform(order)
    load(transformed)


dag = taskflow_example()
