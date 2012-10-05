#!/bin/bash

[ ! -f bootstrap.sh ] && echo "You are not in the directory where the script lives" && exit 1

path=`pwd`
echo "What is your username ?"
read user

id $user > /dev/null 2>&1
[ $? -ne 0 ] && echo "User doesn't exists" && exit 1 

for package in `cat requirements/apps.txt`
do
    urpmi --auto $package
done

sh manage.sh todev
mkdir -p /var/log/mss/
mkdir -p /var/lib/mss/
touch /var/log/mss/mss-agent.log
rm -f /usr/lib/python2.7/site-packages/mss
ln -s ${path}/mss /usr/lib/python2.7/site-packages/mss
python mss/www/manage.py syncdb --noinput
chown $user.$user /var/lib/mss/
chown $user.$user /var/lib/mss/mss-www.db
python mss/agent/setup_mss.py
su -c 'sh build_mo.sh' $user
