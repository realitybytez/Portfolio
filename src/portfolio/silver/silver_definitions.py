from pathlib import Path
from dagster import AssetExecutionContext, Definitions
from dagster_dbt import (
    DbtCliResource,
    DbtProject,
    dbt_assets,
)
import os
import json

dbt_silver = DbtProject (
    project_dir= Path(__file__).joinpath("..").resolve(),
    target='dev'
)

@dbt_assets(manifest=dbt_silver.manifest_path)
def silver_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    # seems like only way to get secret into dbt process when invoked from dagster... works fine from CLI just not
    # when dagster kicks it off.... come back at later date to revise as this is not ideal.
    # hard coded values are read from dbt profiles file just fine...
    dbt_vars = {"DBT_PASSWORD": os.getenv('DBT_PASSWORD')}
    yield from dbt.cli(["build","--vars", json.dumps(dbt_vars)], context=context).stream()


defs = Definitions(
    assets=[silver_assets],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_silver),
    },
)

x=0
