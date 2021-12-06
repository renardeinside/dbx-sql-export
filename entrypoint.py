import logging
import pathlib

import click
import pandas as pd
import datetime as dt
from dataclasses import dataclass
import pyodbc
from logging import Logger
import os


@dataclass
class EndpointInfo:
    host: str
    token: str
    http_path: str
    driver_path: str


class DataProvider:
    """
    Base class for providing access to the data
    """

    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        endpoint_info = self._get_endpoint_info()
        self.connection = pyodbc.connect(
            self.get_connection_string(endpoint_info), autocommit=True
        )

    @staticmethod
    def _get_endpoint_info() -> EndpointInfo:
        """
        This function collects all the nessesary bits of information to connect to the endpoint
        """
        for var in ["DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_TOKEN", "DATABRICKS_HTTP_PATH"]:
            if var not in os.environ:
                raise Exception(f"Environment variable {var} is not defined")

        _host = os.environ["DATABRICKS_SERVER_HOSTNAME"]
        _token = os.environ["DATABRICKS_TOKEN"]
        _http_path = os.environ["DATABRICKS_HTTP_PATH"]
        _driver_path = os.environ.get(
            "SIMBA_DRIVER_PATH", "/opt/simba/spark/lib/64/libsparkodbc_sb64.so"
        )  # default location on Debian
        return EndpointInfo(_host, _token, _http_path, _driver_path)

    @staticmethod
    def get_connection_string(endpoint_info: EndpointInfo) -> str:
        """
        This function builds the connection string as per Simba ODBC driver documentation
        """
        connection_string = "".join(
            [
                f"DRIVER={endpoint_info.driver_path}",
                f";Host={endpoint_info.host}",
                ";PORT=443",
                f";HTTPPath={endpoint_info.http_path}",
                ";AuthMech=3",
                ";Schema=default",
                ";SSL=1",
                ";ThriftTransport=2",
                ";SparkServerType=3",
                ";UID=token",
                f";PWD={endpoint_info.token}",
                ";RowsFetchedPerBlock=1000000",
                # Please note that the default value is 10k, we increase it to 100k for faster fetches
            ]
        )
        return connection_string

    def get_data(self, query: str) -> pd.DataFrame:
        data = pd.read_sql(query, self.connection)
        return data


@click.command(name="export")
@click.option(
    "--database",
    required=True,
    type=str,
    help="""Database name"""
)
@click.option(
    "--table",
    required=True,
    type=str,
    help="""Table name"""
)
@click.option(
    "--output-file",
    required=True,
    type=str,
    help="""Output file"""
)
def export(database: str, table: str, output_file: str):
    click.echo(f"Starting export of the table {database}.{table}")

    load_start_dttm = dt.datetime.now()
    provider = DataProvider(logging.getLogger("dbx-sql-cli"))
    data: pd.DataFrame = provider.get_data(f"select * from {database}.{table}") # noqa
    load_end_dttm = dt.datetime.now()

    load_duration: dt.timedelta = load_end_dttm - load_start_dttm

    file_path = pathlib.Path(output_file)

    if file_path.exists():
        file_path.unlink()

    write_start_dttm = dt.datetime.now()
    data.to_parquet(str(file_path), engine="pyarrow")
    write_end_dttm = dt.datetime.now()

    write_duration: dt.timedelta = write_end_dttm - write_start_dttm

    total_size_in_bytes = pathlib.Path(".data").stat().st_size
    total_size_in_gb = total_size_in_bytes * 0.000001

    click.echo(f"Export of the table {database}.{table} finished successfully")
    click.echo(f"""Export statistics:
    
        Loading duration in seconds: {load_duration.total_seconds()}
        Write duration in seconds:   {write_duration.total_seconds()}
        Total dataset size in Mbs:   {total_size_in_gb}
        
        Throughput: {total_size_in_gb / load_duration.total_seconds()} (Mbs per second)
    """)


if __name__ == "__main__":
    export()
