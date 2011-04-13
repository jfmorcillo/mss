#!/bin/bash

[ ! -f bootstrap.sh ] && echo "You are not in the directory where the script lives" && exit 1

for package in `cat requirements/apps.txt`
do
    urpmi --auto $package
done

sh manage.sh todev
mkdir -p /var/log/mss/
mkdir -p /var/lib/mss/
touch /var/log/mss/mss-agent.log
ln -s `pwd`/mss /usr/lib/python2.5/site-packages/mss
python mss/www/manage.py syncdb --noinput
python mss/agent/setup_mss.py
sh build_mo.sh
