'''
Created on 22-12-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension


class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)

        self.open_blocks_cnt = 0
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_modules_specification(self, t):
        t.lexer.push_state('modules')
        return t

    ##########################################
    #                TOKENS
    ##########################################

    def token_blockopen(self, t):
        r"\{"
        self.open_blocks_cnt += 1
        return t

    def token_blockclose(self, t):
        r"\}"
        self.open_blocks_cnt -= 1
        if self.open_blocks_cnt == 0:
            t.lexer.pop_state()
        return t

    ##########################################
    #                RULES
    ##########################################

    def modules_specification(self, t):
        """
        specification : MODULES_SPECIFICATION BLOCKOPEN modules_specifications_list BLOCKCLOSE
        """
        pass

    def modules_specifications_list(self, t):
        """
        modules_specifications_list : module_specification
                    | modules_specifications_list module_specification
        """
        pass

    def modules_specification_empty(self, t):
        """
        module_specification : empty
        """
        pass

    def _extend(self):
        
        self.parser.add_state('modules', 'inclusive')

        self.parser.add_reserved_word('modules', 'MODULES_SPECIFICATION', func=self.word_modules_specification,)
        self.parser.add_token('BLOCKOPEN', func=self.token_blockopen, states=['modules'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_blockclose, states=['modules'])

        self.parser.add_rule(self.modules_specification)
        self.parser.add_rule(self.modules_specifications_list)
        self.parser.add_rule(self.modules_specification_empty)
