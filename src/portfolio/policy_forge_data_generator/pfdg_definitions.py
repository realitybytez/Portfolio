from dagster import AssetKey, asset_sensor, SensorEvaluationContext, define_asset_job, ScheduleDefinition, EventLogEntry, RunConfig, RunRequest, asset, Definitions
from generate_policy_forge import generate_data
import subprocess

policy_forge_data_job = define_asset_job(name='generate_policy_forge_replica_data', selection='policy_forge_replica_data')
policy_forge_data_schedule = ScheduleDefinition(cron_schedule='0 0 * * *', job=policy_forge_data_job)

policy_forge_upload_job = define_asset_job(name='upload_policy_forge_replica_data', selection='policy_forge_replica_data_upload')

@asset
def policy_forge_replica_data():
    generate_data()

@asset
def policy_forge_replica_data_upload():
    script_path = 'Portfolio/src/portfolio/policy_forge_data_generator/upload_policy_forge_data.sh'
    dml_script_path = 'Portfolio/src/portfolio/policy_forge_data_generator/PolicyForgeDML.sql'
    subprocess.run([script_path, dml_script_path])

@asset_sensor(asset_key=AssetKey('policy_forge_replica_data'), job=policy_forge_upload_job)
def detect_new_policy_forge_data(context: SensorEvaluationContext, asset_event: EventLogEntry):
    assert asset_event.dagster_event and asset_event.dagster_event.asset_key
    yield RunRequest(run_key=context.cursor)

defs = Definitions(
    assets=[policy_forge_replica_data, policy_forge_replica_data_upload],
    schedules=[policy_forge_data_schedule],
    jobs=[policy_forge_upload_job,],
    sensors=[detect_new_policy_forge_data,]
)
