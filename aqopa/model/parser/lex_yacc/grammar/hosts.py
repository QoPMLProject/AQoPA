'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import Host, HostProcess
from ply.lex import Lexer
import re


class Builder():
    """
    Builder for creating channel objects
    """
    
    def build_host(self, token):
        """
        host : HOST IDENTIFIER LPARAN host_schedule_algorithm RPARAN host_channels BLOCKOPEN host_body BLOCKCLOSE
            | HOST IDENTIFIER LPARAN host_schedule_algorithm RPARAN host_channels BLOCKOPEN host_predefined_values host_body BLOCKCLOSE
        """
        
        all_channels_active = '*' in token[6]
        
        instructions_list = []
        predefined_values = []
        
        if len(token) == 10:
            instructions_list = token[8]
        elif len(token) == 11:
            predefined_values = token[8]
            instructions_list = token[9]
        
        h = Host(token[2], token[4], instructions_list, predefined_values)
        
        if all_channels_active:
            h.all_channels_active = True
        else:
            h.active_channels = token[6]
        
        return h
    
    def build_process(self, token):
        """
        host_process : PROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE
                    | PROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
        """
        p = HostProcess(token[2], token[5])
        
        all_channels_active = '*' in token[3]
        if all_channels_active:
            p.all_channels_active = True
        else:
            p.active_channels = token[3]
        
        return p
        
class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)

        self.open_blocks_cnt_by_state = {}
        
        self.builder = Builder()
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_hosts_specification(self, t):
        t.lexer.push_state('hosts')
        return t
    
    def word_host_specification(self, t):
        t.lexer.push_state('host')
        return t
    
    def word_process_specification(self, t):
        t.lexer.push_state('process')
        return t
    
    ##########################################
    #                TOKENS
    ##########################################
    
    def token_block_open(self, t):
        r'{'
        state = t.lexer.current_state()
        if state not in self.open_blocks_cnt_by_state:
            self.open_blocks_cnt_by_state[state] = 0 
        self.open_blocks_cnt_by_state[state] += 1
        return t
    
    def token_block_close(self, t):
        r'}'
        state = t.lexer.current_state()
        self.open_blocks_cnt_by_state[state] -= 1
        if self.open_blocks_cnt_by_state[state] == 0:
            t.lexer.pop_state()
        return t
    
    def token_host_rparan(self, t):
        r'\)'
        t.lexer.push_state('hostrparan')
        return t
    
    def token_host_sq_lparan(self, t):
        r'\['
        t.lexer.pop_state()
        t.lexer.push_state('functionqopargs')
        return t
    
    def token_host_any_char(self, t):
        r"."
        t.lexer.pop_state()
        t.lexer.skip(-1)
        
    def token_qop_sq_rparan(self, t):
        r'\]'
        t.lexer.pop_state()
        return t
    
    def token_error(self, t):
        self.parser.t_error(t)
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        
    ##########################################
    #                RULES
    ##########################################
    
    def hosts_specification(self, t):
        """
        specification : HOSTS_SPECIFICATION BLOCKOPEN hosts_list BLOCKCLOSE
        """
        pass
    
    def hosts_list(self, t):
        """
        hosts_list : host
                    | hosts_list host
        """
        pass
    
    def host(self, t):
        """
        host : HOST IDENTIFIER LPARAN host_schedule_algorithm RPARAN host_channels BLOCKOPEN host_body BLOCKCLOSE
            | HOST IDENTIFIER LPARAN host_schedule_algorithm RPARAN host_channels BLOCKOPEN host_predefined_values host_body BLOCKCLOSE
        """
        self.parser.store.hosts.append(self.builder.build_host(t))
    
    def host_schedule_algorithm(self, t):
        """
        host_schedule_algorithm : ROUND_ROBIN
                                | FIFO
        """
        t[0] = t[1]
    
    def host_channels(self, t):
        """
        host_channels : LPARAN RPARAN
                        | LPARAN STAR RPARAN
                        | LPARAN identifiers_list RPARAN
        """
        if len(t) == 2:
            t[0] = []
        elif len(t) == 2:
            t[0] = ['*']
        elif len(t) > 2:
            t[0] = t[2]
            
    def host_predefined_values(self, t):
        """
        host_predefined_values : host_predefined_value
                            | host_predefined_values host_predefined_value
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
    
    def host_predefined_value(self, t):
        """
        host_predefined_value : HASH instruction_assignment
        """
        t[0] = t[2]
    
    def host_body(self, t):
        """
        host_body : host_process
                    | host_body host_process
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
        
    def host_process(self, t):
        """
        host_process : PROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE
                    | PROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
        """
        t[0] = self.builder.build_process(t)
    
    def _extend(self):
        
        self.parser.add_state('hosts', 'inclusive')
        self.parser.add_state('host', 'inclusive')
        self.parser.add_state('process', 'inclusive')
        
        self.parser.add_state('hostrparan', 'exclusive')
        self.parser.add_state('functionqopargs', 'exclusive')
        
        self.parser.add_reserved_word('hosts', 'HOSTS_SPECIFICATION', func=self.word_hosts_specification)
        self.parser.add_reserved_word('host', 'HOST', func=self.word_host_specification, state='hosts')
        self.parser.add_reserved_word('process', 'PROCESS', func=self.word_process_specification, state='host')

        self.parser.add_reserved_word('rr', 'ROUND_ROBIN', state='host')
        self.parser.add_reserved_word('fifo', 'FIFO', state='host')
        
        self.parser.add_reserved_word('in', 'IN', state='host')
        self.parser.add_reserved_word('out', 'OUT', state='host')
        self.parser.add_reserved_word('while', 'WHILE', state='host')
        self.parser.add_reserved_word('if', 'IF', state='host')
        self.parser.add_reserved_word('else', 'ELSE', state='host')
        self.parser.add_reserved_word('continue', 'CONTINUE', state='host')
        self.parser.add_reserved_word('break', 'BREAK', state='host')
        self.parser.add_reserved_word('stop', 'STOP', state='host')
        self.parser.add_reserved_word('end', 'END', state='host')

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['hosts', 'host', 'process'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['hosts', 'host', 'process'])
        self.parser.add_token('HASH', r'\#', states=['host'])
        
        self.parser.add_token('RPARAN', func=self.token_host_rparan, states=['host', 'process'])
        self.parser.add_token('SQLPARAN', func=self.token_host_sq_lparan, states=['hostrparan'])
        self.parser.add_token('ANYCHAR', func=self.token_host_any_char, states=['hostrparan'], include_in_tokens=False)
        
        self.parser.add_token('error', func=self.token_error, states=['hostrparan'], include_in_tokens=False)
        self.parser.add_token('ignore', "\t", states=['hostrparan'], include_in_tokens=False)
        self.parser.add_token('newline', func=self.t_newline,  states=['hostrparan'], include_in_tokens=False)
        
        self.parser.add_token('error', func=self.token_error, states=['functionqopargs'], include_in_tokens=False)
        self.parser.add_token('ignore', "\t", states=['functionqopargs'], include_in_tokens=False)
        self.parser.add_token('newline', func=self.t_newline,  states=['functionqopargs'], include_in_tokens=False)
        
        self.parser.add_token('SQRPARAN', func=self.token_qop_sq_rparan, states=['functionqopargs'])
        self.parser.add_token('COMMA', r'\,', states=['functionqopargs'])
        self.parser.add_token('TEXT', r'[-_A-Za-z0-9 ]+', states=['functionqopargs'])

        self.parser.add_rule(self.hosts_specification)
        self.parser.add_rule(self.hosts_list)
        self.parser.add_rule(self.host)
        self.parser.add_rule(self.host_schedule_algorithm)
        self.parser.add_rule(self.host_channels)
        self.parser.add_rule(self.host_predefined_values)
        self.parser.add_rule(self.host_predefined_value)
        self.parser.add_rule(self.host_body)
        self.parser.add_rule(self.host_process)
        

    