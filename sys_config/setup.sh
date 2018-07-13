#!/bin/bash

# run with sudo - make sure to set sean/ubuntu in all files

# install needed ubuntu packages
apt-get install nginx supervisor

# install conda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# install conda env
conda env create -f ../env_ss.yml

# move supervisor file to conf.d folder
cp school_schedule.conf /etc/supervisor/conf.d/

# make sure supervisor comes up after reboot
systemctl enable supervisor

# make sure supervisor starts now
systemctl start supervisor

# have supervisor reread the conf files and restart apps with changed confs
supervisorctl reread
supervisorctl update

# move nginx to sites-available
cp school_schedule /etc/nginx/sites-available/

# make link to sites enabled
ln -s /etc/nginx/sites-available/school_schedule /etc/nginx/sites-enabled/school_schedule

# reset nginx
service nginx restart
