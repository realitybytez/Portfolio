cd ~
source ./portfolio_venv/bin/activate
DAGSTER_HOME=~/Portfolio/src/portfolio dagster-daemon run -w ~/Portfolio/src/portfolio/workspace.yaml