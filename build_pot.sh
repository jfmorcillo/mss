#!/bin/sh
#
# Copyright (C) 2006, Jérôme Wax and Adam Cécilefor Linbox FAS
# Copyright (C) 2010, Jean-Philippe Braun for Linbox FAS/Mandriva
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

[ ! -f /usr/bin/xgettext ] && echo "Please install gettext" && exit 1
[ ! -f /usr/bin/json2po ] && echo "Please install json2po" && exit 1

pushd mss/agent

# Agent translation
pot="locale/agent.pot"
json="../../modules/sections.json"
langs="fr_FR pt_BR"
rm -f ${pot}
echo -n "creating ${pot}"
touch ${pot}
json2po --filter=name,desc,description,label,help --progress=none ${json} --pot ${pot}
find . -name modules -prune -o -iname "*.py" -exec xgettext -j -o ${pot} --language=Python --keyword=_ {} \;
# Remove duplicates
sed '/msgctxt/d' ${pot} | msguniq > ${pot}.tmp
mv ${pot}.tmp ${pot}

popd
pushd modules

# Modules translation
for module in modules/*; do
    if [ -d $module ]; then
        mod=`basename $module`
        json=modules/${mod}/desc.json
        pot=modules/${mod}/locale/${mod}.pot
        for lang in $langs; do
            [ ! -d modules/${mod}/locale/$lang/LC_MESSAGES ] && mkdir -p modules/${mod}/locale/$lang/LC_MESSAGES
            touch modules/${mod}/locale/${lang}/LC_MESSAGES/${mod}.po
        done
        rm -f ${pot}
        touch ${pot}
        if [ -f $json ]; then
            echo -n "creating ${pot}"
            json2po --filter=name,desc,description,label,help --progress=none ${json} --pot ${pot}
            bash --dump-po-strings modules/${mod}/*.sh >> ${pot}
            find modules/${mod} -iname "*.py" -exec xgettext -j -o ${pot} --language=Python --keyword=_ {} \;
            # Remove duplicates
            sed '/msgctxt/d' ${pot} | msguniq > ${pot}.tmp
            mv ${pot}.tmp ${pot}
            echo "....done."
        fi
    fi
done

popd
pushd mss/www/wizard
django-admin.py makemessages -l en

popd
pushd mss/www/errors
django-admin.py makemessages -l en

exit 0
