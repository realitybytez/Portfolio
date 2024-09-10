# Pull project source down
cd ~
git clone git@github.com:realitybytez/Portfolio.git

# Setup environment for orchestrator (Dagster)
cd /Portfolio/src/Orchestrator
python3 -m venv orchestration
source orchestration/bin/activate
pip install -r requirements.txt

# Create orchestration project & install in editable mode
cd portfolio
pip install -e ".[dev]"

# Run daemon & web server
python3 -m dagster dev

#deactivate