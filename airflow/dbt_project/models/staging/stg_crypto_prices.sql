SELECT
    id,
    coin,
    price_usd,
    change_24h,
    TO_TIMESTAMP(last_updated) AS last_updated_at,
    ingested_at
FROM raw_crypto_prices
WHERE coin IS NOT NULL
  AND price_usd IS NOT NULL
