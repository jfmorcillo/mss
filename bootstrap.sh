#!/bin/bash

link=/usr/lib/python2.7/site-packages/mss
agent=/usr/sbin/mss-agent
www=/usr/bin/mss-www
mss_shorewall_rules=/usr/sbin/mss-add-shorewall-rule
path=`pwd`

[ ! -f $0 ] && echo "You are not in the directory where the script lives" && exit 1

[ ! -h $link ] && [ -x $link ] && echo "MSS package installed ? $link is not a link." && exit 1

echo "What is your username ? (used to run the webserver)"
read user

id $user > /dev/null 2>&1
[ $? -ne 0 ] && echo "User doesn't exists" && exit 1

if [ ! -f requirements/no_dep ]
then
    for package in `cat requirements/apps.txt`
    do
        urpmi --auto $package
    done
    touch requirements/no_dep
else
    echo skipping dependencies, remove requirements/no_dep to enable dependency checking
fi

function generate_salt() {
	salt=</dev/urandom tr -dc A-Za-z0-9 | head -c 50
	echo $salt
}

sh manage.sh todev
mkdir -p /var/lib/mss/cache
mkdir -p /etc/mss
touch /var/log/mss/mss-agent.log
touch /var/log/mss/mss-www.log
chown $user.$user /var/log/mss/mss-www.log
if [ ! -f ${path}/mss/www/local_settings.py ]; then
    echo Creating local_settings.py file....
    cp ${path}/mss/www/local_settings.py.example ${path}/mss/www/local_settings.py
    chown $user.$user ${path}/mss/www/local_settings.py
    salt=`generate_salt`
    sed -i "s!^SECRET_KEY.*!SECRET_KEY = \"${salt}\"!" ${path}/mss/www/local_settings.py
fi
[ -h $link ] && rm -f $link
ln -s ${path}/mss $link
[ -f $agent ] && rm -f $agent
ln -s ${path}/bin/agent/mss-agent.py $agent
[ -f $www ] && rm -f $www
ln -s ${path}/bin/www/mss-www.sh $www
[ -f $mss_shorewall_rules ] && rm -f $mss_shorewall_rules
ln -s ${path}/bin/mss-add-shorewall-rule $mss_shorewall_rules
python mss/www/manage.py syncdb --noinput
chown $user.$user /var/lib/mss/
chown $user.$user /var/lib/mss/mss-www.db
[ -h /etc/mss/agent.ini ] && rm -f /etc/mss/agent.ini
ln -s ${path}/etc/agent.ini /etc/mss/agent.ini
[ -h /var/lib/mss/local ] && rm -f /var/lib/mss/local
ln -s ${path}/modules /var/lib/mss/local
su -c 'sh build_mo.sh' $user
