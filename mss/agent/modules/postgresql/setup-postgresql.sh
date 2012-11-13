#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

. '../functions.sh'

check_mmc_configured

SERVICE="postgresql"
PG_CONF_FILE="/var/lib/pgsql/data/pg_hba.conf"
PG_CONF_FILE_TEMPLATE="templates/pg_hba.conf.tpl"

#cat $PG_CONF_FILE_TEMPLATE > $PG_CONF_FILE

restart_service $SERVICE
