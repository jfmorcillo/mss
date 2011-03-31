#!/bin/bash

# Copy the svnignores.txt file into the svn:ignores information
# for this directory and all contained directories recursively
svn -R propset svn:ignore -F svnignores.txt .
