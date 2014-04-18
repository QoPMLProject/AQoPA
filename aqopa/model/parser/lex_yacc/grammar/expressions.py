'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import BooleanExpression, TupleExpression,\
    TupleElementExpression, IdentifierExpression, ComparisonExpression,\
    CallFunctionExpression, COMPARISON_TYPE_EQUAL, COMPARISON_TYPE_NOT_EQUAL


class Builder():

    def build_expression_call_function(self, token):
        """
        expression_call_function : IDENTIFIER LPARAN RPARAN 
                                | IDENTIFIER LPARAN expression_function_arguments RPARAN
                                | IDENTIFIER LPARAN RPARAN SQLPARAN expression_function_qop_arguments SQRPARAN
                                | IDENTIFIER LPARAN expression_function_arguments RPARAN SQLPARAN expression_function_qop_arguments SQRPARAN
        """
        arguments = []
        qop_arguments = []
        
        if len(token) == 5:
            arguments = token[3]
        elif len(token) == 7:
            qop_arguments = token[5]
        elif len(token) == 8:
            arguments = token[3]
            qop_arguments = token[6]
            
        return CallFunctionExpression(token[1], arguments, qop_arguments)

    def build_expression_call_id_function(self, token):
        """
        expression_call_function : ID LPARAN RPARAN
                                | ID LPARAN IDENTIFIER RPARAN
                                | ID LPARAN QUALIFIED_IDENTIFIER RPARAN
        """
        arguments = []
        if len(token) == 5:
            arguments.append(IdentifierExpression(token[3]))
        return CallFunctionExpression(token[1], arguments)

    def build_expression_call_routing_next(self, token):
        """
        expression_call_function : ROUTING_NEXT LPARAN IDENTIFIER COMMA expression_call_routing_next_argument RPARAN
                                            | ROUTING_NEXT LPARAN IDENTIFIER COMMA expression_call_routing_next_argument COMMA expression_call_routing_next_argument RPARAN
        """
        arguments = [IdentifierExpression(token[3]), token[5]]
        if len(token) == 9:
            arguments.append(token[7])
        return CallFunctionExpression(token[1], arguments)

    def build_comparison_expression(self, token):
        """
        expression_comaprison : expression_simple EQUAL EQUAL expression_simple
                            | expression_simple EXCLAMATION EQUAL expression_simple
        """
        comparison_type = COMPARISON_TYPE_EQUAL if token[2] == '=' else COMPARISON_TYPE_NOT_EQUAL
        return ComparisonExpression(token[1], token[4], comparison_type)

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
    
    ##########################################
    #                TOKENS
    ##########################################

    ##########################################
    #                RULES
    ##########################################
    
    def expression_conditional(self, t):
        """
        expression_conditional : expression_comaprison
                        | BOOL
        """
        if isinstance(t[1], bool):
            t[0] = BooleanExpression(t[1])
        else:
            t[0] = t[1]
    
    def expression_tuple(self, t):
        """
        expression_tuple : LPARAN RPARAN 
                        | LPARAN expression_function_arguments RPARAN
        """
        elements = []
        if len(t) > 3:
            elements = t[2]
        t[0] = TupleExpression(elements)
    
    def expression_tuple_element(self, t):
        """
        expression_tuple_element : IDENTIFIER SQLPARAN INTEGER SQRPARAN
        """
        t[0] = TupleElementExpression(t[1], t[3])
    
    def expression_function_arguments(self, t):
        """
        expression_function_arguments : expression_simple
                                    | expression_function_arguments COMMA expression_simple
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[3])
        
    def expression_call_function(self, t):
        """
        expression_call_function : IDENTIFIER LPARAN RPARAN 
                                | IDENTIFIER LPARAN expression_function_arguments RPARAN
                                | IDENTIFIER LPARAN RPARAN SQLPARAN expression_function_qop_arguments SQRPARAN
                                | IDENTIFIER LPARAN expression_function_arguments RPARAN SQLPARAN expression_function_qop_arguments SQRPARAN
        """
        t[0] = self.builder.build_expression_call_function(t)

    def expression_call_id_function(self, t):
        """
        expression_call_function : ID LPARAN RPARAN
                                | ID LPARAN IDENTIFIER RPARAN
                                | ID LPARAN QUALIFIED_IDENTIFIER RPARAN
        """
        t[0] = self.builder.build_expression_call_id_function(t)

    def expression_call_routing_next_function(self, t):
        """
        expression_call_function : ROUTING_NEXT LPARAN IDENTIFIER COMMA expression_call_routing_next_argument RPARAN
                                            | ROUTING_NEXT LPARAN IDENTIFIER COMMA expression_call_routing_next_argument COMMA expression_call_routing_next_argument RPARAN
        """
        t[0] = self.builder.build_expression_call_routing_next(t)

    def expression_call_routing_next_argument(self, t):
        """
        expression_call_routing_next_argument : expression_call_function
                                            | expression_tuple_element
                                            | IDENTIFIER
        """
        if isinstance(t[1], str) or isinstance(t[1], unicode):
            t[0] = IdentifierExpression(t[1])
        else:
            t[0] = t[1]
    
    def expression_function_qop_arguments(self, t):
        """
        expression_function_qop_arguments : TEXT 
                                        | expression_function_qop_arguments COMMA TEXT 
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1].strip())
        else:
            t[0] = t[1]
            t[0].append(t[3].strip())
    
    def expression_simple(self, t):
        """
        expression_simple : expression_call_function
                        | expression_tuple_element
                        | expression_tuple
                        | IDENTIFIER
                        | BOOL
        """
        if isinstance(t[1], bool):
            t[0] = BooleanExpression(t[1])
        elif isinstance(t[1], str) or isinstance(t[1], unicode):
            t[0] = IdentifierExpression(t[1])
        else:
            t[0] = t[1]
    
    def expression_comaprison(self, t):
        """
        expression_comaprison : expression_simple EQUAL EQUAL expression_simple
                            | expression_simple EXCLAMATION EQUAL expression_simple
        """
        t[0] = self.builder.build_comparison_expression(t)
    
    def _extend(self):

        self.parser.add_reserved_word('routing_next', 'ROUTING_NEXT', case_sensitive=True)
        self.parser.add_reserved_word('id', 'ID', case_sensitive=True)
        
        self.parser.add_rule(self.expression_conditional)
        self.parser.add_rule(self.expression_tuple)
        self.parser.add_rule(self.expression_tuple_element)
        self.parser.add_rule(self.expression_function_arguments)
        self.parser.add_rule(self.expression_call_function)
        self.parser.add_rule(self.expression_call_id_function)
        self.parser.add_rule(self.expression_call_routing_next_function)
        self.parser.add_rule(self.expression_call_routing_next_argument)
        self.parser.add_rule(self.expression_function_qop_arguments)
        self.parser.add_rule(self.expression_simple)
        self.parser.add_rule(self.expression_comaprison)
        

    