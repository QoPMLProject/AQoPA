'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
import optparse
from qopml.interpreter.model import AssignmentInstruction,\
    CommunicationInstruction, FinishInstruction, ContinueInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction, HostSubprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.simulator import EnvironmentDefinitionException
from qopml.interpreter.simulator.state import InstructionExecutor,\
    ExecutionResult, Process, Hook
from qopml.interpreter.app import Interpreter, Builder
from qopml.interpreter.simulator.error import RuntimeException
from qopml.interpreter.module import timeanalysis

debug = False

class PrintExecutor(InstructionExecutor):
    """
    Excecutor writes current instruction to the stream.
    """
    
    def __init__(self, f):
        self.file = f       # File to write instruction to
        
        self.result = ExecutionResult()
        
    def execute_instruction(self, context):
        """ Overriden """
        self.file.write("Host: %s \t" % context.get_current_host().name)
        instruction = context.get_current_instruction()
        simples = [AssignmentInstruction, CommunicationInstruction, FinishInstruction, ContinueInstruction]
        for s in simples:
            if isinstance(instruction, s):
                self.file.write(unicode(instruction))
                
        if isinstance(instruction, CallFunctionInstruction):
            self.file.write(instruction.function_name + '(...)')
            
        if isinstance(instruction, IfInstruction):
            self.file.write('if (%s) ...' % unicode(instruction.condition))
            
        if isinstance(instruction, WhileInstruction):
            self.file.write('while (%s) ...' % unicode(instruction.condition))
            
        if isinstance(instruction, Process):
            self.file.write('process %s ...' % unicode(instruction.name))
            
        if isinstance(instruction, HostSubprocess):
            self.file.write('subprocess %s ...' % unicode(instruction.name))
        self.file.write("\n") 
        
        return self.result
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return True


class ProgressBarHook(Hook):
    
    def __init__(self, file):
        self.file = file
    
    def execute(self, context):
        """
        Hook does not change the context. 
        It get informations about the state of the process
        and prints it. 
        """
        progress = 0.2
        
        
        
        percentage = str(round(progress*100)) + '%'
        percentage = ' ' * (5-len(percentage)) + percentage
        bar = ('=' * round(progress*20)) + (' ' * (20 - round(progress*20)))
        self.file.write("\r%s -> %s [%s]", (version, percentage, bar))
        

def main(qopml_model, print_instructions = False):

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
                thread.simulator.register_hook()
            
        interpreter.run()
    except EnvironmentDefinitionException, e:
        print "Error on creating environment: %s" % e
        if len(e.errors) > 0:
            print "Errors:"
            sys.stderr.write('\n'.join(e.errors))
            print
        return
    except ParserException, e:
        print "Parsing error: %s" % e
        if len(e.syntax_errors):
            print "Syntax errors:"
            sys.stderr.write('\n'.join(e.syntax_errors))
            print
        return
    except RuntimeException, e:
        print "Runtime error: %s" % e
        return
    #####################################
    
if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.usage = "%prog [options] model_file"
    parser.add_option("-p", "--print", dest="print_instructions", action="store_true", default=False,
                      help="print executed instruction to standard output")
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("no model_file specified")
    
    if not os.path.exists(args[0]):
        parser.error("model file '%s' does not exist" % args[0])
    
    f = open(args[0], 'r')
    qopml_model = f.read()
    f.close()

    main(qopml_model, options.print_instructions)