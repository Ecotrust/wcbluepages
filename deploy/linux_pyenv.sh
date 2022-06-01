#!/bin/bash

cd /usr/local/apps/wcbluepages/
python3 -m pip install --user virtualenv
virtualenv env --python=python3
source /usr/local/apps/wcbluepages/env/bin/activate

pip install -r /usr/local/apps/wcbluepages/requirements.txt