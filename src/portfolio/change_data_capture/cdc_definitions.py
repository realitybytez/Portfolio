from dagster import AssetKey, asset_sensor, SensorEvaluationContext, define_asset_job, EventLogEntry, RunRequest, asset, Definitions, DefaultSensorStatus
from fetch_delta import get_delta

policy_forge_delta_to_bronze_job = define_asset_job(name='policy_forge_delta_to_bronze_job', selection='policy_forge_delta_to_bronze')

@asset
def policy_forge_delta_to_bronze():
    get_delta()

@asset_sensor(asset_key=AssetKey('policy_forge_replica_data_upload'), job=policy_forge_delta_to_bronze_job, default_status=DefaultSensorStatus.RUNNING)
def detect_new_policy_forge_insert(context: SensorEvaluationContext, asset_event: EventLogEntry):
    assert asset_event.dagster_event and asset_event.dagster_event.asset_key
    yield RunRequest(run_key=context.cursor)

defs = Definitions(
    assets=[policy_forge_delta_to_bronze,],
    jobs=[policy_forge_delta_to_bronze_job,],
    sensors=[detect_new_policy_forge_insert,]
)