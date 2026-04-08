SELECT
    coin,
    price_usd,
    change_24h,
    last_updated_at,
    ingested_at,
    LAG(price_usd) OVER (PARTITION BY coin ORDER BY ingested_at) AS prev_price,
    price_usd - LAG(price_usd) OVER (PARTITION BY coin ORDER BY ingested_at) AS price_change,
    AVG(price_usd) OVER (
        PARTITION BY coin
        ORDER BY ingested_at
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS moving_avg_5
FROM {{ ref('stg_crypto_prices') }}
