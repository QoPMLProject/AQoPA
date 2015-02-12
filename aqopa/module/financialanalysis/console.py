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
        self.output_file.write('Module\tFinance Analysis (cost in $)')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n\n' % self.simulator.context.version.name)

        # default cost per one kilowatt-hour
        cost_per_kWh = 0.15

        costs = self.module.calculate_all_costs(self.simulator, context.hosts, cost_per_kWh)

        mincost, minhost = self.module.get_min_cost(self.simulator, context.hosts)
        maxcost, maxhost = self.module.get_max_cost(self.simulator, context.hosts)
        totalcost = self.module.get_total_cost(self.simulator, context.hosts)
        avgcost = self.module.get_avg_cost(self.simulator, context.hosts)

        self.output_file.write('Minimal cost:\t\t{0}\tHost: {1:}\t\n'.format(str(mincost), minhost.name))
        self.output_file.write('Maximal cost: \t\t{0}\tHost: {1:}\t\n'.format(str(maxcost), maxhost.name))
        self.output_file.write('Total cost:\t\t{0}\n'.format(str(totalcost)))
        self.output_file.write('Average cost:\t\t{0}\n'.format(str(avgcost)))

        self.output_file.write("\nActual costs:\n")
        for host in context.hosts:
            self.output_file.write('{0}\t\t{1:}\t'.format(host.name, str(costs[host])))
            self.output_file.write("\n")