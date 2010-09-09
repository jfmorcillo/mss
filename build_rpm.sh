#!/bin/sh

name=mss
version=`cat version`
release=$(( `cat release` + 1))
svnrev=`head -n11 .svn/entries | tail -n 1`
echo $release > release
rpmtopdir=`rpm --eval %_topdir`

if [ ! -d mss ]; then
    echo You must run this from a $name source checkout top directory
    exit 1
fi

python setup.py sdist

sed -i 's!^\%define svnrev .*$!\%define svnrev '$svnrev'!' packaging/mss.spec
sed -i 's!^\%define version .*$!\%define version '$version'!' packaging/mss.spec
sed -i 's!^\%define release .*$!\%define release '$release'!' packaging/mss.spec

cp -f packaging/$name.spec $rpmtopdir/SPECS
mv -f dist/$name-$version-r$svnrev.tar.gz $rpmtopdir/SOURCES
cp -f packaging/first_time.html packaging/logrotate.conf packaging/mss.desktop packaging/mss.png  $rpmtopdir/SOURCES

rpmbuild -ba --clean --rmsource $rpmtopdir/SPECS/$name.spec
