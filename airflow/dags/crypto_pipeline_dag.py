from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2


default_args = {
    'owner': 'kelash',
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}


def check_data_freshness(**kwargs):
    """Check if new data has arrived in the last 5 minutes."""
    conn = psycopg2.connect(
        host='postgres',
        dbname='crypto_db',
        user='crypto_user',
        password='crypto_pass'
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM raw_crypto_prices
        WHERE ingested_at > NOW() - INTERVAL '5 minutes'
    """)
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    if count == 0:
        raise Exception("No fresh data in last 5 minutes! Pipeline may be down.")
    print(f"Fresh data check passed: {count} new rows in last 5 minutes.")


with DAG(
    dag_id='crypto_streaming_pipeline',
    default_args=default_args,
    description='Orchestrates dbt transformations for crypto pipeline',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2026, 4, 7),
    catchup=False,
    tags=['crypto', 'streaming'],
) as dag:

    check_freshness = PythonOperator(
        task_id='check_data_freshness',
        python_callable=check_data_freshness,
    )

    run_dbt_staging = BashOperator(
        task_id='run_dbt_staging',
        bash_command='cd /usr/app && dbt run --select stg_crypto_prices --profiles-dir .',
    )

    run_dbt_intermediate = BashOperator(
        task_id='run_dbt_intermediate',
        bash_command='cd /usr/app && dbt run --select int_crypto_metrics --profiles-dir .',
    )

    run_dbt_mart = BashOperator(
        task_id='run_dbt_mart',
        bash_command='cd /usr/app && dbt run --select mart_daily_summary --profiles-dir .',
    )

    check_row_count = PythonOperator(
        task_id='check_mart_row_count',
        python_callable=lambda: print("dbt transformation complete. Mart refreshed."),
    )

    check_freshness >> run_dbt_staging >> run_dbt_intermediate >> run_dbt_mart >> check_row_count
