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

        self.output_file.write('-'*80)
        self.output_file.write('\n')
        self.output_file.write('Module\tEnergy Analysis (consumption in J and Ah)')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n' % self.simulator.context.version.name)
        self.output_file.write('\n')

        voltage = 3.0
        self.module.set_voltage(voltage)

        consumptions = self.module.get_hosts_consumptions(self.simulator, context.hosts, voltage)
        for h in context.hosts:
            host_consumptions = {
                'energy': 'N/A',
                'amp-hour': 'N/A',
            }
            if h in consumptions:
                host_consumptions = consumptions[h]
            self.output_file.write('{0}\t{1}\t{2}\t'.format(h.name, str(host_consumptions['energy']),
                                                            str(host_consumptions['amp-hour'])))
            self.output_file.write("\n")
        self.output_file.write('\n')
