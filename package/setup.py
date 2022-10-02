###############################################################################
#####   Setup.py - installs all the required packages and dependancies    #####
###############################################################################

from setuptools import setup, find_packages
import pathlib
import datetime
import re
import argparse
import io
import time
import subprocess
import os
import glob
import csv
import sys
import CiscoStyleCli 


#ensure python version is greater than 3
if sys.version_info[0] < 3:
    sys.exit('Python 3 is the minimum version requirement')

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

setup(name='ciscostylecli',
      version='1.0.2.0',
      description='A Python package for command line interface like cisco',
      long_description = README,
      long_description_content_type = "text/markdown",
      author="charles.lee",
      author_email="cheoljoo@gmail.com",
      license='MIT',
      url='https://github.com/cheoljoo/fish/tree/main/package',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

      install_requires=[
        #   'numpy>=1.16.6',
        #   'delayed',
        #   'scikit-learn==0.24.1',
        #   'requests>=2.25',
        #   'urllib3>=1.26'
      ],

     py_modules=['CiscoStyleCli'], 
     packages=['CiscoStyleCli'],
     include_package_data=True,
     zip_safe=True)

