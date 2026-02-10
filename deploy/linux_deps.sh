#!/bin/bash

apt update
apt upgrade -y
apt install python3.12 python3.12-dev python3.12-venv python3-pip python3-virtualenv virtualenv gcc make uwsgi uwsgi-plugin-python3 gdal-bin python3-gdal build-essential nginx libproj-dev proj-bin -y

# 20.04 Focal
# apt install postgresql-12 postgresql-contrib postgresql-server-dev-12 postgis postgresql-12-postgis-3 -y

# 22.04 Jammy
# apt install postgresql-14 postgresql-contrib postgresql-server-dev-14 postgis postgresql-14-postgis-3 -y

# 24.04 Noble
apt install postgresql-16 postgresql-contrib postgresql-server-dev-16 postgis postgresql-16-postgis-3 -y

curl -sL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install nodejs -y