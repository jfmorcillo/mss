#!/bin/sh

git pull
git clean -fdx
sh build_mo.sh
gitversion=-`git describe --always --long`
gitbranch=`git rev-parse --abbrev-ref HEAD`
python setup.py setopt -o tag_build -s $gitversion-$gitbranch -c egg_info
python setup.py setopt -o tag_date -s 1 -c egg_info
python setup.py sdist
