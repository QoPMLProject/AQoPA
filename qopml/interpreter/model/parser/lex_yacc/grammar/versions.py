'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from qopml.interpreter.model.parser.lex_yacc.parser import LexYaccParserExtension


class Builder():
    """
    Builder for creating channel objects
    """
    
    def build_version(self, token):
        """
        """
        pass

class ParserExtension(LexYaccParserExtension):
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
    
    ##########################################
    #                RULES
    ##########################################
    
    def versions_specification(self, t):
        """
        specification : VERSIONS_SPECIFICATION BLOCK_OPEN versions_list BLOCK_CLOSE
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
        version : VERSION INTEGER BLOCK_OPEN version_run_hosts BLOCK_CLOSE
        """
        pass
    
    def version_run_hosts(self, t):
        """
        version_run_hosts : version_run_host
                        | version_run_hosts version_run_host
        """
        pass
    
    def version_run_host(self, t):
        """
        version_run_host : RUN HOST IDENTIFIER version_channels BLOCK_OPEN BLOCK_CLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition BLOCK_OPEN BLOCK_CLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCK_OPEN BLOCK_CLOSE
                        | RUN HOST IDENTIFIER version_channels BLOCK_OPEN version_run_processes BLOCK_CLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition BLOCK_OPEN version_run_processes BLOCK_CLOSE
                        | RUN HOST IDENTIFIER version_channels version_repetition version_repetition_channels BLOCK_OPEN version_run_processes BLOCK_CLOSE
        """
        pass
    
    def version_repetition(self, t):
        """
        version_repetition : BLOCK_OPEN INTEGER BLOCK_CLOSE
        """
        pass
    
    def version_channels(self, t):
        """
        version_channels : LPARAN RPARAN
                        | LPARAN STAR RPARAN
                        | LPARAN identifiers_list RPARAN
        """
        pass
    
    def version_repetition_channels(self, t):
        """
        version_repetition_channels : SQ_LPARAN qualified_identifiers_list SQ_RPARAN
        """
        pass
    
    def version_run_processes(self, t):
        """
        version_run_processes : version_run_process
                            | version_run_processes version_run_process
        """
        pass
    
    def version_run_process(self, t):
        """
        version_run_process : version_run_process_base
                        | version_run_process_base ARROW_RIGHT version_run_process_follower
        """
        pass
    
    def version_run_process_base(self, t):
        """
        version_run_process_base : RUN IDENTIFIER version_subprocesses_list
                                | RUN IDENTIFIER version_subprocesses_list version_repetition
                                | RUN IDENTIFIER version_subprocesses_list version_repetition version_repetition_channels
        """
        pass
    
    def version_run_process_follower(self, t):
        """
        version_run_process_follower : RUN IDENTIFIER version_subprocesses_list
        """
        pass
    
    def version_subprocesses_list(self, t):
        """
        version_subprocesses_list : LPARAN RPARAN
                        | LPARAN STAR RPARAN
                        | LPARAN identifiers_list RPARAN
        """
    
    def _extend(self):
        
        self.parser.add_state('versions', 'inclusive')
        
        self.parser.add_reserved_word('versions', 'VERSIONS_SPECIFICATION', func=self.word_versions_specification)
        self.parser.add_reserved_word('version', 'VERSION', state='versions')
        self.parser.add_reserved_word('run', 'RUN', state='versions')
        self.parser.add_reserved_word('host', 'HOST', state='versions')

        self.parser.add_token('BLOCK_OPEN', func=self.token_block_open, states=['versions'])
        self.parser.add_token('BLOCK_CLOSE', func=self.token_block_close, states=['versions'])
        self.parser.add_token('ARROW_RIGHT', r'\-\>', states=['versions'])

        self.parser.add_rule(self.versions_specification)
        self.parser.add_rule(self.versions_list)
        self.parser.add_rule(self.version)
        self.parser.add_rule(self.version_run_hosts)
        self.parser.add_rule(self.version_run_host)
        self.parser.add_rule(self.version_repetition)
        self.parser.add_rule(self.version_channels)
        self.parser.add_rule(self.version_repetition_channels)
        self.parser.add_rule(self.version_run_processes)
        self.parser.add_rule(self.version_run_process)
        self.parser.add_rule(self.version_run_process_base)
        self.parser.add_rule(self.version_run_process_follower)
        self.parser.add_rule(self.version_subprocesses_list)
        

    