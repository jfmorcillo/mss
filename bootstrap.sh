#!/bin/bash

link=/usr/lib/python2.7/site-packages/mss
agent=/usr/sbin/mss-agent
www=/usr/bin/mss-www
path=`pwd`

[ ! -f $0 ] && echo "You are not in the directory where the script lives" && exit 1

[ ! -h $link ] && [ -x $link ] && echo "MSS package installed ? $link is not a link." && exit 1

echo "What is your username ? (used to run the webserver)"
read user

id $user > /dev/null 2>&1
[ $? -ne 0 ] && echo "User doesn't exists" && exit 1 

for package in `cat requirements/apps.txt`
do
    urpmi --auto $package
done

function generate_salt() {
	salt=</dev/urandom tr -dc A-Za-z0-9 | head -c 50
	echo $salt
}

mkdir -p /var/log/mss/
mkdir -p /var/lib/mss/
touch /var/log/mss/mss-agent.log
if [ ! -f ${path}/mss/www/settings.py ]; then
    echo Creating settings.py file....
    cp ${path}/mss/www/settings.py.example ${path}/mss/www/settings.py
    chown $user.$user ${path}/mss/www/settings.py
    salt=`generate_salt`
    sed -i "s!^SECRET_KEY.*!SECRET_KEY = \"${salt}\"!" ${path}/mss/www/settings.py
fi
sh manage.sh todev
[ -h $link ] && rm -f $link
ln -s ${path}/mss $link
[ -f $agent ] && rm -f $agent
ln -s ${path}/bin/agent/mss-agent.py $agent
[ -f $www ] && rm -f $www
ln -s ${path}/bin/www/mss-www.sh $www
python mss/www/manage.py syncdb --noinput
chown $user.$user /var/lib/mss/
chown $user.$user /var/lib/mss/mss-www.db
python mss/agent/setup_mss.py
su -c 'sh build_mo.sh' $user

