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

# git pull

name=mss
version=2.0
release=`grep tag_build setup.cfg | cut -d' ' -f3`
rpmtopdir=`rpm --eval %_topdir`

if [ ! -d mss ]; then
    echo You must run this from a $name source checkout top directory
    exit 1
fi

./manage.sh toprod
./build_mo.sh
python setup.py sdist

if [ $? -ne 0 ]; then
	echo "Error while running setup.py sdist"
	exit 1
fi

cp -f packaging/$name.spec $rpmtopdir/SPECS
mv -f dist/$name-${version}${release}.tar.gz $rpmtopdir/SOURCES
cp -f packaging/first_time.html packaging/logrotate.conf packaging/mss.desktop packaging/mss.png  $rpmtopdir/SOURCES

rpmbuild -bs --clean --rmsource $rpmtopdir/SPECS/$name.spec
