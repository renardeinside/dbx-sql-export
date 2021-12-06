# Quick example on using Databricks ODBC driver from Python

## Pre-requisites:
- Docker
- make

## How-to
- provide the following variables in `.env`:
```
DATABRICKS_TOKEN=dapi...
DATABRICKS_SERVER_HOSTNAME=...
DATABRICKS_HTTP_PATH=...
```

- build:
```
make build
```
launch:
```
make launch
```