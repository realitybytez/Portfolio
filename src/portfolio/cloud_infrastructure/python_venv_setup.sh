#!/bin/bash
# Setup environment
os_password="$HOME/Portfolio/src/portfolio/local_secrets/portfolio_os_user_secret.txt"
cd ~
sudo -S apt install -y python3.12-venv <$os_password
sudo -S apt install -y python3-pip <$os_password
python3 -m venv portfolio_venv
source ./portfolio_venv/bin/activate
python3 -m pip install --upgrade setuptools wheel pip
pip install -r "$HOME/Portfolio/src/portfolio/requirements.txt"
deactivate
