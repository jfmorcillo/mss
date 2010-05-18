#!/bin/sh

config=".my.cnf.$$"
command=".mysql.$$"

rootpwd=$1
auditpwd=$2

prepare() {
    touch $config $command
    chmod 600 $config $command
}

do_query() {
    echo "$1" >$command
    #sed 's,^,> ,' < $command  # Debugging
    mysql --defaults-file=$config <$command
    return $?
}

# This simple escape works correctly in both places.
basic_single_escape () {
    # The quoting on this sed command is a bit complex.  Single-quoted strings
    # don't allow *any* escape mechanism, so they cannot contain a single
    # quote.  The string sed gets (as argv[1]) is:  s/\(['\]\)/\\\1/g
    #
    # Inside a character class, \ and ' are not special, so the ['\] character
    # class is balanced and contains two characters.
    echo "$1" | sed 's/\(['"'"'\]\)/\\\1/g'
}

make_config() {
    echo "# mysql_secure_installation config file" >$config
    echo "[mysql]" >>$config
    echo "user=root" >>$config
    esc_pass=`basic_single_escape "$rootpass"`
    echo "password='$esc_pass'" >>$config
    #sed 's,^,> ,' < $config  # Debugging
}

get_root_password() {
	rootpass=$1
	make_config
	do_query ""
    return $?
}

cleanup() {
    echo "Cleaning up..."
    rm -f $config $command
}

# mysql setup

prepare
get_root_password $rootpwd
if [ $? -ne 0 ]; then
    echo "2The current Mysql password is not valid."
    cleanup
    exit 1
fi
echo "Create audit database"
do_query "DROP DATABASE audit;"
do_query "CREATE DATABASE audit;"
echo "Grant privileges on database"
do_query "GRANT ALL PRIVILEGES ON audit.* TO 'audit'@'localhost' IDENTIFIED BY '$auditpwd' WITH GRANT OPTION; FLUSH PRIVILEGES;"
cleanup

# audit tables setup
audittpl="templates/base-audit.ini.tpl"

grep -q "\[audit\]" /etc/mmc/plugins/base.ini
if [ $? -ne 0 ]; then
    # first audit install
    cat $audittpl >> /etc/mmc/plugins/base.ini
    sed -i "s/\@AUDITPASSWORD\@/${auditpwd}/" /etc/mmc/plugins/base.ini
else
    # audit reconfigure
    sed -i "s/^\(dbpassword[[:space:]]\+=[[:space:]]\+\).*$/\1${auditpwd}/" /etc/mmc/plugins/base.ini
fi

mmc-helper audit init

/sbin/service mmc-agent restart > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "0Service MMC started succesfully."
else echo "1Service MMC fails starting. Check /var/log/mmc/mmc-agent.log"; exit 1
fi

sleep 1
exit 0
