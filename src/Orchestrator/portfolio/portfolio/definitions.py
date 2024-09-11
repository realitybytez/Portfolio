from dagster import Definitions, load_assets_from_modules, define_asset_job, ScheduleDefinition
from portfolio import assets
from policy_forge_data_generator import dagster_assets as oltp_assets
from policy_forge_data_generator import dagster_definitions as oltp_definitions
all_assets = load_assets_from_modules([assets, oltp_assets])

world_job = define_asset_job(name='world_job', selection='*')
schedule = ScheduleDefinition(cron_schedule='*/1 * * * *', job=world_job)

defs = Definitions(
    assets=all_assets,
    schedules=[schedule, oltp_definitions.policy_forge_data_schedule]
)



