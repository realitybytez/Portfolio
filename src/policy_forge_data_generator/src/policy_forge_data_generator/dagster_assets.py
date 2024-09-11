from dagster import asset
from policy_forge_data_generator.generate_policy_forge import generate_data


@asset
def policy_forge_replica_data():
    generate_data()

