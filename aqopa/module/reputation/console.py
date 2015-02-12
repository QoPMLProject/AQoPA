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
        self.output_file.write('Module\tReputation')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n\n' % self.simulator.context.version.name)

        for h in context.hosts:
            self.output_file.write('{0}:'.format(h.name))
            variables = self.module.get_host_vars(h)
            if len(variables) == 0:
                self.output_file.write('\t\tNo variables')
            self.output_file.write('\n')
            for var_name in variables:
                self.output_file.write('\t{0}\t{1}\n'.format(var_name, unicode(variables[var_name])))
        self.output_file.write('\n')
