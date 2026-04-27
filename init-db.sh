#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER metabase_user WITH PASSWORD 'metabase_pass';
    CREATE DATABASE metabase_db OWNER metabase_user;
    GRANT ALL PRIVILEGES ON DATABASE metabase_db TO metabase_user;
EOSQL
