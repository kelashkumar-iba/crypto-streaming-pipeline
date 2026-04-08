import json
import os
import time
import psycopg2
from kafka import KafkaConsumer


BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC_NAME = os.environ.get('TOPIC_NAME', 'crypto-prices')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'crypto_db')
DB_USER = os.environ.get('DB_USER', 'crypto_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'crypto_pass')


def safe_deserializer(v):
    try:
        return json.loads(v.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Bad message skipped: {e}")
        return None


def connect_postgres():
    for attempt in range(10):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Connected to PostgreSQL.")
            return conn
        except Exception as e:
            print(f"Attempt {attempt+1}/10 - PostgreSQL not ready: {e}")
            time.sleep(5)
    raise ConnectionError("Could not connect to PostgreSQL after 10 attempts.")


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_crypto_prices (
                id SERIAL PRIMARY KEY,
                coin VARCHAR(50),
                price_usd NUMERIC(18, 8),
                change_24h NUMERIC(10, 4),
                last_updated BIGINT,
                ingested_at TIMESTAMP DEFAULT NOW()
            );
        """)
    conn.commit()
    print("Table raw_crypto_prices ready.")


def create_consumer():
    for attempt in range(10):
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=BOOTSTRAP_SERVERS,
                group_id='crypto-consumer-group',
                value_deserializer=safe_deserializer,
                auto_offset_reset='earliest'
            )
            print("Connected to Redpanda.")
            return consumer
        except Exception as e:
            print(f"Attempt {attempt+1}/10 - Redpanda not ready: {e}")
            time.sleep(5)
    raise ConnectionError("Could not connect to Redpanda after 10 attempts.")


def main():
    conn = connect_postgres()
    create_table(conn)
    consumer = create_consumer()

    print("Listening for messages...")
    for message in consumer:
        if message.value is None:
            continue

        data = message.value
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO raw_crypto_prices (coin, price_usd, change_24h, last_updated)
                    VALUES (%s, %s, %s, %s)
                """, (
                    data.get('coin'),
                    data.get('price_usd'),
                    data.get('change_24h'),
                    data.get('last_updated'),
                ))
            conn.commit()
            print(f"Inserted: {data.get('coin')} @ ${data.get('price_usd')}")

        except Exception as e:
            print(f"DB insert error: {e}")
            conn.rollback()


if __name__ == '__main__':
    main()
