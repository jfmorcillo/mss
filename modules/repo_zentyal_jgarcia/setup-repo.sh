#!/bin/bash
REPO_LOCAL_DIR=/root/zentyal_rpms
REPO_URL=http://people.zentyal.org/~jgarcia/rpms/

if [ -d $REPO_LOCAL_DIR ]; then
    rm -rf $REPO_LOCAL_DIR
fi

mkdir $REPO_LOCAL_DIR
cd $REPO_LOCAL_DIR
wget -q -r -nH -np --accept "*rpm" --cut-dirs=3 $REPO_URL

urpmi.addmedia zentyal_samba4_local_rpms "$REPO_LOCAL_DIR"
