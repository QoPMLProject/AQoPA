#!/usr/bin/env python
'''
Created on 28-10-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from setuptools import setup, find_packages
import os
import aqopa

def read(filename):
    with open(filename) as f:
        return f.read()

def find_library_data():
    data_files = []
    path = os.path.join('aqopa', 'library', 'models')
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path, dir_name) 
        
        if os.path.isdir(dir_path):
            dir_data_files = []
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    dir_data_files.append(file_path)
            if len(dir_data_files) > 0:
                data_files.append((dir_path, dir_data_files))
    return data_files
    
print find_library_data()

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
      package_data={'aqopa' : ['bin/assets/logo.png']},
      data_files=find_library_data(),
      
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

