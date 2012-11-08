#!/bin/sh

./build_mo.sh

gitversion=-`git describe --always --long`
python setup.py setopt -o tag_build -s $gitversion -c egg_info -o tag_date -s 1
python setup.py sdist
