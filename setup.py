from setuptools import setup, find_packages
import sys, os

version = '2.0'

setup(
    name='mss',
    author = "Jean-Philippe Braun",
    author_email = "jpbraun@mandriva.com",
    maintainer = "Jean-Philippe Braun",
    maintainer_email = "jpbraun@mandriva.com",
    version = version,
    description = "Mandriva Server Setup",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
)
