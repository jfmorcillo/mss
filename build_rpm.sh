#!/bin/sh
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

name=mss
version=`cat version`
# bump release number
release=$(( `cat release` + 1))
svnrev=`head -n11 .svn/entries | tail -n 1`
echo $release > release
rpmtopdir=`rpm --eval %_topdir`

if [ ! -d mss ]; then
    echo You must run this from a $name source checkout top directory
    exit 1
fi

todev=0
./manage.sh isprod
if [ $? -ne 0 ]; then
	todev=1
	./manage.sh toprod
fi

./bin/build_mo.sh

python setup.py sdist

if [ $? -ne 0 ]; then
	echo "Error while running setup.py sdist"
	exit 1
fi

sed -i 's!^\%define svnrev .*$!\%define svnrev '$svnrev'!' packaging/mss.spec
sed -i 's!^\%define version .*$!\%define version '$version'!' packaging/mss.spec
sed -i 's!^\%define release .*$!\%define release '$release'!' packaging/mss.spec

cp -f packaging/$name.spec $rpmtopdir/SPECS
mv -f dist/$name-$version-r$svnrev.tar.gz $rpmtopdir/SOURCES
cp -f packaging/first_time.html packaging/logrotate.conf packaging/mss.desktop packaging/mss.png  $rpmtopdir/SOURCES

rpmbuild -ba --clean --rmsource $rpmtopdir/SPECS/$name.spec

if [ $todev -eq 1 ]; then
	./manage.sh todev
fi
