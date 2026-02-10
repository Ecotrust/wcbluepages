#!/bin/bash

cd /usr/local/apps/
python3 -m pip install --user virtualenv
virtualenv env --python=python3.12
source /usr/local/apps/env/bin/activate

pip install -r /usr/local/apps/wcbluepages/requirements.txt