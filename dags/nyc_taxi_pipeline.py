"""NYC Taxi ETL Pipeline — ingest -> BigQuery -> dbt"""
from datetime import datetime, timedelta
import os, tempfile, requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "nyc-taxi-etl-498205")
BQ_DATASET     = os.environ.get("BQ_DATASET", "nyc_taxi")
BQ_TABLE       = "raw_trips"
DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

default_args = {
    "owner": "beatrice",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def download_and_load(**context):
    import pandas as pd
    from google.cloud import bigquery

    print(f"Downloading: {DATA_URL}")
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        r = requests.get(DATA_URL, stream=True, timeout=120)
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            tmp.write(chunk)
        tmp_path = tmp.name

    df = pd.read_parquet(tmp_path)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")

    client = bigquery.Client(project=GCP_PROJECT_ID)
    table_ref = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Done. Rows written: {job.output_rows:,}")
    os.unlink(tmp_path)

with DAG(
    dag_id="nyc_taxi_pipeline",
    default_args=default_args,
    description="NYC Taxi: ingest -> BigQuery -> dbt",
    schedule_interval="@monthly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["nyc-taxi", "bigquery", "dbt"],
) as dag:

    ingest = PythonOperator(
        task_id="download_and_load_to_bigquery",
        python_callable=download_and_load,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt --target prod",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir /opt/airflow/dbt --target prod",
    )

    ingest >> dbt_run >> dbt_test