#!/usr/bin/python

"""
Return the list of packages of MSS modules provided by the mss-modules-base
package
"""

import json
import glob

exclude_modules = [
    "mds_audit",
    "mds_smb",
    "mds_kerberos",
    "pulse2_inventory",
    "pulse2_imaging",
    "pulse2_deployment",
    "zarafa",
    "eva",
    "egroupware",
    "tftp_server",
    "nfs_server",
]

packages = set()

for desc_file in glob.glob('modules/*/desc.json'):
    with open(desc_file) as h:
        desc = json.load(h)
    if desc['slug'] in exclude_modules:
        continue
    if 'packages' not in desc:
        continue
    for pkgs in desc['packages']:
        packages |= set(pkgs["rpms"])

print("\n".join(sorted(packages)))
