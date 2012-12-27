#!/bin/bash

# This script maps PO and POT files to transifex ressources
# on https://transifex.mandriva.com

if [[ ! -d doc && ! -d mss ]]; then
	echo "Run this script at the top dir of the repository"
	exit 1
fi

which tx > /dev/null
if [ $? -ne 0 ]; then
	echo "Install the transifex client v0.4 (pip install transifex-client==0.4)"
    echo "Newer version WONT work!"
	exit 1
fi

test -d .tx || tx init --host=https://transifex.mandriva.com

tx set --execute --auto-local -r mss.agent -s en -f mss/agent/locale/agent.pot "mss/agent/locale/<lang>/LC_MESSAGES/agent.po"

for mod in mss/agent/modules/*
do
    if [ -d ${mod} ]; then
        name=`basename ${mod}`
        tx set --execute --auto-local -r mss.module-${name} -s en -f ${mod}/locale/${name}.pot "${mod}/locale/<lang>/LC_MESSAGES/${name}.po"
    fi
done

tx set --execute --auto-local -r mss.wizard -s en "mss/www/wizard/locale/<lang>/LC_MESSAGES/django.po"

for layout in mss/www/layout/*
do
    if [ -d ${layout} ]; then
        name=`basename ${layout}`
        tx set --execute --auto-local -r mss.layout-${name} -s en "${layout}/locale/<lang>/LC_MESSAGES/django.po"
    fi
done

echo ""
echo "Setup complete. You can now push/pull translations from transifex."
echo "See help.transifex.net/features/client/index.html for details."
