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
        
    def execute(self, context):
        """ """

        self.output_file.write('#'*20)
        self.output_file.write('\n')
        self.output_file.write('#      Energy Analysis')
        self.output_file.write('\n')
        self.output_file.write('#'*20)
        self.output_file.write('\n')
        self.output_file.write('\n')

        self.output_file.write('-'*20)
        self.output_file.write('\n')
        self.output_file.write('Version: %s\n' % self.simulator.context.version.name)

        if self.simulator.infinite_loop_occured():
            self.output_file.write('ERROR: Infinite loop on {0} -> {1}\n'.format(
                                unicode(self.simulator.context.get_current_host()),
                                unicode(self.simulator.context.get_current_instruction())))
            self.output_file.write('\n')

        voltage = 3.0
        consumptions = self.module.get_hosts_consumptions(self.simulator, context.hosts, voltage)

        for h in context.hosts:
            self.output_file.write('{0: <15}: {1: <15} '.format(h.name, str(consumptions[h])))
            if h.finished():
                self.output_file.write('Finished')
                if h.get_finish_error():
                    self.output_file.write(' with error: {0}'.format(h.get_finish_error()))
            else:
                self.output_file.write('NOT Finished: {0}'.format(unicode(h.get_current_instructions_context()\
                                                                .get_current_instruction())))
            self.output_file.write("\n")
            
        self.output_file.write('-'*20)
        self.output_file.write('\n')
