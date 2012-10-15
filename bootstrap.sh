#!/bin/bash

link=/usr/lib/python2.7/site-packages/mss
agent=/usr/sbin/mss-agent
path=`pwd`

[ ! -f $0 ] && echo "You are not in the directory where the script lives" && exit 1

[ -d $link ] && echo "MSS package installed ? $link is a directory." && exit 1

echo "What is your username ? (used to run the webserver)"
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
[ -f $link ] && rm -f $link
ln -s ${path}/mss $link
[ -f $agent ] && rm -f $agent
ln -s ${path}/bin/agent/mss-agent.py $agent
python mss/www/manage.py syncdb --noinput
chown $user.$user /var/lib/mss/
chown $user.$user /var/lib/mss/mss-www.db
python mss/agent/setup_mss.py
su -c 'sh build_mo.sh' $user
