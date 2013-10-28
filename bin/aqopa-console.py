'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
import optparse
import threading
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from aqopa import VERSION
from aqopa.simulator.state import PrintExecutor
from aqopa.model.parser import ParserException, ModelParserException,\
    MetricsParserException, ConfigurationParserException
from aqopa.simulator import EnvironmentDefinitionException
from aqopa.app import Interpreter, Builder, ConsoleInterpreter
from aqopa.simulator.error import RuntimeException,\
    InfiniteLoopException
from aqopa.module import timeanalysis

class ProgressThread(threading.Thread):

    def __init__(self, file, interpreter, *args, **kwargs):
        super(ProgressThread, self).__init__(*args, **kwargs)
        self.file = file
        self.interpreter = interpreter
        self.signs = '|/-\\'
        self.sign_no = 0
        
    def get_progress(self):
        all = 0.0
        sum = 0.0
        for thr in self.interpreter.threads:
            all += 1
            sum += thr.simulator.context.get_progress()
        progress = 0
        if all > 0:
            progress = sum / all
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
        

def main(qopml_model, qopml_metrics, qopml_configuration, 
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
        interpreter.set_qopml_config(qopml_config)
        
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
        
    #####################################
    
if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.usage = "%prog [options]"
    parser.add_option("-f", "--model-file", dest="model_file",  metavar="FILE",
                      help="specifies model file")
    parser.add_option("-m", "--metrics-file", dest="metrics_file",  metavar="FILE",
                      help="specifies file with metrics")
    parser.add_option("-c", "--config-file", dest="config_file",  metavar="FILE",
                      help="specifies file with modules configuration")
    parser.add_option("-s", "--states", dest="save_states", action="store_true", default=False,
                      help="save states flow in a file")
    parser.add_option("-p", '--progressbar', dest="show_progressbar", action="store_true", default=False,
                      help="show the progressbar of the simulation")
    parser.add_option("-V", '--version', dest="show_version", action="store_true", default=False,
                      help="show version of AQoPA")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="DEBUG mode")
    
    (options, args) = parser.parse_args()
    
    if options.show_version:
        print "AQoPA (version %s)" % VERSION
        sys.exit(0)
    
    if not options.model_file:
        parser.error("no qopml model file specified")
    if not os.path.exists(options.model_file):
        parser.error("qopml model file '%s' does not exist" % options.model_file)
        
    if not options.metrics_file:
        parser.error("no metrics file specified")
    if not os.path.exists(options.metrics_file):
        parser.error("metrics file '%s' does not exist" % options.metrics_file)
        
    if not options.config_file:
        parser.error("no configuration file specified")
    if not os.path.exists(options.config_file):
        parser.error("configuration file '%s' does not exist" % options.config_file)
    
    
    f = open(options.model_file, 'r')
    qopml_model = f.read()
    f.close()
    f = open(options.metrics_file, 'r')
    qopml_metrics = f.read()
    f.close()
    f = open(options.config_file, 'r')
    qopml_config = f.read()
    f.close()

    main(qopml_model, qopml_metrics, qopml_config, 
         save_states=options.save_states, debug=options.debug,
         show_progressbar=options.show_progressbar)
