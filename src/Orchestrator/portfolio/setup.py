from setuptools import find_packages, setup

setup(
    name="portfolio",
    packages=find_packages(exclude=["portfolio_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
