FROM ghcr.io/dbt-labs/dbt-postgres:1.7.4
WORKDIR /usr/app
COPY dbt_project.yml .
COPY profiles.yml .
COPY models/ models/
ENTRYPOINT ["dbt"]
CMD ["run", "--profiles-dir", "."]
