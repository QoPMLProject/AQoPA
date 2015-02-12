'''
Created on 31-10-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from aqopa import cmd

cmd.gui_command()