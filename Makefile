ifneq (,$(wildcard ./.env))
    include .env
    export
endif

build:
	docker build --progress=plain -t dbx-sql-cli .

launch:
	docker run \
		-e DATABRICKS_SERVER_HOSTNAME \
		-e DATABRICKS_TOKEN \
		-e DATABRICKS_HTTP_PATH \
		dbx-sql-cli \
		entrypoint.py --database=default --table=iot_stream --output-file=.data