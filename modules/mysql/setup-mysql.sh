#!/bin/sh

# Copyright (C) 2002 MySQL AB and Jeremy Cole
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

. ../functions.sh

config="/root/.my.cnf"
command=".mysql.$$"

trap "interrupt" 2

rootpass=""
echo_n=
echo_c=

set_echo_compat() {
    case `echo "testing\c"`,`echo -n testing` in
	*c*,-n*) echo_n=   echo_c=     ;;
	*c*,*)   echo_n=-n echo_c=     ;;
	*)       echo_n=   echo_c='\c' ;;
    esac
}

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

# Simple escape mechanism (\-escape any ' and \), suitable for two contexts:
# - single-quoted SQL strings
# - single-quoted option values on the right hand side of = in my.cnf
#
# These two contexts don't handle escapes identically.  SQL strings allow
# quoting any character (\C => C, for any C), but my.cnf parsing allows
# quoting only \, ' or ".  For example, password='a\b' quotes a 3-character
# string in my.cnf, but a 2-character string in SQL.
#
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
    esc_pass=`basic_single_escape "$1"`
    echo "password='$esc_pass'" >>$config
    #sed 's,^,> ,' < $config  # Debugging
    chmod go-rwx $config
}

get_root_password() {
	rootpass=$1
	make_config
	do_query ""
    if [ $? -eq 0 ]; then
        echo "OK, successfully used password, moving on..."
    else
        echo "1Invalid current Mysql password."
        interrupt
    fi
}

set_root_password() {

    echo "Setting the root password ensures that nobody can log into the MySQL"
    echo "root user without the proper authorisation."
    esc_pass=`basic_single_escape "$1"`
    #do_query "UPDATE mysql.user SET Password=PASSWORD('$esc_pass') WHERE User='root';"
    mysqladmin password "$1"
    if [ $? -eq 0 ]; then
        echo "Password updated successfully!"
        echo "Reloading privilege tables.."
        make_config "$1"
        #reload_privilege_tables || exit 1
    else
        echo "2Password update failed!"
        interrupt
    fi

    return 0
}

remove_anonymous_users() {
    echo $echo_n "Removing anonymous users"
    do_query "DELETE FROM mysql.user WHERE User='';"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!"
	interrupt
    fi

    return 0
}

remove_remote_root() {
    echo $echo_n "Disallowing root login remotely"
    do_query "DELETE FROM mysql.user WHERE User='root' AND Host!='localhost';"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!"
    fi
}

remove_test_database() {
    echo $echo_n "Remove test database and access to it"
    echo " - Dropping test database..."
    do_query "DROP DATABASE test;"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!  Not critical, keep moving..."
    fi

    echo " - Removing privileges on test database..."
    do_query "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
    else
	echo " ... Failed!  Not critical, keep moving..."
    fi

    return 0
}

reload_privilege_tables() {
    echo $echo_n "Reloading the privilege tables"
    do_query "FLUSH PRIVILEGES;"
    if [ $? -eq 0 ]; then
	echo " ... Success!"
	return 0
    else
	echo " ... Failed!"
	return 1
    fi
}

interrupt() {
    echo
    echo "Aborting!"
    echo
    cleanup
    stty echo
    exit 1
}

cleanup() {
    echo "Cleaning up..."
    rm -f $command
}


# The actual script starts here
restart_service mysqld
prepare
set_echo_compat
#get_root_password $1
#set_root_password $2
set_root_password "$1"
remove_anonymous_users
remove_remote_root
remove_test_database
reload_privilege_tables

cleanup

echo 8MySQL is running
echo 7- A password has been set for the root user
echo 7- Anonymous users were removed
echo 7- Test database has been removed
echo 7- Remote login for root has been disabled

exit 0
