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
        self.output_file.write('Module\tCarbon Dioxide Emissions Analysis (pounds of CO2 produced per kWh)')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n\n' % self.simulator.context.version.name)

        # temp default value
        pounds_of_co2_per_kWh = 1.85

        emissions = self.module.calculate_all_emissions(self.simulator, context.hosts, pounds_of_co2_per_kWh)

        minemission, minhost = self.module.get_min_emission(self.simulator, context.hosts)
        maxemission, maxhost = self.module.get_max_emission(self.simulator, context.hosts)
        totalemission = self.module.get_total_emission(self.simulator, context.hosts)
        avgemission = self.module.get_avg_emission(self.simulator, context.hosts)

        self.output_file.write('Minimal emission:\t{0}\tHost: {1:}\t\n'.format(str(minemission), minhost.name))
        self.output_file.write('Maximal emission: \t{0}\tHost: {1:}\t\n'.format(str(maxemission), maxhost.name))
        self.output_file.write('Total emission:\t\t{0}\n'.format(str(totalemission)))
        self.output_file.write('Average emission:\t{0}\n'.format(str(avgemission)))

        self.output_file.write("\nActual emissions:\n")
        for host in context.hosts:
            self.output_file.write('{0}\t\t{1:}\t'.format(host.name, str(emissions[host])))
            self.output_file.write("\n")