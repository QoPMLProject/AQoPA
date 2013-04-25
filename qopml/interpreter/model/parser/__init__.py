'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class QoPMLModelParser():
    
    def parse(self, s):
        """
        Parses string s and returns the store of all required parsed objects.
        The parser can also store created objects in his own store.
        Sometimes modules will add parsing rules and the results should be keept by the modules,
        so information about custom stores filling in is kept in modules code. 
        """
        raise NotImplementedError()
    
class ParserException(Exception):   
    pass 

# At the moment, only lex/yacc parser is available
# Therefore, no fancy parser builder and api is created for modules
# Modules at the moment can think of only lex/yacc parser and
# use its small api
def get_parser(store):
    from qopml.interpreter.model.parser.lex_yacc import parser
    return parser.create(store)


    