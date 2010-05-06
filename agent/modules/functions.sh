# Copyright Mandriva 2009, 2010 all rights reserved

function echo_v() {
	if [ -n "$verbose" ]; then
		echo "== $@"
	fi
}

# output: stdout: example.com or the possible detected domain
function detect_domain() {
	mydomain=`hostname -d`
	if [ -z "$mydomain" ]; then
		mydomain="example.com"
	fi
	echo "$mydomain"
	return 0
}

# output: stdout: name of temporary file
# *exits* if error
function make_temp() {
	tmpfile=`mktemp ${TMP:-/tmp}/mandriva-mds.XXXXXXXXXXXX`
	if [ -f "$tmpfile" ]; then
		echo "$tmpfile"
		return 0
	else
		echo "error while making temporary file" >&2
		exit 1
	fi
}

# $1: domain
# returns standard dc=foo,dc=bar suffix on stdout
function calc_suffix() {
	old_ifs=${IFS}
	IFS="."
	for component in $1; do
		result="$result,dc=$component"
	done
	IFS="${old_ifs}"
	echo "${result#,}"
	return 0
}

# $1: *file* to be backed up
# output (stdout): backup filename
function mybackup() {
    now=`date +%s`
    if [ ! -f "$1" ]; then
        echo "Internal error, $1 has to be a file" >&2
        echo "Aborting" >&2
        exit 1
    fi
    newname="$1.$now"
    cp -a "$1" "$newname"
    echo "$newname"
    return 0
}

# $1: *file* to be backed up
# output (stdout): backup filename
function backup() {
    now=`date +%s`
	if [ ! -f "$1" ]; then
        echo "1No file to backup"
    else
        newname="$1-mmc-wizard-$now"
        cp -a "$1" "$newname"
        if [ $? -eq 0 ]; then 
            echo "0Backed up #$1# to #$newname"
        else 
            echo "1Cannot make backup for $1"
            exit 1
        fi
	fi
}

# $1: directory where the LDAP database is
# output (stdout): backup dir of the previous database
function clean_database() {
    now=`date +%s`
	backupdir="/var/lib/ldap.$now"
	cp -a "$1" "$backupdir" 2>/dev/null
	if [ "$?" -ne "0" ]; then
		echo "Error, could not make a backup copy of the"
		echo "current LDAP database, aborting..."
		echo
		echo "(not enough disk space?)"
		echo
		exit 1
	fi
	rm -f "$1"/{*.bdb,log.*,__*,alock}
	echo "$backupdir"
	return 0
}
