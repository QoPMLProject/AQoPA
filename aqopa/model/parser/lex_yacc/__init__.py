'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.model.parser import ParserException, QoPMLModelParser

    
##########################################
#   EXTENDERS 
##########################################

class LexYaccParserExtension():
    """
    Abstract extenstion of parser (tokens, states, rules, etc.)
    """
    
    def __init__(self):
        self.parser = None       # Extended parser
    
    def _save_parser(self, parser):
        if not self.parser:
            self.parser = parser
    
    def _extend(self):
        raise NotImplementedError()
    
    def extend(self, parser):
        self._save_parser(parser)
        self._extend()

##########################################
#   MODEL PARSER 
##########################################

class LexYaccParser(QoPMLModelParser):
    """
    Parser class
    """
    
    def __init__(self):
        self.tokens = ()         # lex tokens
        self.precedence = []     # lex precedence
        self.states = []         # lex states
        self.reserved_words = {} # lex reserved_words
        
        self.start_symbol = None # grammar starting symbol 
        self.lexer = None        # lex object
        self.yaccer = None       # yacc object
        
        self.extensions = []     # objects that extend parser (instances of LexYaccParserExtension)
        
        self.store = None        # store for built objects
        
        self.syntax_errors = []  # list of syntax errors that occured while parsing
        
        
    def get_syntax_errors(self):
        return self.syntax_errors
    
    def add_extension(self, ext):
        self.extensions.append(ext)
        return self
    
    def set_store(self, store):
        self.store = store
        return self
    
    def build(self, **kwargs):
        if not self.lexer:
            
            for e in self.extensions:
                e.extend(self)
            
            # Build the lexer
            from ply import lex
            self.lexer = lex.lex(object=self, **kwargs)
            # Build the yacc
            import ply.yacc as yacc
            self.yaccer = yacc.yacc(module=self, start=self.start_symbol, **kwargs)
        return self
    
    def parse(self, s):
        self.yaccer.parse(input = s, lexer = self.lexer)
        return self.store
        
    # LEX
    
    t_ignore = " \t"
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        
    def t_error(self, t):
        last_cr = t.lexer.lexdata.rfind('\n',0,t.lexpos)
        if last_cr < 0:
            last_cr = 0
        column = (t.lexpos - last_cr) + 1
        self.syntax_errors.append(("Line [%s:%s, pos:%s]: Illegal character '%s'" % (t.lexer.lineno, column, t.lexer.lexpos, t.value[0])))
        
        next_cr = t.lexer.lexdata.find('\n',t.lexpos)
        if next_cr < 0:
            next_cr = len(t.lexer.lexdata)
        t.lexer.skip(next_cr - t.lexer.lexpos)
        
    def add_state(self, name, state_type):
        if state_type not in ['inclusive', 'exclusive']:
            raise ParserException('Invalid state type State type must be either inclusive or exclusive.')
        self.states.append((name, state_type))
    
    def add_precedence(self, token_name, precedence):
        """
        Adds precedence for token
        """
        self.precedences.append((precedence, token_name))
    
    def add_token(self, name, regex=None, func=None, precedence=None, states=[], include_in_tokens=True):
        """
        Adds new token and saves it in this module. 
        It is needed by 
        """
        
        if include_in_tokens:
            if not name in self.tokens:
                self.tokens += (name,)
        
        field_name = name 
        states_str = '_'.join(states)
        if len(states_str):
            field_name = states_str + '_' + name
        
        if regex and func:
            raise ParserException('Cannot add token with both: regex and function.')
        
        if regex:
            setattr(self, 't_%s' % field_name, regex)
        if func:
            setattr(self, 't_%s' % field_name, func)
            
        if precedence:
            self.add_precedence(name, precedence)
    
    def add_reserved_word(self, word, token, func=None, state='INITIAL', case_sensitive=True):
        """
        Adds token representing reserved word for particular state (INITIAL by default)
        """
        if not token in self.tokens:
            self.tokens += (token,)
        
        if state not in self.reserved_words:
            self.reserved_words[state] = {}
        self.reserved_words[state][word]= (token, func, case_sensitive)
    
    def get_reserved_words(self):
        """
        Returns all reserver words 
        """
        return self.reserved_words
    
    # YACC
    
    def add_rule(self, func):
        setattr(self, 'p_%s' % (func.__name__), func)
    
    def p_error(self, t):
        if not t:
            self.syntax_errors.append("Syntax error 'Unexpected end of file' \n")
        else:
            last_cr = t.lexer.lexdata.rfind('\n',0,t.lexpos)
            if last_cr < 0:
                last_cr = 0
            column = (t.lexpos - last_cr) + 1
            self.syntax_errors.append(("Line [%s:%s, pos: %s]: Syntax error near '%s' \n" % (t.lexer.lineno, column, t.lexer.lexpos, t.value)))
    
