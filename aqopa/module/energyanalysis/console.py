'''
Created on 05-12-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import sys

from aqopa.simulator.state import Hook

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
        self.output_file.write('Module\tEnergy Analysis (consumption in J)')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n' % self.simulator.context.version.name)
        self.output_file.write('\n')

        voltage = 3.0

        consumptions = self.module.get_hosts_consumptions(self.simulator, context.hosts, voltage)
        for h in context.hosts:
            consumption = 'N/A'
            if h in consumptions:
                consumption = str(consumptions[h])
            self.output_file.write('{0}\t{1:}\t'.format(h.name, consumption))
            self.output_file.write("\n")
        self.output_file.write('\n')
