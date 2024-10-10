#!/bin/bash

HOME_DIR=/home/vagrant
KEA_DIR=/etc/kea
NGINX_DIR_BASE=/etc/nginx
NGINX_DIR=$NGINX_DIR_BASE/conf.d
PROVISION_DIR=/var/www/html/ztd

# Upgrade and install some utilites
export DEBIAN_FRONTEND=noninteractive
apt-get update # && apt-get upgrade -y
apt-get install bash-completion vim python3.11-venv -y

# Install Kea and nginx. Remove default configs
curl -1sLf \
'https://dl.cloudsmith.io/public/isc/kea-2-6/setup.deb.sh' \
| bash
apt-get update && apt-get install isc-kea-dhcp4 nginx -y
rm $KEA_DIR/* ; rm $NGINX_DIR_BASE/sites-enabled/*

# Generate DHCP config and provisioning script for each switch
cp -r /vagrant/ztd $HOME_DIR && cd $HOME_DIR/ztd
python3 -m venv venv
venv/bin/pip install flask gunicorn netmiko
chown -R vagrant:vagrant $HOME_DIR/ztd
cd create_scripts
su vagrant -c '../venv/bin/python create_scripts.py'

# Move or copy configs and scripts to respective directories
mv *.conf $KEA_DIR
chown _kea:_kea $KEA_DIR/*
chmod 640 $KEA_DIR/*

cp /vagrant/config_server/nginx-http.conf $NGINX_DIR
mkdir -p $PROVISION_DIR && mv *.sh $_
cp /vagrant/config_dell/* $PROVISION_DIR
cp /vagrant/firmware/*.bin $PROVISION_DIR
chown -R www-data:www-data $PROVISION_DIR
chmod 755 $PROVISION_DIR
chmod 644 $PROVISION_DIR/*

cp /vagrant/config_server/ztd.service /etc/systemd/system

# Restart Kea and nginx
systemctl enable isc-kea-dhcp4-server ; systemctl restart isc-kea-dhcp4-server
systemctl enable nginx ; systemctl restart nginx

# Start ZTD service
systemctl enable ztd ; systemctl start ztd