import json
import os
import time
import requests
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC_NAME = os.environ.get('TOPIC_NAME', 'crypto-prices')

COINS = 'bitcoin,ethereum,solana,cardano,polkadot,chainlink,avalanche-2,polygon-ecosystem-token,dogecoin,shiba-inu'
API_URL = 'https://api.coingecko.com/api/v3/simple/price'


def create_producer():
    for attempt in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Connected to Redpanda.")
            return producer
        except Exception as e:
            print(f"Attempt {attempt+1}/10 - Redpanda not ready: {e}")
            time.sleep(5)
    raise ConnectionError("Could not connect to Redpanda after 10 attempts.")


def fetch_prices():
    params = {
        'ids': COINS,
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_last_updated_at': 'true'
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()


def main():
    producer = create_producer()

    while True:
        try:
            data = fetch_prices()
            for coin, values in data.items():
                message = {
                    'coin': coin,
                    'price_usd': values.get('usd'),
                    'change_24h': values.get('usd_24h_change'),
                    'last_updated': values.get('last_updated_at'),
                }
                producer.send(TOPIC_NAME, value=message)
                print(f"Sent: {message}")

            producer.flush()
            time.sleep(60)

        except requests.RequestException as e:
            print(f"API error: {e}. Retrying in 30s...")
            time.sleep(30)
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 10s...")
            time.sleep(10)


if __name__ == '__main__':
    main()
