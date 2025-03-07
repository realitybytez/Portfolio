from pathlib import Path
from dagster import AssetKey, asset_sensor, SensorEvaluationContext, define_asset_job, EventLogEntry, RunRequest, asset, Definitions, DefaultSensorStatus, AssetExecutionContext, PipesSubprocessClient, MaterializeResult
import os
import json
import subprocess

bronze_to_silver = define_asset_job(name='adls2_to_silver', selection='silver')

@asset
def silver(context: AssetExecutionContext, pipes_subprocess_client: PipesSubprocessClient):
    cmd = ["dbt", "build", "--project-dir", Path(__file__, "..").resolve(), "--profiles-dir", Path(__file__, "..").resolve(),
         '--target', 'dev']
    return pipes_subprocess_client.run(
        command=cmd, context=context
    ).get_materialize_result()

@asset_sensor(asset_key=AssetKey('policy_forge_delta_to_bronze'), job=bronze_to_silver, default_status=DefaultSensorStatus.RUNNING)
def detect_bronze_update(context: SensorEvaluationContext, asset_event: EventLogEntry):
    assert asset_event.dagster_event and asset_event.dagster_event.asset_key
    yield RunRequest(run_key=context.cursor)

defs = Definitions(
    assets=[silver],
    resources={"pipes_subprocess_client": PipesSubprocessClient()},
    jobs = [bronze_to_silver,],
    sensors = [detect_bronze_update],
)

