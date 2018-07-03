#!/bin/bash

# run with sudo - make sure to set sean/ubuntu in all files

# install needed ubuntu packages
apt-get install nginx supervisor

# move supervisor file to conf.d folder and update supervisor
cp school_schedule.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update

# move nginx to sites-available
cp school_schedule /etc/nginx/sites-available/

# make link to sites enabled
ln -s /etc/nginx/sites-available/school_schedule /etc/nginx/sites-enabled/school_schedule

# reset nginx
service nginx restart
