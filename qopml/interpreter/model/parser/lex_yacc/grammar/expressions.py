'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from qopml.interpreter.model.parser.lex_yacc.parser import LexYaccParserExtension


class Builder():

    pass

class ParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
        self.builder = Builder()
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    ##########################################
    #                TOKENS
    ##########################################

    ##########################################
    #                RULES
    ##########################################
    
    def expression_test(self, t):
        """
        specification : expression_function_arguments
        """
        pass
    
    def expression_conditional(self, t):
        """
        expression_conditional : expression_comaprison
                        | BOOL
        """
        pass
    
    def expression_tuple(self, t):
        """
        expression_tuple : LPARAN RPARAN 
                        | LPARAN expression_function_arguments RPARAN
        """
        pass
    
    def expression_tuple_element(self, t):
        """
        expression_tuple_element : IDENTIFIER SQ_LPARAN INTEGER SQ_RPARAN
        """
        pass
    
    def expression_function_arguments(self, t):
        """
        expression_function_arguments : expression_simple
                                    | expression_function_arguments COMMA expression_simple
        """
        pass
        
    def expression_call_function(self, t):
        """
        expression_call_function : IDENTIFIER LPARAN RPARAN 
                                | IDENTIFIER LPARAN expression_function_arguments RPARAN
                                | IDENTIFIER LPARAN RPARAN SQ_LPARAN expression_function_qop_arguments SQ_RPARAN
                                | IDENTIFIER LPARAN expression_function_arguments RPARAN SQ_LPARAN expression_function_qop_arguments SQ_RPARAN
        """
        pass
    
    def expression_function_qop_arguments(self, t):
        """
        expression_function_qop_arguments : TEXT 
                                        | expression_function_qop_arguments COMMA TEXT 
        """
        pass
    
    def expression_simple(self, t):
        """
        expression_simple : expression_call_function
                        | expression_tuple_element
                        | expression_tuple
                        | IDENTIFIER
                        | BOOL
        """
        pass
    
    def expression_comaprison(self, t):
        """
        expression_comaprison : expression_simple EQUAL EQUAL expression_simple
        """
        pass
    
    def _extend(self):
        
        self.parser.add_rule(self.expression_test)
        
        self.parser.add_rule(self.expression_conditional)
        self.parser.add_rule(self.expression_tuple)
        self.parser.add_rule(self.expression_tuple_element)
        self.parser.add_rule(self.expression_function_arguments)
        self.parser.add_rule(self.expression_call_function)
        self.parser.add_rule(self.expression_function_qop_arguments)
        self.parser.add_rule(self.expression_simple)
        self.parser.add_rule(self.expression_comaprison)
        

    