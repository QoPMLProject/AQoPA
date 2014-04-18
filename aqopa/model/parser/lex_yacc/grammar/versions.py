'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import Version, VersionRunProcess, VersionRunHost,\
    MetricsSet


class Builder():
    """
    Builder for creating channel objects
    """
    
    def build_version(self, token):
        """
        version : VERSION IDENTIFIER BLOCKOPEN metrics_sets version_run_hosts BLOCKCLOSE
                | VERSION IDENTIFIER BLOCKOPEN metrics_sets version_run_hosts version_communication BLOCKCLOSE
        """
        v = Version(token[2])
        for metrics_set in token[4]:
            v.metrics_sets.append(metrics_set)
        for run_host in token[5]:
            v.run_hosts.append(run_host)
            
        if len(token) == 8:
            v.communication = token[6]
            
        return v
    
    def create_metrics_set(self, token):
        """
        metrics_set : SET HOST IDENTIFIER LPARAN IDENTIFIER RPARAN SEMICOLON
                | SET HOST IDENTIFIER LPARAN QUALIFIED_IDENTIFIER RPARAN SEMICOLON
        """
        return MetricsSet(token[3], token[5])
    
    def build_run_host(self, token):
        """
        version_run_host : RUN HOST IDENTIFIER version_channels BLOCKOPEN BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition BLOCKOPEN BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCKOPEN BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels BLOCKOPEN version_run_processes BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition BLOCKOPEN version_run_processes BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCKOPEN version_run_processes BLOCKCLOSE
        """
        run_host = VersionRunHost(token[3])
        if '*' in token[4]:
            run_host.all_channels_active = True
        else:
            run_host.active_channels = token[4]
            
        if len(token) == 8:
            
            if isinstance(token[5], int): # RUN HOST IDENTIFIER version_channels version_repetition BLOCKOPEN BLOCKCLOSE
                run_host.repetitions = token[5]
            else: # RUN HOST IDENTIFIER version_channels BLOCKOPEN version_run_processes BLOCKCLOSE
                run_host.run_processes = token[6]
                
        elif len(token) == 9:
            
            if isinstance(token[6], list): # RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCKOPEN BLOCKCLOSE
                run_host.repetitions = token[5]
                run_host.repeated_channels = token[6]
            else: # RUN HOST IDENTIFIER version_channels version_repetition BLOCKOPEN version_run_processes BLOCKCLOSE
                run_host.repetitions = token[5]
                run_host.run_processes = token[7]
            
        elif len(token) == 10:
            run_host.repetitions = token[5]
            run_host.repeated_channels = token[6]
            run_host.run_processes = token[8]
            
            
        return run_host    
    
    def build_run_process(self, token):
        """
        version_run_process : version_run_process_base
                        | version_run_process_base ARROWRIGHT version_run_process_follower
        """
        run_process = token[1]
        if len(token) == 4:
            run_process.follower = token[3]
        return run_process 
    
    def build_run_process_base(self, token):
        """
        version_run_process_base : RUN IDENTIFIER version_subprocesses_list
                                | RUN IDENTIFIER version_subprocesses_list version_repetition
                                | RUN IDENTIFIER version_subprocesses_list version_repetition version_repetition_channels
        """
        run_process = VersionRunProcess(token[2])
        
        if '*' in token[3]:
            run_process.all_subprocesses_active = True
        else:
            for identifier in token[3]:
                run_process.active_subprocesses.append(identifier)
        
        if len(token) > 4:
            run_process.repetitions = token[4]
        
        if len(token) > 5:
            for identifier in token[5]:
                run_process.repeated_channels.append(identifier)
        
        return run_process
    
    def build_run_process_follower(self, token):
        """
        version_run_process_follower : RUN IDENTIFIER version_subprocesses_list
        """
        run_process = VersionRunProcess(token[2])
        
        if '*' in token[3]:
            run_process.all_subprocesses_active = True
        else:
            for identifier in token[3]:
                run_process.active_subprocesses.append(identifier)
        return run_process

class ConfigParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)

        self.open_blocks_cnt = 0
        
        self.builder = Builder()
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_versions_specification(self, t):
        t.lexer.push_state('versions')
        return t
    
    ##########################################
    #                TOKENS
    ##########################################
    
    def token_block_open(self, t):
        r'{'
        self.open_blocks_cnt += 1
        return t
    
    def token_block_close(self, t):
        r'}'
        self.open_blocks_cnt -= 1
        if self.open_blocks_cnt == 0:
            t.lexer.pop_state()
        return t
    
    def token_sq_lparan(self, t):
        r'\['
        t.lexer.push_state('versionsrepeatedchannels')
        return t
    
    def token_sq_rparan(self, t):
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
    
    def versions_specification(self, t):
        """
        specification : VERSIONS_SPECIFICATION BLOCKOPEN versions_list BLOCKCLOSE
        """
        pass
    
    
    def versions_list(self, t):
        """
        versions_list : version 
                    | versions_list version
        """
        pass
    
    def version(self, t):
        """
        version : VERSION IDENTIFIER BLOCKOPEN metrics_sets version_run_hosts BLOCKCLOSE
                | VERSION IDENTIFIER BLOCKOPEN metrics_sets version_run_hosts version_communication BLOCKCLOSE
        """
        self.parser.store.versions.append(self.builder.build_version(t))
    
    def metrics_sets(self, t):
        """
        metrics_sets : metrics_set
                    | metrics_sets metrics_set
        """
        if len(t) == 3:
            t[0] = t[1]
            t[0].append(t[2])
        else:
            t[0] = []
            t[0].append(t[1])
    
    def metrics_set(self, t):
        """
        metrics_set : SET HOST IDENTIFIER LPARAN IDENTIFIER RPARAN SEMICOLON
                | SET HOST IDENTIFIER LPARAN QUALIFIED_IDENTIFIER RPARAN SEMICOLON
        """
        t[0] = self.builder.create_metrics_set(t)
    
    def version_run_hosts(self, t):
        """
        version_run_hosts : version_run_host
                        | version_run_hosts version_run_host
        """
        if len(t) == 3:
            t[0] = t[1]
            t[0].append(t[2])
        else:
            t[0] = []
            t[0].append(t[1])
    
    def version_run_host(self, t):
        """
        version_run_host : RUN HOST IDENTIFIER version_channels BLOCKOPEN BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition BLOCKOPEN BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCKOPEN BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels BLOCKOPEN version_run_processes BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition BLOCKOPEN version_run_processes BLOCKCLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCKOPEN version_run_processes BLOCKCLOSE
        """
        t[0] = self.builder.build_run_host(t)
    
    def version_repetition(self, t):
        """
        version_repetition : BLOCKOPEN INTEGER BLOCKCLOSE
        """
        t[0] = t[2]
    
    def version_channels(self, t):
        """
        version_channels : LPARAN RPARAN
                        | LPARAN STAR RPARAN
                        | LPARAN identifiers_list RPARAN
        """
        if len(t) == 3:
            t[0] = []
        elif len(t) == 4:
            if t[2] == '*':
                t[0] = ['*']
            else:
                t[0] = t[2]
    
    def version_repetition_channels(self, t):
        """
        version_repetition_channels : SQLPARAN version_repetition_channels_list SQRPARAN
        """
        t[0] = t[2]
        
    def version_repetition_channels_list(self, t):
        """
        version_repetition_channels_list : version_repetition_channel
                                        | version_repetition_channels_list COMMA version_repetition_channel
        """
        if len(t) == 4:
            t[0] = t[1]
            t[0].append(t[3])
        else:
            t[0] = []
            t[0].append(t[1])
        
    def version_repetition_channel(self, t):
        """
        version_repetition_channel : QUALIFIED_IDENTIFIER 
                                | IDENTIFIER
        """
        t[0] = t[1]
    
    def version_run_processes(self, t):
        """
        version_run_processes : version_run_process
                            | version_run_processes version_run_process
        """
        if len(t) == 3:
            t[0] = t[1]
            t[0].append(t[2])
        else:
            t[0] = []
            t[0].append(t[1])
    
    def version_run_process(self, t):
        """
        version_run_process : version_run_process_base
                        | version_run_process_base ARROWRIGHT version_run_process_follower
        """
        t[0] = self.builder.build_run_process(t)
    
    def version_run_process_base(self, t):
        """
        version_run_process_base : RUN IDENTIFIER version_subprocesses_list
                                | RUN IDENTIFIER version_subprocesses_list version_repetition
                                | RUN IDENTIFIER version_subprocesses_list version_repetition version_repetition_channels
        """
        t[0] = self.builder.build_run_process_base(t)
    
    def version_run_process_follower(self, t):
        """
        version_run_process_follower : RUN IDENTIFIER version_subprocesses_list
        """
        t[0] = self.builder.build_run_process_follower(t)
    
    def version_subprocesses_list(self, t):
        """
        version_subprocesses_list : LPARAN RPARAN
                        | LPARAN STAR RPARAN
                        | LPARAN identifiers_list RPARAN
        """
        if len(t) == 3:
            t[0] = []
        elif len(t) == 4:
            if t[2] == '*':
                t[0] = ['*']
            else:
                t[0] = t[2]
    
    def _extend(self):
        
        self.parser.add_state('versions', 'inclusive')
        self.parser.add_state('versionsrepeatedchannels', 'exclusive')
        
        self.parser.add_reserved_word('versions', 'VERSIONS_SPECIFICATION', func=self.word_versions_specification)
        self.parser.add_reserved_word('version', 'VERSION', state='versions')
        self.parser.add_reserved_word('run', 'RUN', state='versions')
        self.parser.add_reserved_word('set', 'SET', state='versions')
        self.parser.add_reserved_word('host', 'HOST', state='versions')

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['versions'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['versions'])
        self.parser.add_token('ARROWRIGHT', r'\-\>', states=['versions'])
        
        self.parser.add_token('SQLPARAN', func=self.token_sq_lparan, states=['versions'])
        self.parser.add_token('IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*', states=['versionsrepeatedchannels'])
        self.parser.add_token('QUALIFIED_IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*(\.[0-9][0-9]*)+', 
                              states=['versionsrepeatedchannels'])
        self.parser.add_token('COMMA', r',', states=['versionsrepeatedchannels'])
        self.parser.add_token('SQRPARAN', func=self.token_sq_rparan, states=['versionsrepeatedchannels'])
        
        self.parser.add_token('error', func=self.token_error, states=['versionsrepeatedchannels'], include_in_tokens=False)
        self.parser.add_token('ignore', "\t ", states=['versionsrepeatedchannels'], include_in_tokens=False)
        self.parser.add_token('newline', func=self.t_newline,  states=['versionsrepeatedchannels'], include_in_tokens=False)

        self.parser.add_rule(self.versions_specification)
        self.parser.add_rule(self.versions_list)
        self.parser.add_rule(self.version)
        self.parser.add_rule(self.metrics_sets)
        self.parser.add_rule(self.metrics_set)
        self.parser.add_rule(self.version_run_hosts)
        self.parser.add_rule(self.version_run_host)
        self.parser.add_rule(self.version_repetition)
        self.parser.add_rule(self.version_channels)
        self.parser.add_rule(self.version_repetition_channels)
        self.parser.add_rule(self.version_repetition_channels_list)
        self.parser.add_rule(self.version_repetition_channel)
        self.parser.add_rule(self.version_run_processes)
        self.parser.add_rule(self.version_run_process)
        self.parser.add_rule(self.version_run_process_base)
        self.parser.add_rule(self.version_run_process_follower)
        self.parser.add_rule(self.version_subprocesses_list)
        

    