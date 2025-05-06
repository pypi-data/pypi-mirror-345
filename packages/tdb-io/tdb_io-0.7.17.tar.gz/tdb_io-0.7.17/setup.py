#!/usr/bin/env python
import os
from setuptools import setup, find_packages
#
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#exec(open('version.py').read())

import os.path

def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="tdb_io",
    description="tool to fast look into influxdb and insert data from python",
    author="jaromrax",
    author_email="jaromrax@gmail.com",
    licence="GPL2",
    version=get_version("tdb_io/version.py"),
    #packages=find_packages(),
    packages=['tdb_io'],
    package_data={'tdb_io': ['data/*']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    scripts = ['bin/tdb_io'],
    install_requires = ['pymongo','matplotlib','argparse','pandas','numpy','datetime','fire','influxdb', 'drawilleplot', 'tzlocal', 'console'],
    # tables were not on core6a but yes on zotac2
    # terminaltables==3.1.10
)
 #
