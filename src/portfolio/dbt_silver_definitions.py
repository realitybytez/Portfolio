from pathlib import Path

from dagster import AssetExecutionContext, Definitions
from dagster_dbt import (
    DbtCliResource,
    DbtProject,
    build_schedule_from_dbt_selection,
    dbt_assets,
)

dbt_silver = DbtProject (
project_dir= "Portfolio/src/portfolio/dbt_silver",
target='prod'
)

@dbt_assets(manifest=dbt_silver.manifest_path)
def silver_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


defs = Definitions(
    assets=[silver_assets],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_silver),
    },
)
