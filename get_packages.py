#!/usr/bin/python

"""
Return the list of packages of MSS modules provided by the mss-modules-base
package
"""

import json
import glob

exclude_modules = []
packages = set()

with open('MANIFEST.in') as h:
    for line in h.readlines():
        if line.startswith('prune'):
            exclude_modules.append(line.split('/')[1].strip())

for desc_file in glob.glob('modules/*/desc.json'):
    with open(desc_file) as h:
        desc = json.load(h)
    if desc['slug'] in exclude_modules:
        continue
    if 'packages' not in desc:
        continue
    for pkgs in desc['packages']:
        packages |= set(pkgs["rpms"])

print("\n".join(packages))
