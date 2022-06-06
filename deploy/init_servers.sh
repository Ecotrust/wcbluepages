#!/bin/bash
PROJ_DIR=/usr/local/apps/wcbluepages
APPS_DIR=$PROJ_DIR/bluepages
DEPLOY_DIR=$PROJ_DIR/deploy

sudo cp $DEPLOY_DIR/bluepages_nginx.conf /etc/nginx/sites-available/bluepages
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/bluepages /etc/nginx/sites-enabled/bluepages

sudo cp $DEPLOY_DIR/uwsgi/uwsgi.service /etc/systemd/system/
sudo cp $DEPLOY_DIR/uwsgi/bluepages.ini /etc/uwsgi/apps-enabled/
sudo service uwsgi start
sudo service uwsgi restart
sudo systemctl enable uwsgi

sudo service nginx restart