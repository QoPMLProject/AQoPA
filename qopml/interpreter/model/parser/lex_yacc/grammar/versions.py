'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from qopml.interpreter.model.parser.lex_yacc.parser import LexYaccParserExtension
from qopml.interpreter.model.parser.lex_yacc.builder import LexYaccBuilder
from qopml.interpreter.model import Function, Channel


class Builder(LexYaccBuilder):
    """
    Builder for creating channel objects
    """
    
    def build(self, cls, token):
        """
        channel : CHANNEL identifiers_list LPARAN channel_buffor RPARAN SEMICOLON
        """
        if cls != Channel:
            return []
        
        channels = []
        for name in token[2]:
            buffer_size = token[4]
            if isinstance(buffer_size, str) and buffer_size == "*":
                buffer_size = -1
            channels.append(Channel(name, buffer_size))
        return channels


class ParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_channels_specification(self, t):
        t.lexer.push_state('channels')
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
    
    def channels_specification(self, t):
        """
        specification : CHANNELS_SPECIFICATION BLOCK_OPEN channels_list BLOCK_CLOSE
        """
        pass
    
    
    def channels_list(self, t):
        """
        channels_list : channel 
                    | channels_list channel
        """
        pass
    
    def channel(self, t):
        """
        channel : CHANNEL identifiers_list LPARAN channel_buffor RPARAN SEMICOLON
        """
        for ch in self.parser.builder.build(Channel, t):
            self.parser.store.channels.append(ch)
    
    def channel_buffor(self, t):
        """
        channel_buffor : STAR
            | INTEGER
        """
        t[0] = t[1]
    
    def _extend(self):
        
        self.parser.add_state('channels', 'inclusive')

        self.parser.add_reserved_word('channels', 'CHANNELS_SPECIFICATION', func=self.word_channels_specification)
        self.parser.add_reserved_word('channel', 'CHANNEL', state='channels')

        self.parser.add_token('BLOCK_CLOSE', func=self.token_block_close, states=['channels'])
        

        self.parser.add_rule(self.channels_specification)
        self.parser.add_rule(self.channels_list)
        self.parser.add_rule(self.channel)
        self.parser.add_rule(self.channel_buffor)
        

    