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

cwd=`pwd`

cd mss/agent/modules
for mod in *
do
    if [ -d ${mod} ]; then
        tx set --execute --auto-local -r mss.module-${mod} -s en -f ${mod}/locale/${mod}.pot "${mod}/locale/<lang>/LC_MESSAGES/${mod}.po"
    fi
done

cd $cwd

cd mss/www/layout
for layout in *
do
    if [ -d ${layout} ]; then
        tx set --execute --auto-local -r mss.layout-${layout} -s en "${layout}/locale/<lang>/LC_MESSAGES/django.po"
    fi
done

cd $cwd

cd mss/www/wizard
tx set --execute --auto-local -r mss.wizard -s en "locale/<lang>/LC_MESSAGES/django.po"

echo ""
echo "Setup complete. You can now push/pull translations from transifex."
echo "See help.transifex.net/features/client/index.html for details."
