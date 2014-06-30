'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import re
from aqopa.model.parser.lex_yacc import LexYaccParserExtension

class ModelParserExtension(LexYaccParserExtension):
    
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
        r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9]+)*'


        qualified_regexp = r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9]+)+'
        if re.match(qualified_regexp, t.value):
            t.type = 'QUALIFIED_IDENTIFIER'
            return t

        words = self.parser.get_reserved_words()
        
        states_stack = []
        states_stack.extend(t.lexer.lexstatestack)
        states_stack.append(t.lexer.current_state())
        
        i = len(states_stack)-1
        while i >= 0:
            state = states_stack[i]
            if state in words:
                state_words = words[state]
                for state_word in state_words:
                    
                    tvalue = t.value
                    state_word_value = state_word
                    word_tuple = state_words[state_word]
                    
                    # if not case sensitive
                    if not word_tuple[2]:
                        tvalue = tvalue.lower()
                        state_word_value = state_word_value.lower()
                    
                    if tvalue == state_word_value:
                        # If function exists
                        if word_tuple[1]:
                            t = word_tuple[1](t)
                        t.type = word_tuple[0]
                        break
            i -= 1

        return t

    def token_float(self, t):
        r'([1-9][0-9]*\.[0-9]+)|(0\.[0-9]+)'
        t.value = float(t.value)
        return t
    
    def token_integer(self, t):
        r'0|[1-9][0-9]*'
        t.value = int(t.value)
        return t
    
    def token_comment(self, t):
        r'\%[^\n]*'
        pass
        
    
    ##########################################
    #                RULES
    ##########################################
    
    def rule_model(self, t):
        """
        model : specification 
            | model specification
        """
        pass

    def rule_empty(self, t):
        """
        empty :
        """
        pass

    def rule_number(self, t):
        """
        number : FLOAT
                | INTEGER
        """
        t[0] = t[1]

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

    def rule_qualified_identifiers_list(self, t):
        """
        qualified_identifiers_list : QUALIFIED_IDENTIFIER
                    | qualified_identifiers_list COMMA QUALIFIED_IDENTIFIER
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
        self.parser.add_token('FLOAT', func=self.token_float)
        self.parser.add_token('INTEGER', func=self.token_integer)
        self.parser.add_token('QUALIFIED_IDENTIFIER')
        self.parser.add_token('IDENTIFIER', func=self.token_identifier)
        self.parser.add_token('TEXT', r'[-_A-Za-z0-9 ]+')
        
        self.parser.add_token('SEMICOLON', r';')
        self.parser.add_token('COLON', r':',)
        self.parser.add_token('STAR', r'\*')
        self.parser.add_token('EQUAL', r'\=')
        self.parser.add_token('EXCLAMATION', r'\!')
        self.parser.add_token('PIPE', r'\|')
        
        self.parser.add_token('LPARAN', r'\(')
        self.parser.add_token('RPARAN', r'\)')
        self.parser.add_token('SQLPARAN', r'\[')
        self.parser.add_token('SQRPARAN', r'\]')
        self.parser.add_token('BLOCKOPEN', r'{')
        self.parser.add_token('BLOCKCLOSE', r'}')
        
        self.parser.add_token('COMMENT', self.token_comment, include_in_tokens=False)
        
        self.parser.add_rule(self.rule_model)
        self.parser.add_rule(self.rule_empty)
        self.parser.add_rule(self.rule_number)
        self.parser.add_rule(self.rule_identifiers_list)
        self.parser.add_rule(self.rule_qualified_identifiers_list)
        
        self.parser.start_symbol = 'model'

class MetricsParserExtension(LexYaccParserExtension):
    """
    """
    
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
        r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9]+)*'


        qualified_regexp = r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9]+)+'
        if re.match(qualified_regexp, t.value):
            t.type = 'QUALIFIED_IDENTIFIER'
            return t
        
        words = self.parser.get_reserved_words()
        
        states_stack = []
        states_stack.extend(t.lexer.lexstatestack)
        states_stack.append(t.lexer.current_state())
        
        i = len(states_stack)-1
        while i >= 0:
            state = states_stack[i]
            if state in words:
                state_words = words[state]
                for state_word in state_words:
                    
                    tvalue = t.value
                    state_word_value = state_word
                    word_tuple = state_words[state_word]
                    
                    # if not case sensitive
                    if not word_tuple[2]:
                        tvalue = tvalue.lower()
                        state_word_value = state_word_value.lower()
                    
                    if tvalue == state_word_value:
                        # If function exists
                        if word_tuple[1]:
                            t = word_tuple[1](t)
                        t.type = word_tuple[0]
                        break
            i -= 1
            
        return t

    def token_float(self, t):
        r'([1-9][0-9]*\.[0-9]+)|(0\.[0-9]+)'

        t.value = float(t.value)
        return t
    
    def token_integer(self, t):
        r'0|[1-9][0-9]*'
        
        t.value = int(t.value)
        return t
    
    def token_comment(self, t):
        r'\%[^\n]*'
        pass
        
    
    ##########################################
    #                RULES
    ##########################################
    
    def rule_metrics(self, t):
        """
        metrics : specification
            | metrics specification
        """
        pass

    def rule_empty(self, t):
        """
        empty :
        """
        pass

    def rule_number(self, t):
        """
        number : FLOAT
                | INTEGER
        """
        t[0] = t[1]

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

    def rule_qualified_identifiers_list(self, t):
        """
        qualified_identifiers_list : QUALIFIED_IDENTIFIER
                    | qualified_identifiers_list COMMA QUALIFIED_IDENTIFIER
        """
        if len(t) == 2:
            t[0] = [t[1]]
        else:
            t[0] = t[1]
            t[0].append(t[3])
    
    def _extend(self):
        
        self.parser.add_token('COMMA', r',')
        self.parser.add_token('FLOAT', func=self.token_float)
        self.parser.add_token('INTEGER', func=self.token_integer)
        self.parser.add_token('QUALIFIED_IDENTIFIER')
        self.parser.add_token('IDENTIFIER', func=self.token_identifier)
        self.parser.add_token('TEXT', r'[-_A-Za-z0-9 ]+')
        
        self.parser.add_token('SEMICOLON', r';')
        self.parser.add_token('COLON', r':',)
        self.parser.add_token('STAR', r'\*')
        self.parser.add_token('EQUAL', r'\=')
        
        self.parser.add_token('LPARAN', r'\(')
        self.parser.add_token('RPARAN', r'\)')
        self.parser.add_token('SQLPARAN', r'\[')
        self.parser.add_token('SQRPARAN', r'\]')
        self.parser.add_token('BLOCKOPEN', r'{')
        self.parser.add_token('BLOCKCLOSE', r'}')
        
        self.parser.add_token('COMMENT', self.token_comment, include_in_tokens=False)
        
        self.parser.add_rule(self.rule_metrics)
        self.parser.add_rule(self.rule_empty)
        self.parser.add_rule(self.rule_number)
        self.parser.add_rule(self.rule_identifiers_list)
        self.parser.add_rule(self.rule_qualified_identifiers_list)
        
        self.parser.start_symbol = 'metrics'


class ConfigParserExtension(LexYaccParserExtension):
    """
    """
    
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
        r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9]+)*'


        qualified_regexp = r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9]+)+'
        if re.match(qualified_regexp, t.value):
            t.type = 'QUALIFIED_IDENTIFIER'
            return t
        
        words = self.parser.get_reserved_words()
        
        states_stack = []
        states_stack.extend(t.lexer.lexstatestack)
        states_stack.append(t.lexer.current_state())
        
        i = len(states_stack)-1
        while i >= 0:
            state = states_stack[i]
            if state in words:
                state_words = words[state]
                for state_word in state_words:
                    
                    tvalue = t.value
                    state_word_value = state_word
                    word_tuple = state_words[state_word]
                    
                    # if not case sensitive
                    if not word_tuple[2]:
                        tvalue = tvalue.lower()
                        state_word_value = state_word_value.lower()
                    
                    if tvalue == state_word_value:
                        # If function exists
                        if word_tuple[1]:
                            t = word_tuple[1](t)
                        t.type = word_tuple[0]
                        break
            i -= 1
            
        return t

    def token_float(self, t):
        r'([1-9][0-9]*\.[0-9]+)|(0\.[0-9]+)'

        t.value = float(t.value)
        return t
    
    def token_integer(self, t):
        r'0|[1-9][0-9]*'
        
        t.value = int(t.value)
        return t
    
    def token_comment(self, t):
        r'\%[^\n]*'
        pass
        
    
    ##########################################
    #                RULES
    ##########################################
    
    def rule_configuration(self, t):
        """
        configuration : specification 
            | configuration specification
        """
        pass

    def rule_empty(self, t):
        """
        empty :
        """
        pass

    def rule_number(self, t):
        """
        number : FLOAT
                | INTEGER
        """
        t[0] = t[1]

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

    def rule_qualified_identifiers_list(self, t):
        """
        qualified_identifiers_list : QUALIFIED_IDENTIFIER
                    | qualified_identifiers_list COMMA QUALIFIED_IDENTIFIER
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
        self.parser.add_token('FLOAT', func=self.token_float)
        self.parser.add_token('INTEGER', func=self.token_integer)
        self.parser.add_token('QUALIFIED_IDENTIFIER')
        self.parser.add_token('IDENTIFIER', func=self.token_identifier)
        self.parser.add_token('TEXT', r'[-_A-Za-z0-9 ]+')

        self.parser.add_token('SEMICOLON', r';')
        self.parser.add_token('COLON', r':',)
        self.parser.add_token('STAR', r'\*')
        self.parser.add_token('EQUAL', r'\=')
        
        self.parser.add_token('LPARAN', r'\(')
        self.parser.add_token('RPARAN', r'\)')
        self.parser.add_token('SQLPARAN', r'\[')
        self.parser.add_token('SQRPARAN', r'\]')
        self.parser.add_token('BLOCKOPEN', r'{')
        self.parser.add_token('BLOCKCLOSE', r'}')
        
        self.parser.add_token('COMMENT', self.token_comment, include_in_tokens=False)
        
        self.parser.add_rule(self.rule_configuration)
        self.parser.add_rule(self.rule_empty)
        self.parser.add_rule(self.rule_number)
        self.parser.add_rule(self.rule_identifiers_list)
        self.parser.add_rule(self.rule_qualified_identifiers_list)
        
        self.parser.start_symbol = 'configuration'

