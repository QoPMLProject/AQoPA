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

from qopml.interpreter import VERSION
from qopml.interpreter.simulator.state import PrintExecutor
from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.simulator import EnvironmentDefinitionException
from qopml.interpreter.app import Interpreter, Builder
from qopml.interpreter.simulator.error import RuntimeException,\
    InfiniteLoopException
from qopml.interpreter.module import timeanalysis

class ProgressThread(threading.Thread):

    def __init__(self, file, interpreter, *args, **kwargs):
        super(ProgressThread, self).__init__(*args, **kwargs)
        self.file = file
        self.interpreter = interpreter
        
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
            time.sleep(1)
            progress = self.get_progress()
        self.print_progressbar(progress)
        
        
    def print_progressbar(self, progress):
            """
            Prints the formatted progressbar showing the progress of simulation. 
            """
            percentage = str(int(round(progress*100))) + '%'
            percentage = (' ' * (5-len(percentage))) + percentage
            bar = ('#' * int(round(progress*20))) + (' ' * (20 - int(round(progress*20))))
            self.file.write("\r%s [%s]" % (percentage, bar))
            self.file.flush()
        

def main(qopml_model, print_instructions = False, debug = False):

    ############### DEBUG ###############    
    if debug:
        builder = Builder()
        store = builder.build_store()
        parser = builder.build_parser(store, [])
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
    interpreter = Interpreter(builder=Builder())
    try:
        interpreter.set_qopml_model(qopml_model)
        interpreter.register_qopml_module(timeanalysis.Module())
        interpreter.prepare()
        
        if options.print_instructions:
            for thread in interpreter.threads: 
                thread.simulator.get_executor().prepend_instruction_executor(PrintExecutor(sys.stdout))
        
        if options.show_progressbar:
            progressbar_thread = ProgressThread(sys.stdout, interpreter)
            progressbar_thread.start()
        
        interpreter.run()

    except EnvironmentDefinitionException, e:
        print "Error on creating environment: %s" % e
        if len(e.errors) > 0:
            print "Errors:"
            sys.stderr.write('\n'.join(e.errors))
            print
    except ParserException, e:
        print "Parsing error: %s" % e
        if len(e.syntax_errors):
            print "Syntax errors:"
            sys.stderr.write('\n'.join(e.syntax_errors))
            print
        
    #####################################
    
if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.usage = "%prog [options] model_file"
    parser.add_option("-p", "--print", dest="print_instructions", action="store_true", default=False,
                      help="print executed instruction to standard output")
    parser.add_option("-b", '--progressbar', dest="show_progressbar", action="store_true", default=False,
                      help="show the progressbar of the simulation")
    parser.add_option("-V", '--version', dest="show_version", action="store_true", default=False,
                      help="show version of AQoPA")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="DEBUG mode")
    
    (options, args) = parser.parse_args()
    
    if options.show_version:
        print "AQoPA (version %s)" % VERSION
        sys.exit(0)
    
    if len(args) < 1:
        parser.error("no model_file specified")
    
    if not os.path.exists(args[0]):
        parser.error("model file '%s' does not exist" % args[0])
    
    f = open(args[0], 'r')
    qopml_model = f.read()
    f.close()

    main(qopml_model, print_instructions=options.print_instructions, debug=options.debug)
