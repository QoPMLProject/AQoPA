'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import threading
from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.model.store import QoPMLModelStore
from qopml.interpreter.simulator import Simulator, EnvironmentDefinitionException
from qopml.interpreter.simulator.state import Context

class VersionThread(threading.Thread):
    """
    One thread for one version
    """
    
    def __init__(self, simulator, *args, **kwargs):
        super(VersionThread, self).__init__(*args, **kwargs)
        self.simulator = simulator
        
    def run(self):
        pass
    
class Builder():
    """
    Builder that builds environment elements
    """
    
    def build_store(self):
        """
        Builds store - keeps all parsed elements from qopml model
        """
        return QoPMLModelStore()
    
    def build_context(self):
        """
        Builds context with initial state.
        """
        return Context()
    
    def build_simulator(self, version):
        """
        Creates simulator for particular version.
        """
        return Simulator(self.build_context())
    
    def build_parser(self, store, modules):
        """
        Builder parser that parses model written in QoPML
        and populates the store.
        """
        from qopml.interpreter.model.parser.lex_yacc import LexYaccParser
        from qopml.interpreter.model.parser.lex_yacc.grammar import main,\
                functions, channels, equations, expressions, instructions, versions,\
                hosts, metrics
        
        parser = LexYaccParser()
        parser.set_store(store) \
                .add_extension(main.ParserExtension()) \
                .add_extension(functions.ParserExtension()) \
                .add_extension(channels.ParserExtension()) \
                .add_extension(equations.ParserExtension()) \
                .add_extension(expressions.ParserExtension()) \
                .add_extension(instructions.ParserExtension()) \
                .add_extension(versions.ParserExtension()) \
                .add_extension(hosts.ParserExtension()) \
                .add_extension(metrics.ParserExtension())
                
        for m in modules:
            parser = m.extend_parser(parser)
                
        return parser.build()
    
class Interpreter():
    """
    Interpreter is responsible for parsing the model,
    creating the environment for simulations,
    manipulating selected models.
    """
    
    def __init__(self, builder=None, model_as_text=""):
        self.builder = builder if builder is not None else Builder()
        self.model_as_text = model_as_text
        
        self.store = self.builder.build_store()
        self.threads = []
        
        self.modules = []
        
    def set_qopml_model(self, model_as_text):
        """
        Set qopml model that will be interpreted.
        """
        self.model_as_text = model_as_text
        return self
    
    def register_qopml_module(self, qopml_module):
        """
        Registers new module
        """
        if qopml_module in self._modules:
            raise EnvironmentDefinitionException(u"QoPML Module '%s' is already registered" % unicode(qopml_module))
        self._modules.append(qopml_module)
        return self
        
    def _parse(self):
        """
        Parses the model from model_as_text field and populates the store.
        """
        
        if len(self.model_as_text) == 0:
            raise EnvironmentDefinitionException("QoPML Model not provided")
    
        parser = self.builder.build_parser(self.store, self.modules)
        parser.parse(self.model_as_text)
        
        if len(parser.get_syntax_errors()) > 0:
            raise ParserException('Invalid syntax', syntax_errors=parser.get_syntax_errors())
        
    def run(self):
        self._parse()
        
