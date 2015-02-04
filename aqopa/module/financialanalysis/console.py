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

        self.output_file.write('-'*20)
        self.output_file.write('\n')
        self.output_file.write('Module\tFinance Analysis')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n' % self.simulator.context.version.name)

        # default cost per one kilowatt-hour
        cost_per_kWh = 0.15

        # calculate costs for every host: total, min, max, avg
        costs = self.module.calculate_all_costs(self.simulator, context.hosts, cost_per_kWh)
        mincost, minhost = self.module.get_min_cost(self.simulator, context.hosts)
        maxcost, maxhost = self.module.get_max_cost(self.simulator, context.hosts)
        totalcost = self.module.get_total_cost(self.simulator, context.hosts)
        avgcost = self.module.get_avg_cost(self.simulator, context.hosts)

        self.output_file.write("Minimal cost :")

        for host, cost in context.hosts, costs:
            self.output_file.write("Host: " + host.original_name() + ", Cost: " + str(cost) + " $\n")