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

# Agent translation
POT="locale/agent.pot"
rm -f ${POT}
touch ${POT}
find . -maxdepth 1 -iname "*.py" -exec xgettext -j -o ${POT} --language=Python --keyword=_ {} \;
for name in `find locale -type f -name *.po`; do
	echo -n "updating ${name}..."
	msgmerge --update --add-location --sort-output ${name} ${POT}
done

# Modules translation
for module in modules/*; do
    mod=`basename $module`
    xml=modules/${mod}/desc.xml
    pot=modules/${mod}/locale/${mod}.pot
    if [ -d modules/${mod} ]; then        
        if [ -d modules/${mod}/locale ]; then
            rm -f ${pot}
            touch ${pot}
            if [ -f $xml ]; then
                echo -n "creating ${pot}"
                xml2po -o ${pot} ${xml}
                echo "....done."
            fi
            for po in `find modules/${mod}/locale -type f -name *.po`; do
                if [ -f $po ]; then
                    echo -n "updating ${po}..."
                    msgmerge --update --add-location --sort-output ${po} ${pot}
                fi
            done
        else
            echo "locale dir not found for module ${mod}"
        fi
    fi
done

exit 0
