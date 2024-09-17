cd ~
source ./portfolio_venv/bin/activate
DAGSTER_HOME=~/Portfolio/src/portfolio dagster-webserver -h 0.0.0.0 -p 3000 -w ~/Portfolio/src/portfolio/workspace.yaml