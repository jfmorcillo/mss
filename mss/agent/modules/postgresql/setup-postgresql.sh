#!/bin/bash
# Copyright Mandriva 2012 all rights reserved

. '../functions.sh'

check_root

restart_service postgresql
sleep 10

info_b $"Postgresql is running."
