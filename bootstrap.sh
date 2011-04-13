#!/bin/bash

for package in `cat requirements/apps.txt`
do
    urpmi --auto $package
done
