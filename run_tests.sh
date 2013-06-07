#!/bin/bash

export LC_ALL=C

[ $UID -ne 0 ] && echo "Run as root." && exit 1

for unittest in basic config validation
do
    python mss/agent/tests/${unittest}.py
done
