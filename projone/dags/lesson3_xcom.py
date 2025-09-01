import pendulum
from airflow.decorators import dag, task


@dag(
    dag_id="lesson3_xcom",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson3"],
)
def lesson3():


    @task
    def extract():
        return {"name": "Airflow", "version": 2}


    @task
    def transform(payload: dict):
        payload["version_str"] = f"v{payload['version']}"
        return payload


    @task
    def load(final_payload: dict):
        print("Final:", final_payload)


    load(transform(extract()))


lesson3()