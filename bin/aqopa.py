'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
import optparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.simulator import EnvironmentDefinitionException
from qopml.interpreter.simulator.state import PrintExecutor
from qopml.interpreter.app import Interpreter, Builder
from qopml.interpreter.simulator.error import RuntimeException,\
    InfiniteLoopException
from qopml.interpreter.module import timeanalysis

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
        
        if print_instructions:
            for thread in interpreter.threads: 
                thread.simulator.get_executor().prepend_instruction_executor(PrintExecutor(sys.stdout))
            
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
    #except RuntimeException, e:
    #    print "Runtime error: %s" % e
        
    #####################################
    
if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.usage = "%prog [options] model_file"
    parser.add_option("-p", "--print", dest="print_instructions", action="store_true", default=False,
                      help="print executed instruction to standard output")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="DEBUG mode")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("no model_file specified")
    
    if not os.path.exists(args[0]):
        parser.error("model file '%s' does not exist" % args[0])
    
    f = open(args[0], 'r')
    qopml_model = f.read()
    f.close()

    main(qopml_model, print_instructions=options.print_instructions, debug=options.debug)
