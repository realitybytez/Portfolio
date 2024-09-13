cd ~

# Setup environment
python3 -m venv portfolio_venv
cd portfolio_venv
sudo -S apt install -y python3-pip <~/password.txt # todo secure later
sudo -S python3 -m pip install --upgrade setuptools wheel pip <~/password.txt
source portfolio_venv/bin/activate
pip install -r requirements.txt
deactivate

# Fetch codebase
git clone git@github.com:realitybytez/Portfolio.git
