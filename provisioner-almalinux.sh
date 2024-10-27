#!/bin/bash

HOME_DIR=/home/vagrant
KEA_DIR=/etc/kea
NGINX_DIR_BASE=/etc/nginx
NGINX_DIR=$NGINX_DIR_BASE/conf.d
PROVISION_DIR=/var/www/html/ztd

# Upgrade and install some utilites
# dnf upgrade -y
dnf install bash-completion vim python3.11 policycoreutils-python-utils -y

# Install Kea and nginx. Remove default configs
dnf config-manager --set-enabled powertools 
dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y
curl -1sLf \
  'https://dl.cloudsmith.io/public/isc/kea-2-6/setup.rpm.sh' \
  | bash
dnf install isc-kea-dhcp4 nginx -y
rm $KEA_DIR/*

# Generate DHCP config and provisioning script for each switch
cp -r /vagrant/ztd $HOME_DIR && cd $HOME_DIR/ztd
python3 -m venv venv
venv/bin/pip install flask gunicorn netmiko python-dotenv
echo "IP_BASE=$1" > create_scripts/.env
chown -R vagrant:vagrant $HOME_DIR/ztd
cd create_scripts
su vagrant -c '../venv/bin/python create_scripts.py'

# Move or copy configs and scripts to respective directories
mv *.conf $KEA_DIR
chown kea:kea $KEA_DIR/*
chmod 640 $KEA_DIR/*

cp /vagrant/config_server/nginx-http.conf $NGINX_DIR
sed -in '/^ \+server {/,/# Settings/{/# Settings/!d}' $NGINX_DIR_BASE/nginx.conf
mkdir -p $PROVISION_DIR && mv *.sh $_
cp /vagrant/config_dell/* $PROVISION_DIR
cp /vagrant/firmware/*.bin $PROVISION_DIR
chown -R nginx:nginx $PROVISION_DIR
chmod 755 $PROVISION_DIR
chmod 644 $PROVISION_DIR/*

cp /vagrant/config_server/ztd.service /etc/systemd/system

# SELinux 
cd /tmp
cp /vagrant/config_server/selinux-ztd.te .
checkmodule -M -m -o selinux-ztd.mod selinux-ztd.te
semodule_package -o selinux-ztd.pp -m selinux-ztd.mod
semodule -i selinux-ztd.pp
rm -f selinux-ztd*
setsebool -P httpd_can_network_connect 1
restorecon -Rv $KEA_DIR
restorecon -Rv $NGINX_DIR
restorecon -Rv $PROVISION_DIR

# Restart Kea and nginx
systemctl enable kea-dhcp4 ; systemctl restart kea-dhcp4
systemctl enable nginx ; systemctl restart nginx

# Start ZTD service
systemctl enable ztd ; systemctl start ztd