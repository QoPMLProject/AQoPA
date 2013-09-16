'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import Equation, BooleanExpression,\
    IdentifierExpression, CallFunctionExpression


class Builder():
    
    def build_equation(self, token):
        """
        equation : EQUATION equation_complex_expression EQUAL equation_simple_expression SEMICOLON
        """
        return Equation(token[4], token[2])
    
    def build_equation_complex_expression(self, token):
        """
        equation_complex_expression : IDENTIFIER LPARAN equation_function_arguments RPARAN
                                    | IDENTIFIER LPARAN  RPARAN
        """
        if len(token) == 5:
            return CallFunctionExpression(token[1], token[3])
        return CallFunctionExpression(token[1], [])

class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
        self.builder = Builder()
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_equations_specification(self, t):
        t.lexer.push_state('equations')
        return t
    
    ##########################################
    #                TOKENS
    ##########################################

    def token_block_close(self, t):
        r'}'
        
        t.lexer.pop_state()
        return t
    
    ##########################################
    #                RULES
    ##########################################
    
    def equations_specification(self, t):
        """
        specification : EQUATIONS_SPECIFICATION BLOCKOPEN equations_list BLOCKCLOSE
        """
        pass
    
    
    def equations_list(self, t):
        """
        equations_list : equation 
                    | equations_list equation
        """
        pass
    
    def equation(self, t):
        """
        equation : EQUATION equation_complex_expression EQUAL equation_simple_expression SEMICOLON
        """
        self.parser.store.equations.append(self.builder.build_equation(t))
    
    def equation_complex_expression(self, t):
        """
        equation_complex_expression : IDENTIFIER LPARAN equation_function_arguments RPARAN
                                    | IDENTIFIER LPARAN  RPARAN
        """
        t[0] = self.builder.build_equation_complex_expression(t)
    
    def equation_simple_expression(self,t):
        """
        equation_simple_expression : IDENTIFIER 
                                    | BOOL
        """
        if isinstance(t[1], str) or isinstance(t[1], unicode):
            t[0] = IdentifierExpression(t[1])
        else:
            t[0] = BooleanExpression(t[1])
        
    def equation_function_arguments(self, t):
        """
        equation_function_arguments : equation_expression
                                    | equation_function_arguments COMMA equation_expression 
        """
        if len(t) == 2:
            t[0] = [t[1]]
        else:
            t[0] = t[1]
            t[0].append(t[3])
        
    def equation_expression(self, t):
        """
        equation_expression : equation_complex_expression
                            | equation_simple_expression
        """
        t[0] = t[1]
    
    def _extend(self):
        
        self.parser.add_state('equations', 'inclusive')

        self.parser.add_reserved_word('equations', 'EQUATIONS_SPECIFICATION', func=self.word_equations_specification)
        self.parser.add_reserved_word('eq', 'EQUATION', state='equations')

        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['equations'])
        

        self.parser.add_rule(self.equations_specification)
        self.parser.add_rule(self.equations_list)
        self.parser.add_rule(self.equation)
        self.parser.add_rule(self.equation_complex_expression)
        self.parser.add_rule(self.equation_simple_expression)
        self.parser.add_rule(self.equation_function_arguments)
        self.parser.add_rule(self.equation_expression)
        

    