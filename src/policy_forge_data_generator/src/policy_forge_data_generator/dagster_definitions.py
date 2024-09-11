from dagster import asset
from policy_forge_data_generator.dagster_assets import policy_forge_replica_data
from dagster import define_asset_job, ScheduleDefinition


policy_forge_data_job = define_asset_job(name='generate_policy_forge_replica_data', selection='*')
policy_forge_data_schedule = ScheduleDefinition(cron_schedule='0 0 * * *', job=policy_forge_data_job)
