#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

. '../functions.sh'

check_mmc_configured

# Create configuration file from template
cat tempaltes/sshlpk.ini.tpl > /etc/mmc/plugins/sshlpk.ini

# Import LDAP schema
add_schema /usr/share/doc/python-mmc-base/contrib/ldap/sshlpk.schema

# Restart mmc agent
restart_service mmc-agent /var/log/mmc/mmc-agent.log

exit 0
