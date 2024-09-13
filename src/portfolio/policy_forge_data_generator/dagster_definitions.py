from dagster import AssetKey, asset_sensor, define_asset_job, ScheduleDefinition, EventLogEntry, RunConfig, RunRequest

policy_forge_data_job = define_asset_job(name='generate_policy_forge_replica_data', selection='policy_forge_replica_data')
policy_forge_upload_job = define_asset_job(name='upload_policy_forge_replica_data', selection='policy_forge_replica_data_upload')
policy_forge_data_schedule = ScheduleDefinition(cron_schedule='0 0 * * *', job=policy_forge_data_job)


@asset_sensor(asset_key=AssetKey('policy_forge_replica_data'), job=policy_forge_upload_job)
def detect_new_policy_forge_data():
    yield RunRequest(
        run_config=RunConfig(
            ops={
                "read_materialization": ReadMaterializationConfig(
                    asset_key=list(asset_event.dagster_event.asset_key.path)
                )
            }
        ),
    )
