'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import Channel


class Builder():
    """
    Builder for creating channel objects
    """
    
    def build_channels(self, token):
        """
        channel : CHANNEL identifiers_list LPARAN channel_buffor RPARAN SEMICOLON
            | CHANNEL identifiers_list LPARAN channel_buffor RPARAN SQLPARAN IDENTIFIER SQRPARAN SEMICOLON
        """
        tag_name = token[7] if len(token) == 10 else None
        channels = []
        for name in token[2]:
            buffer_size = token[4]
            if (isinstance(buffer_size, str) or isinstance(buffer_size, unicode)) \
                and buffer_size == "*":
                buffer_size = -1
            channels.append(Channel(name, buffer_size, tag_name))
        return channels


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
        specification : CHANNELS_SPECIFICATION BLOCKOPEN channels_list BLOCKCLOSE
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
            | CHANNEL identifiers_list LPARAN channel_buffor RPARAN SQLPARAN IDENTIFIER SQRPARAN SEMICOLON
        """
        for ch in self.builder.build_channels(t):
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

        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['channels'])
        
        self.parser.add_rule(self.channels_specification)
        self.parser.add_rule(self.channels_list)
        self.parser.add_rule(self.channel)
        self.parser.add_rule(self.channel_buffor)
        

    