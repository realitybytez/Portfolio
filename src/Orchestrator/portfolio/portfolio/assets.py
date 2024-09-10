from dagster import asset

@asset
def fetch_the_world():
    return 'hello world'

@asset
def read_the_world(fetch_the_world):
    return fetch_the_world