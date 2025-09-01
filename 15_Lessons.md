# Apache Airflow — 15 Lessons with Step‑by‑Step Hands‑On (Docker setup)

> Default environment: **Airflow on Docker Compose**. If you already ran the official compose file (Postgres, Redis, Webserver, Scheduler, Worker), you’re ready. All paths assume the compose root directory where your `dags/`, `logs/`, `plugins/` live and `docker compose` is available.

---

## Common One‑Time Setup (if not done yet)

1. **Download official compose**

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

2. **Create folders & user mapping**

```bash
mkdir -p ./dags ./logs ./plugins
printf "AIRFLOW_UID=$(id -u)\n" > .env
```

3. **Initialize & start**

```bash
docker compose up airflow-init
# After it completes
docker compose up -d
```

4. **Open UI** → [http://localhost:8080](http://localhost:8080) (default creds: `airflow` / `airflow`).

---

# Lesson 1 — Airflow Basics & Your First DAG

**Goal:** Understand DAGs, tasks, dependencies. Run a simple pipeline.

### Steps

1. Create file `dags/lesson1_hello_dag.py`:

```python
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
```

2. In UI, **unpause** `lesson1_hello_dag` and **Trigger DAG**.
3. Open **Graph** → click each task → **Log** → confirm output.

**Validate:** You see two green tasks; logs show the echoed string and system date.

**If issues:** Ensure file is inside `./dags/` (mounted into container at `/opt/airflow/dags`).

---

# Lesson 2 — Scheduling, Catchup & Templating

**Goal:** Master schedules, logical dates, Jinja templates.

### Steps

1. Create `dags/lesson2_schedule.py`:

```python
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="lesson2_schedule",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 * * * *",  # every hour on the hour
    catchup=False,  # run only future schedules when unpaused
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
```

2. Unpause and **Trigger DAG** manually to inspect templated values.
3. Change `schedule="@daily"` or `"*/15 * * * *"` and observe next runs.

**Validate:** Logs show templated values for each run.

**Tip:** Set `catchup=True` + historical `start_date` to backfill; then **clear** tasks with “Past” selected to re-run.

---

# Lesson 3 — Dependencies & XCom (TaskFlow API)

**Goal:** Pass data between tasks using XCom with the modern TaskFlow API.

### Steps

1. Create `dags/lesson3_xcom.py`:

```python
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
```

2. Trigger DAG → open logs for each task; observe returned dicts.

**Validate:** `load` prints the enriched object; XCom tab shows values.

**Note:** With TaskFlow, return values automatically go to XCom and can be passed as function args.

---

# Lesson 4 — Core Operators (Bash, Python, Empty)

**Goal:** Use common operators and retries.

### Steps

1. Create `dags/lesson4_operators.py`:

```python
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
        task_id="bash",
        bash_command="echo 'Bash step OK'"
    )

    py = PythonOperator(
        task_id="python",
        python_callable=do_python,
    )

    end = EmptyOperator(task_id="end")

    start >> [bash, py] >> end
```

2. Trigger and check logs. Observe retry logic by temporarily changing `bash_command` to `exit 1` to see retries.

---

# Lesson 5 — Variables & Connections (UI & CLI)

**Goal:** Store config (Variables) and credentials (Connections) and use them.

### Steps

1. **Set a Variable** (UI → Admin → Variables) with key `api_key` and a dummy value.

   * CLI (inside webserver container):

   ```bash
   docker compose exec airflow-webserver \
     airflow variables set api_key "MY_DEMO_KEY"
   ```
2. **Create an HTTP Connection** (UI → Admin → Connections):

   * Conn Id: `http_demo`
   * Conn Type: `HTTP`
   * Host: `https://jsonplaceholder.typicode.com`
3. Use them in a DAG: `dags/lesson5_vars_conns.py`:

```python
import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.providers.http.operators.http import SimpleHttpOperator

with DAG(
    dag_id="lesson5_vars_conns",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson5"],
) as dag:

    api_key = Variable.get("api_key")

    get_post = SimpleHttpOperator(
        task_id="get_post",
        http_conn_id="http_demo",
        endpoint=f"/posts/1",  # api_key available if your API needs it
        method="GET",
        log_response=True,
    )
```

4. Trigger and view logs; you should see the JSON payload.

**Note:** If `SimpleHttpOperator` is missing, add provider. See **Lesson 7 – Providers**.

---

# Lesson 6 — Sensors (Waiting for Events)

**Goal:** Wait for a file before processing. Use efficient reschedule mode.

### Steps

1. Create a shared folder for files inside `dags/` so containers can see it:

```bash
mkdir -p ./dags/data
```

2. Create `dags/lesson6_sensor.py`:

```python
import pendulum
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator

DATA_PATH = "/opt/airflow/dags/data/ready.txt"

with DAG(
    dag_id="lesson6_sensor",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson6"],
) as dag:

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

    wait_for_file >> process
```

3. Trigger DAG. It will **wait**.
4. In another terminal, create the file:

```bash
echo "hello" > ./dags/data/ready.txt
```

5. The Sensor turns success and `process` runs.

---

# Lesson 7 — Providers, Hooks & External Services

**Goal:** Install a provider and use a Hook to query a database.

### Steps

1. **Add provider** to the image via the compose’s env var:

   * Edit `docker-compose.yaml` service `airflow-webserver` (and `scheduler`, `worker`) and add:

   ```yaml
   environment:
     - PIP_ADDITIONAL_REQUIREMENTS=apache-airflow-providers-postgres apache-airflow-providers-http
   ```

   (If the key exists, append to it.)
2. **Recreate** containers to install packages:

```bash
docker compose down
docker compose up -d --build
```

3. **Add a Postgres connection** (to the metadata DB for demo):

   * UI → Admin → Connections → **+**
   * Conn Id: `pg_meta`
   * Conn Type: `Postgres`
   * Host: `postgres`
   * Schema: `airflow`
   * Login: `airflow`  Password: `airflow`  Port: `5432`
4. Create `dags/lesson7_postgres_hook.py`:

```python
import pendulum
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator


def query_meta_db():
    hook = PostgresHook(postgres_conn_id="pg_meta")
    records = hook.get_records("SELECT COUNT(*) FROM dag")
    print("DAGs in metadata:", records[0][0])

with DAG(
    dag_id="lesson7_postgres_hook",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson7"],
) as dag:

    run_query = PythonOperator(
        task_id="run_query",
        python_callable=query_meta_db,
    )
```

5. Trigger and check logs; you should see a count.

**Note:** For real projects, point to **external** Postgres, not metadata.

---

# Lesson 8 — Branching & Conditional Logic

**Goal:** Use `BranchPythonOperator` to choose a path.

### Steps

1. Create `dags/lesson8_branching.py`:

```python
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
        provide_context=True,
    )

    monday_path = EmptyOperator(task_id="monday_path")
    other_days = EmptyOperator(task_id="other_days")
    join = EmptyOperator(task_id="join", trigger_rule="none_failed_min_one_success")

    branch >> [monday_path, other_days] >> join
```

2. Trigger several times; observe which branch runs.

---

# Lesson 9 — Dynamic Task Mapping (Fan‑out)

**Goal:** Create tasks dynamically at runtime with TaskFlow `.expand()`.

### Steps

1. Create `dags/lesson9_dynamic_mapping.py`:

```python
import pendulum
from airflow.decorators import dag, task

@dag(
    dag_id="lesson9_dynamic_mapping",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson9"],
)
def dynamic_example():

    @task
    def list_files():
        return ["a.csv", "b.csv", "c.csv"]

    @task
    def process(file_name: str):
        print("Processing", file_name)

    files = list_files()
    process.expand(file_name=files)

dynamic_example()
```

2. Trigger → see 3 parallel mapped tasks.

**Tip:** Combine with Sensors to map only discovered files.

---

# Lesson 10 — Task Groups (Refactor Large DAGs)

**Goal:** Organize complex DAGs for readability.

### Steps

1. Create `dags/lesson10_task_groups.py`:

```python
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup

with DAG(
    dag_id="lesson10_task_groups",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson10"],
) as dag:

    with TaskGroup("extract") as extract:
        a = BashOperator(task_id="a", bash_command="echo extract A")
        b = BashOperator(task_id="b", bash_command="echo extract B")

    with TaskGroup("transform") as transform:
        c = BashOperator(task_id="c", bash_command="echo transform C")
        d = BashOperator(task_id="d", bash_command="echo transform D")

    load = BashOperator(task_id="load", bash_command="echo load")

    extract >> transform >> load
```

2. Trigger → Graph view shows grouped boxes.

---

# Lesson 11 — Monitoring, Logging & Alerting

**Goal:** Inspect logs, failures, retries; add simple alert callbacks.

### Steps

1. Create `dags/lesson11_monitoring.py` with a failing task then alert:

```python
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def will_fail():
    raise RuntimeError("Intentional failure for alert demo")


def on_failure_callback(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    print(f"[ALERT] {dag_id}.{task_id} failed! Check logs.")

with DAG(
    dag_id="lesson11_monitoring",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args={"retries": 1},
    on_failure_callback=on_failure_callback,
    tags=["lesson11"],
) as dag:

    fail = PythonOperator(task_id="fail", python_callable=will_fail)
```

2. Trigger → see failure in UI and alert message printed in logs.

**Next:** Replace `on_failure_callback` with Slack/Email operators once SMTP/Slack webhook are configured.

---

# Lesson 12 — Executors & Parallelism (Celery/Local)

**Goal:** Experience parallel execution and concurrency controls.

### Steps

1. Create `dags/lesson12_parallel.py`:

```python
import time
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def sleeper(n):
    time.sleep(n)

with DAG(
    dag_id="lesson12_parallel",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson12"],
    max_active_tasks=10,
) as dag:

    tasks = [
        PythonOperator(task_id=f"sleep_{i}", python_callable=sleeper, op_args=[20])
        for i in range(1, 7)
    ]
```

2. Trigger and watch tasks in **Graph** & **Gantt**. With CeleryExecutor, multiple tasks run across worker processes.
3. Tune DAG-level `max_active_tasks`, task `pool`, and global `parallelism` (Airflow config) to observe limits.

---

# Lesson 13 — Packaging with Docker & (Intro to) Kubernetes

**Goal:** Customize the image and understand K8s deployment basics.

### Steps (Docker image with extra libs)

1. Create `Dockerfile` in project root:

```dockerfile
FROM apache/airflow:2.9.3
# Install extra Python libs and providers
RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres \
    apache-airflow-providers-http \
    pandas requests
```

2. Build & use the image in `docker-compose.yaml` (`image:` for webserver/scheduler/worker).
3. `docker compose up -d --build`.

### Steps (Kubernetes high-level)

1. Ensure a cluster (e.g., kind/minikube) and a registry.
2. Push your custom Airflow image to the registry.
3. Use the official Helm chart or manifests to deploy Webserver, Scheduler, and (for Celery/K8sExecutor) Workers.
4. Mount or sync DAGs via Git-Sync sidecar or build DAGs into the image.

*(Full Helm walkthrough can be added later once your cluster is ready.)*

---

# Lesson 14 — CI/CD for DAGs (GitHub Actions)

**Goal:** Version control DAGs and auto-deploy to Dockerized Airflow.

### Steps (Image-based deploy)

1. Put DAGs under `dags/` and commit to GitHub.
2. Use the Dockerfile (Lesson 13) to bake DAGs into the image.
3. Create `.github/workflows/deploy.yml`:

```yaml
name: build-and-push-airflow
on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY }}
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - name: Build
        run: docker build -t ${{ secrets.REGISTRY }}/airflow:${{ github.sha }} .
      - name: Push
        run: docker push ${{ secrets.REGISTRY }}/airflow:${{ github.sha }}
```

4. Pull the new image on your Airflow host and restart services.

### Steps (Volume/sync alternative)

* Use a Git pull or rsync in a small script/container that syncs `dags/` into `/opt/airflow/dags` when main updates.

---

# Lesson 15 — End‑to‑End ETL (API → Transform → Store)

**Goal:** Build a small ETL using TaskFlow, HTTP provider, and local storage.

### Steps

1. Ensure **HTTP provider** is installed (Lesson 7) and connection `http_demo` exists pointing to `https://jsonplaceholder.typicode.com`.
2. Create `dags/lesson15_etl.py`:

```python
import json
import pendulum
from pathlib import Path
from airflow.decorators import dag, task
from airflow.providers.http.hooks.http import HttpHook

DATA_DIR = Path("/opt/airflow/dags/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = DATA_DIR / "posts_raw.json"
CLEAN_PATH = DATA_DIR / "posts_clean.json"

@dag(
    dag_id="lesson15_etl",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lesson15"],
)
def etl():

    @task
    def extract():
        hook = HttpHook(http_conn_id="http_demo", method="GET")
        resp = hook.run("/posts")
        data = resp.json()
        RAW_PATH.write_text(json.dumps(data))
        return len(data)

    @task
    def transform(n_records: int):
        data = json.loads(RAW_PATH.read_text())
        # simple transform: keep only id & title
        cleaned = [{"id": d["id"], "title": d["title"]} for d in data]
        CLEAN_PATH.write_text(json.dumps(cleaned, indent=2))
        return {"input": n_records, "output": len(cleaned)}

    @task
    def load(stats: dict):
        print("ETL stats:", stats)
        print("Clean file at:", CLEAN_PATH)

    load(transform(extract()))

etl()
```

3. Trigger and verify files in `./dags/data/` on your host.

**Extend:** Swap `load` to insert into Postgres using `PostgresHook` (Lesson 7).

---

## Bonus: Troubleshooting Cheatsheet

* **DAG doesn’t appear**: filename under `dags/`, valid Python, no syntax errors; check Webserver logs.
* **ImportError for provider operator/hook**: add the right provider via `PIP_ADDITIONAL_REQUIREMENTS` and recreate containers.
* **Permissions**: ensure `.env` has `AIRFLOW_UID` and host folders are writable by containers.
* **Connection fails**: check service name (e.g., `postgres`), port mappings, credentials; test from within container with `psql` or `curl`.
* **Stuck tasks**: look at Scheduler & Worker logs; confirm Executor is running and Redis/DB are healthy.

---

## Where to go next

* Add real cloud providers (AWS/GCP/Azure) and practice ingesting files to object storage, running SQL in warehouses, and orchestrating ML jobs.
* Convert Lesson 15 into a daily job with backfills and data validation.
* Add Slack/email notifications and data quality checks (Great Expectations or SQL tests).
