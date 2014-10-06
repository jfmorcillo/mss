#!/bin/bash
# Copyright Mandriva 2013 all rights reserved

# Include toolbox
. '../functions.sh'

check_mmc_configured

# Import LDAP schema
add_schema ldap/openssh-lpk.schema

# Restart services
restart_service slapd
restart_service mmc-agent /var/log/mmc/mmc-agent.log

exit 0
