'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from qopml.interpreter.model.parser.lex_yacc.parser import LexYaccParserExtension
import sys

class ParserExtension(LexYaccParserExtension):
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_bool(self, t):
        t.value = bool(t.value)
        return t
    
    ##########################################
    #                TOKENS
    ##########################################
    
    def token_identifier(self, t):
        r'[_a-zA-Z][_a-zA-Z0-9]*'
        
        words = self.parser.get_reserved_words()
        
        states_stack = []
        states_stack.extend(t.lexer.lexstatestack)
        states_stack.append(t.lexer.current_state())
        
         
        i = len(states_stack)-1
        while i >= 0:
            state = states_stack[i]
            if state in words:
                state_words = words[state]
                if t.value in state_words:
                    word = state_words[t.value]
                    # If function exists
                    if word[1]:
                        t = word[1](t)
                    t.type = word[0]
                    break
            i -= 1
            
        return t
    
    def token_integer(self, t):
        r'0|[1-9][0-9]*'
        
        t.value = int(t.value)
        return t
    
    def token_float(self, t):
        r'[1-9][0-9]*(\.[0-9]+)?'
        
        t.value = float(t.value)
        return t
        
    
    ##########################################
    #                RULES
    ##########################################
    
    def rule_model(self, t):
        """
        model : specification 
            | model specification
        """
        pass

    def rule_identifiers_list(self, t):
        """
        identifiers_list : IDENTIFIER
                    | identifiers_list COMMA IDENTIFIER
        """
        if len(t) == 2:
            t[0] = [t[1]]
        else:
            t[0] = t[1]
            t[0].append(t[3])
    
    def _extend(self):
        
        self.parser.add_reserved_word('true', 'BOOL', func=self.word_bool)
        self.parser.add_reserved_word('false', 'BOOL', func=self.word_bool)
        
        self.parser.add_token('COMMA', r',')
        self.parser.add_token('INTEGER', func=self.token_integer)
        self.parser.add_token('FLOAT', func=self.token_float)
        self.parser.add_token('QUALIFIED_IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*(\.[1-9][0-9]*)+')
        #add_token('BIT_MULTIPLIER', r'[kmg]?(bits|bytes)')
        self.parser.add_token('IDENTIFIER', func=self.token_identifier)
        self.parser.add_token('TEXT', r'[-_A-Za-z0-9 ]+')  
        
        self.parser.add_token('SEMICOLON', r';')
        self.parser.add_token('COLON', r':',)
        self.parser.add_token('STAR', r'\*')
        self.parser.add_token('EQUAL', r'\=')
        
        self.parser.add_token('LPARAN', r'\(')
        self.parser.add_token('RPARAN', r'\)')
        self.parser.add_token('SQ_LPARAN', r'\[')
        self.parser.add_token('SQ_RPARAN', r'\]')
        self.parser.add_token('BLOCK_OPEN', r'{')
        self.parser.add_token('BLOCK_CLOSE', r'}')
        
        self.parser.add_rule(self.rule_model)
        self.parser.add_rule(self.rule_identifiers_list)
        
        self.parser.start_symbol = 'model'

