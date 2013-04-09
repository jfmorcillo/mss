#!/bin/sh

git clean -fdx
sh build_mo.sh
gitversion=-`git describe --always --long`
python setup.py setopt -o tag_build -s $gitversion -c egg_info
python setup.py setopt -o tag_date -s 1 -c egg_info
python setup.py sdist
