from dagster import asset
from policy_forge_data_generator.generate_policy_forge import generate_data
import subprocess
from pkg_resources import resource_filename


@asset
def policy_forge_replica_data():
    generate_data()


@asset
def policy_forge_replica_data_upload():
    script_path = resource_filename(__name__, 'upload_policy_forge_data.sh')
    dml_script_path = resource_filename(__name__, 'PolicyForgeDML.sql')
    subprocess.run([script_path, dml_script_path])
