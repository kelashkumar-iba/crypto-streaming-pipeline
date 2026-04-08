FROM apache/airflow:2.8.1-python3.11

USER root
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir dbt-postgres==1.7.4 psycopg2-binary==2.9.9

COPY dags/ /opt/airflow/dags/

COPY --chown=airflow:root dbt_project/ /usr/app/
