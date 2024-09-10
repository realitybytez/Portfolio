from dagster import Definitions, load_assets_from_modules, define_asset_job, ScheduleDefinition
import portfolio.assets
all_assets = load_assets_from_modules([portfolio.assets])

world_job = define_asset_job(name='world_job', selection='*')
schedule = ScheduleDefinition(cron_schedule='*/1 * * * *', job=world_job)

defs = Definitions(
    assets=all_assets,
    schedules=[schedule,]
)

