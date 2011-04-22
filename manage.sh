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

todev() {
	echo -n "Swithing to dev environement..."
	rm -rf mss/www/cpserver
	cp -r mss/www/cpserver-dev mss/www/cpserver
	sed -i "s!^DEBUG.*!DEBUG = True!" mss/www/settings.py
	sed -i 's!^\(.*logging\.\)INFO\(.*\)$!\1DEBUG\2!' mss/agent/module.py
	echo "dev"
}

isprod() {
	grep -q "DEBUG = False" mss/www/settings.py
	if [ $? -eq 0 ]; then
		return 0
	else
		return 1
	fi
}

toprod() {
	echo -n "Swithing to prod environement..."
	rm -rf mss/www/cpserver
	cp -r mss/www/cpserver-prod mss/www/cpserver
	sed -i "s!^DEBUG.*!DEBUG = False!" mss/www/settings.py
	sed -i 's!^\(.*logging\.\)DEBUG\(.*\)$!\1INFO\2!' mss/agent/managers/module.py
	echo "done"
}

case "$1" in
	todev)
		todev
		;;
	toprod)
		toprod
		;;
	isprod)
		isprod
		;;
	*)
		echo "Usage: $0 [toprod | todev | isprod]"
		;;
esac
