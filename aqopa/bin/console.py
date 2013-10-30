#!/usr/bin/env python
'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
import threading
import time

from aqopa.model.parser import ModelParserException,\
    MetricsParserException, ConfigurationParserException
from aqopa.app import Builder, ConsoleInterpreter
from aqopa.simulator import EnvironmentDefinitionException
from aqopa.module import timeanalysis

class ProgressThread(threading.Thread):

    def __init__(self, f, interpreter, *args, **kwargs):
        super(ProgressThread, self).__init__(*args, **kwargs)
        self.file = f
        self.interpreter = interpreter
        self.signs = '|/-\\'
        self.sign_no = 0
        
    def get_progress(self):
        all_progress = 0.0
        sum_progress = 0.0
        for thr in self.interpreter.threads:
            all_progress += 1
            sum_progress += thr.simulator.context.get_progress()
        progress = 0
        if all_progress > 0:
            progress = sum_progress / all_progress
        return progress
            
    def run(self):
        
        progress = self.get_progress()
        while progress < 1:
            self.print_progressbar(progress)
            time.sleep(0.1)
            progress = self.get_progress()
        self.print_progressbar(progress)
        
        
    def print_progressbar(self, progress):
            """
            Prints the formatted progressbar showing the progress of simulation. 
            """
            self.sign_no += 1
            sign = self.signs[self.sign_no % len(self.signs)]
            
            percentage = str(int(round(progress*100))) + '%'
            percentage = (' ' * (5-len(percentage))) + percentage
            
            bar = ('#' * int(round(progress*20))) + (' ' * (20 - int(round(progress*20))))
            
            self.file.write("\r%c[%s] %s" % (sign, bar, percentage))
            self.file.flush()
        

def run(qopml_model, qopml_metrics, qopml_configuration, 
         save_states = False, debug = False, show_progressbar = False):

    ############### DEBUG ###############    
    if debug:
        builder = Builder()
        store = builder.build_store()
        parser = builder.build_model_parser(store, [])
        parser.lexer.input(qopml_model)
        while True:
            print  parser.lexer.current_state()
            tok = parser.lexer.token()
            if not tok:
                break
            print tok
            print ""
        print 'Errors: ' + str(parser.get_syntax_errors())
        print ""
        print ""
    
    #####################################
    interpreter = ConsoleInterpreter()
    try:
        interpreter.set_qopml_model(qopml_model)
        interpreter.set_qopml_metrics(qopml_metrics)
        interpreter.set_qopml_config(qopml_configuration)
        
        interpreter.register_qopml_module(timeanalysis.Module())
        
        interpreter.parse()
        interpreter.prepare()
        
        if save_states:
            for simulator in interpreter.simulators: 
                interpreter.save_states_to_file(simulator)
        
        if show_progressbar:
            progressbar_thread = ProgressThread(sys.stdout, interpreter)
            progressbar_thread.start()
        
        interpreter.run()

    except EnvironmentDefinitionException, e:
        sys.stderr.write('Error on creating environment: %s\n' % e)
        if len(e.errors) > 0:
            sys.stderr.write('Errors:\n')
            sys.stderr.write('\n'.join(e.errors))
            sys.stderr.write('\n')
    except ModelParserException, e:
        sys.stderr.write('Model parsing error: %s\n' % e)
        if len(e.syntax_errors):
            sys.stderr.write('Syntax errors:\n')
            sys.stderr.write('\n'.join(e.syntax_errors))
            sys.stderr.write('\n')
    except MetricsParserException, e:
        sys.stderr.write('Metrics parsing error: %s\n' % e)
        if len(e.syntax_errors):
            sys.stderr.write('Syntax errors:\n')
            sys.stderr.write('\n'.join(e.syntax_errors))
            sys.stderr.write('\n')
    except ConfigurationParserException, e:
        sys.stderr.write('Configuration parsing error: %s\n' % e)
        if len(e.syntax_errors):
            sys.stderr.write('Syntax errors:\n')
            sys.stderr.write('\n'.join(e.syntax_errors))
            sys.stderr.write('\n')
        
