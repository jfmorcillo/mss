#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

. '../functions.sh'

check_root

hostname=$1
domain=$2

backup /etc/hosts
echo -e "127.0.0.1\tlocalhost.localdomain\tlocalhost" > /etc/hosts
echo -e "127.0.1.1\t${hostname}.${domain}\t${hostname}" >> /etc/hosts
backup /etc/hostname
echo $hostname > /etc/hostname
hostname -F /etc/hostname

echo "0Hostname and domain setup."

exit 0
