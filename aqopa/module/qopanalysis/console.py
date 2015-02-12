#!/usr/bin/env python

import sys
from aqopa.simulator.state import Hook

"""
@file       console.py
@author     Katarzyna Mazur
"""

class PrintResultsHook(Hook):

    def __init__(self, module, simulator, output_file=sys.stdout):
        """ """
        self.module = module
        self.simulator = simulator
        self.output_file = output_file

    def execute(self, context, **kwargs):
        """ """

        self.output_file.write('-'*80)
        self.output_file.write('\n')
        self.output_file.write('Module\tQoP Analysis')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n\n' % self.simulator.context.version.name)

        self.output_file.write('All occured facts:\t{0}\n'.format(self.module.get_all_facts()))

        self.output_file.write("\nActual facts:\n")
        for host in context.hosts:
            self.output_file.write('Host:\t{0}\tFacts: {1:}\t\n'.format(host.name, str(self.module.get_occured_facts(self.simulator, host))))