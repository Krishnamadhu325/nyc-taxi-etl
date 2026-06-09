FROM apache/airflow:2.9.1
USER airflow
RUN pip install --no-cache-dir \
    apache-airflow-providers-google==10.14.0 \
    dbt-bigquery==1.8.0 \
    google-cloud-bigquery==3.20.1 \
    pandas==2.2.2 \
    pyarrow==16.0.0 \
    requests==2.31.0