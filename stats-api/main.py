import os

import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        dbname=os.getenv("DB_NAME", "crypto_db"),
        user=os.getenv("DB_USER", "crypto_user"),
        password=os.getenv("DB_PASSWORD", "crypto_pass"),
    )


@app.get("/api/stats")
def stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT coin) as distinct_coins,
            MIN(ingested_at) as first_record,
            MAX(ingested_at) as last_record
        FROM raw_crypto_prices
    """)
    row = cur.fetchone()
    cur.execute("SELECT DISTINCT coin FROM raw_crypto_prices ORDER BY coin")
    coins = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {
        "total_rows": row[0],
        "distinct_coins": row[1],
        "first_record": str(row[2]),
        "last_record": str(row[3]),
        "coins": coins,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}
