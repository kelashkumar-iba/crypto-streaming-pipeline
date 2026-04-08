# 🚀 Crypto Streaming Pipeline

**A production-grade, end-to-end real-time data pipeline** that ingests live cryptocurrency prices from 10 coins, streams them through a message broker, transforms raw data into analytics-ready marts, and visualizes insights on a live dashboard — fully containerized and orchestrated.

> Built as part of the [Data Engineering Accelerated Mastery](https://github.com/kelashkumar-iba) program · April 2026

---

## 📊 Live Dashboard

![Crypto Dashboard](screenshots/dashboard.png)

*Real-time Metabase dashboard showing price trends, volatility analysis, 24h performance, and daily summaries across 10 cryptocurrencies.*

---

## 🏗️ Architecture

![Architecture Diagram](screenshots/architecture.png)

### Data Flow

```
CoinGecko API ──► Python Producer ──► Redpanda (Kafka) ──► Python Consumer ──► PostgreSQL
                                                                                    │
                                                                                    ▼
                                                                    dbt (staging → intermediate → mart)
                                                                                    │
                                                                                    ▼
                                                                            Metabase Dashboard
                                                                                    ▲
                                                                                    │
                                                                        Airflow (orchestration)
```

### How It Works

1. **Producer** pulls real-time prices for 10 cryptocurrencies (Bitcoin, Ethereum, Solana, Cardano, Polkadot, Chainlink, Avalanche, Polygon, Dogecoin, Shiba Inu) from the CoinGecko API every 60 seconds.

2. **Redpanda** (Kafka-compatible message broker) decouples the producer from the consumer. Messages are durably stored in the `crypto-prices` topic, surviving consumer downtime.

3. **Consumer** reads messages from Redpanda, deserializes JSON, and inserts rows into PostgreSQL's `raw_crypto_prices` table with defensive error handling (poison pill protection).

4. **dbt** transforms raw data through three layers:
   - **Staging** — cleans column types, filters nulls, converts unix timestamps
   - **Intermediate** — calculates price changes (LAG), 5-period moving averages
   - **Mart** — aggregates daily summaries: avg/high/low price, spread, reading counts

5. **Airflow** orchestrates dbt every 5 minutes: checks data freshness → runs staging → intermediate → mart. If no fresh data exists, the DAG fails early with alerting.

6. **Metabase** dashboards query the mart tables, providing live analytics without any manual refresh.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Ingestion** | Python, CoinGecko API | Pull real-time crypto prices |
| **Streaming** | Redpanda (Kafka-compatible) | Decouple producer/consumer, message durability |
| **Storage** | PostgreSQL 14 | Persistent relational storage |
| **Transformation** | dbt 1.7.4 | SQL-based staging → intermediate → mart layers |
| **Orchestration** | Apache Airflow 2.8.1 | Schedule dbt runs, data freshness checks |
| **Visualization** | Metabase | Interactive dashboards on mart tables |
| **Containerization** | Docker & Docker Compose | All 8 services run in isolated containers |

---

## 📸 Screenshots

### All Services Running
![Docker Services](screenshots/docker-ps.png)

*8 containers running simultaneously: Redpanda, PostgreSQL, Producer, Consumer, dbt, Airflow (webserver + scheduler), and Metabase.*

### Producer — Streaming 10 Coins
![Producer Logs](screenshots/producer-logs.png)

*Producer pulling live prices from CoinGecko API and publishing to Redpanda every 60 seconds.*

### Consumer — Writing to PostgreSQL
![Consumer Logs](screenshots/consumer-logs.png)

*Consumer reading from Redpanda, deserializing JSON, and inserting into PostgreSQL with retry logic.*

### dbt — Three-Layer Transformation
![dbt Output](screenshots/dbt-run.png)

*dbt executing staging (view) → intermediate (view) → mart (table) in under 2 seconds.*

### Airflow — Automated Orchestration
![Airflow DAG](screenshots/airflow-dag.png)

*DAG running every 5 minutes: freshness check → staging → intermediate → mart → confirmation. All tasks green.*

### PostgreSQL — Analytics-Ready Mart
![Mart Data](screenshots/mart-data.png)

*Final mart table showing daily summaries per coin — ready for dashboard consumption.*

---

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20+
- Docker Compose 1.29+

### Launch the Entire Pipeline

```bash
# Clone the repository
git clone https://github.com/kelash/crypto-streaming-pipeline.git
cd crypto-streaming-pipeline

# Stop any local PostgreSQL to free port 5432
sudo systemctl stop postgresql

# Build and start all services
docker-compose up --build -d

# Verify all containers are running
docker-compose ps

# Run dbt transformations
docker-compose run --rm dbt run --profiles-dir .
```

### Access the Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Metabase Dashboard** | http://localhost:3000 | Setup on first visit |
| **Airflow UI** | http://localhost:8080 | admin / admin |
| **PostgreSQL** | localhost:5432 | crypto_user / crypto_pass |
| **Redpanda** | localhost:9092 | — |

### Connect Metabase to PostgreSQL
When Metabase asks for database connection:
- Type: PostgreSQL
- Host: `postgres`
- Port: `5432`
- Database: `crypto_db`
- Username: `crypto_user`
- Password: `crypto_pass`

---

## 📁 Project Structure

```
crypto-streaming-pipeline/
├── docker-compose.yml              # Orchestrates all 8 services
├── producer/
│   ├── Dockerfile                  # Python 3.11-slim base image
│   ├── requirements.txt            # kafka-python, requests
│   └── producer.py                 # CoinGecko API → Redpanda producer
├── consumer/
│   ├── Dockerfile                  # Python 3.11-slim base image
│   ├── requirements.txt            # kafka-python, psycopg2-binary
│   └── consumer.py                 # Redpanda → PostgreSQL consumer
├── dbt_crypto/
│   ├── Dockerfile                  # dbt-postgres base image
│   ├── dbt_project.yml             # dbt configuration
│   ├── profiles.yml                # PostgreSQL connection
│   └── models/
│       ├── staging/
│       │   └── stg_crypto_prices.sql
│       ├── intermediate/
│       │   └── int_crypto_metrics.sql
│       └── mart/
│           └── mart_daily_summary.sql
├── airflow/
│   ├── Dockerfile                  # Airflow + dbt-postgres
│   ├── dags/
│   │   └── crypto_pipeline_dag.py  # 5-min orchestration DAG
│   └── dbt_project/                # dbt files for Airflow container
│       ├── dbt_project.yml
│       ├── profiles.yml
│       └── models/
│           ├── staging/
│           ├── intermediate/
│           └── mart/
├── screenshots/                    # Dashboard & architecture images
└── README.md
```

---

## 🔧 Engineering Decisions

### Why Redpanda over Kafka?
Redpanda speaks the exact Kafka protocol but runs without the JVM, consuming ~80% less memory. Ideal for local development on a student laptop running 8 containers simultaneously. In production, the choice between Kafka and Redpanda depends on organizational needs — the code is identical either way.

### Why dbt views for staging/intermediate?
Staging and intermediate models are lightweight SQL transformations that don't need physical storage. Only the mart layer materializes as a table, since that's what Metabase queries repeatedly. This minimizes storage overhead while keeping dashboard queries fast.

### Why Airflow checks data freshness first?
If the producer or Redpanda is down, running dbt on stale data wastes compute and could mask pipeline failures. The freshness check fails fast and surfaces the real problem: no new data is flowing.

### Why `PYTHONUNBUFFERED: "1"`?
Python buffers stdout inside Docker containers (no TTY attached). Without this flag, `docker logs` shows nothing even when the code is running correctly. This is a standard production practice for Python in Docker.

### Why retry loops in Producer and Consumer?
`depends_on` in Docker Compose only waits for a container to **start**, not for the service to be **ready**. PostgreSQL and Redpanda take several seconds to accept connections after container startup. Retry loops handle this gracefully without crashing.

---

## 🧠 What I Learned

- **Streaming architecture fundamentals** — topics, partitions, consumer groups, offsets, and why message brokers decouple producers from consumers
- **Docker multi-service orchestration** — networking, volumes, layer caching, and the `PYTHONUNBUFFERED` gotcha
- **dbt transformation layers** — staging (clean) → intermediate (enrich) → mart (serve), with `ref()` building automatic dependency graphs
- **Airflow DAG construction** — scheduling, retries, failure callbacks, and the critical difference between `catchup=True` and `catchup=False`
- **Production patterns** — poison pill handling, dead letter queue concepts, retry logic, idempotent table creation, and defensive serialization/deserialization
- **Data quality awareness** — freshness checks as DAG gates, null filtering in staging, type casting for clean downstream models

---

## 📈 Future Improvements

- [ ] Add Great Expectations quality gates between dbt layers
- [ ] Implement dead letter queue for failed messages
- [ ] Add Slack/email alerting on Airflow DAG failures
- [ ] Deploy to AWS (S3 + RDS + ECS) using MinIO → S3 migration
- [ ] Add CI/CD with GitHub Actions (lint → test → build → push images)
- [ ] Write pytest unit tests for producer/consumer transformation logic

---

## 👤 Author

**Kelash Kumar**
BS Computer Science · Sukkur IBA University · Class of 2026

[![GitHub](https://img.shields.io/badge/GitHub-kelash-181717?style=flat&logo=github)](https://github.com/kelashkumar-iba)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-kelash-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/kelashkumar-iba)

---

*"The compound effect of daily discipline is indistinguishable from talent."*
