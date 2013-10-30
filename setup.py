#!/usr/bin/env python
'''
Created on 28-10-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from setuptools import setup, find_packages
import aqopa

def read(filename):
    with open(filename) as f:
        return f.read()


setup(name='AQoPA',
      
      version=aqopa.VERSION,
      description='Automated Quality of Protection Analysis Tool for QoP-ML models.',
      long_description=read('README.md'),
      author='Damian Rusinek',
      author_email='damian.rusinek@gmail.com',
      url='http://qopml.org/aqopa/',
      
      license='Freeware',
      platforms=["any"],
      
      install_requires=[read('requirements').split("\n")],
      
      packages=find_packages(),
      package_data={'aqopa': ['bin/assets/logo.png']},
      
      entry_points = {
        'console_scripts': [
            'aqopa-gui = aqopa.cmd:gui_command',
            'aqopa-console = aqopa.cmd:console_command',
        ]
      },
      
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: Freeware',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: System :: Monitoring',
      ]
     )