Perfect 👍 Running **Airflow on Docker** is the best way to get started without polluting your local environment. Let me walk you through step by step.

---

## 🔹 Step 1: Prerequisites

Make sure you have:

* **Docker** installed → [Download](https://docs.docker.com/get-docker/)
* **Docker Compose** installed → comes bundled with Docker Desktop
* At least **4GB RAM** allocated to Docker

Check versions:

```bash
docker --version
docker compose version
```

---

## 🔹 Step 2: Get Airflow Docker Setup

The Airflow community provides an official **docker-compose.yaml** file.

Run:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

This downloads the official **docker-compose.yaml** (already configured with Postgres, Redis, Scheduler, Webserver, Worker).

---

## 🔹 Step 3: Set Up Airflow Environment

Create required folders and environment files:

```bash
mkdir -p ./dags ./logs ./plugins

echo -e "AIRFLOW_UID=$(id -u)" > .env
```

This ensures Docker maps the correct user permissions.

---

## 🔹 Step 4: Initialize Airflow

Initialize the Airflow database and metadata:

```bash
docker compose up airflow-init
```

After success, you’ll see:

```
Airflow initdb complete
```

---

## 🔹 Step 5: Start Airflow

Now bring up all services:

```bash
docker compose up -d
```

This starts:

* **Webserver** (UI at [http://localhost:8080](http://localhost:8080))
* **Scheduler**
* **Worker**
* **Redis**
* **Postgres**

Default login:

* **Username:** `airflow`
* **Password:** `airflow`

---

## 🔹 Step 6: Stop & Restart

To stop:

```bash
docker compose down
```

To restart:

```bash
docker compose up -d
```

---

## 🔹 Step 7: Add Your DAGs

Place DAG files in the `./dags/` folder (next to your `docker-compose.yaml`).
They will automatically appear in the Airflow UI.

Example DAG: `dags/hello_dag.py`

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    "hello_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    task1 = BashOperator(
        task_id="say_hello",
        bash_command="echo 'Hello from Dockerized Airflow!'"
    )
```

Trigger it from the UI → you’ll see logs inside `./logs`.

---

✅ You now have Airflow running in **Docker**.
Would you like me to also show you how to **enable extra providers (AWS, GCP, etc.) in Docker** so you can connect Airflow to cloud services, or should we first run a **hands-on DAG in this Docker setup**?
