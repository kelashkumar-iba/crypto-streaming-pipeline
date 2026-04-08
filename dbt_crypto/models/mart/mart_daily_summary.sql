SELECT
    coin,
    DATE(ingested_at) AS trade_date,
    COUNT(*) AS num_readings,
    AVG(price_usd) AS avg_price,
    MIN(price_usd) AS low_price,
    MAX(price_usd) AS high_price,
    MAX(price_usd) - MIN(price_usd) AS daily_spread,
    AVG(change_24h) AS avg_24h_change
FROM {{ ref('int_crypto_metrics') }}
GROUP BY coin, DATE(ingested_at)
ORDER BY trade_date DESC, coin
