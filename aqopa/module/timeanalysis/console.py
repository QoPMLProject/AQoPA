'''
Created on 07-09-2013

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
        self.output_file.write('Module\tTime Analysis (time in s)')
        self.output_file.write('\n')
        self.output_file.write('Version\t%s\n\n' % self.simulator.context.version.name)
        
        if self.simulator.infinite_loop_occured():
            self.output_file.write('ERROR\tInfinite loop on {0} -> {1}\n'.format(
                                unicode(self.simulator.context.get_current_host()),
                                unicode(self.simulator.context.get_current_instruction())))
            self.output_file.write('\n')

        for h in context.hosts:
            self.output_file.write('{0}\t{1}\t'.format(h.name, str(self.module.get_current_time(self.simulator, h))))
            if h.finished():
                self.output_file.write('Finished')
                if h.get_finish_error():
                    self.output_file.write(' with error\t{0}'.format(h.get_finish_error()))
            else:
                self.output_file.write('NOT Finished\t{0}'.format(unicode(h.get_current_instructions_context()\
                                                                .get_current_instruction())))
            self.output_file.write("\n")
            
        self.output_file.write('\n')
        self.output_file.write('Dropped messages\n')
        i = 0
        for c in context.channels_manager.channels:
            if c.get_dropped_messages_nb() > 0:
                i += 1
                self.output_file.write('%s\t%d\n' % (c.name, c.get_dropped_messages_nb()))
        if i == 0:
            self.output_file.write('None\n')
        self.output_file.write('\n')
