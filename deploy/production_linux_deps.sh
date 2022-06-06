#!/bin/bash

apt update
apt upgrade -y
apt install python3 python3-pip python3-virtualenv virtualenv gcc make uwsgi uwsgi-plugin-python3 gdal-bin python3-gdal python3-dev build-essential nginx libproj-dev proj-bin munin munin-node -y

# 22.04 Jammy
apt install postgresql-14 postgresql-contrib postgresql-server-dev-14 postgis postgresql-14-postgis-3 -y