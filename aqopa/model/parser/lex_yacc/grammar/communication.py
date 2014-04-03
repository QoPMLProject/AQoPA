'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import Channel


class Builder():
    """
    Builder for store objects
    """
    
    pass


class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        self.builder = Builder()
        self.open_blocks_cnt = 0

    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_communication_specification(self, t):
        t.lexer.push_state('communication')
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
    
    def communication_specification(self, t):
        """
        specification : COMMUNICATION_SPECIFICATION BLOCKOPEN comm_specifications BLOCKCLOSE
        """
        pass
    
    
    def comm_specifications(self, t):
        """
        comm_specifications : comm_specification
                    | comm_specifications comm_specification
        """
        pass
    
    def topology_specification(self, t):
        """
        comm_specification : TOPOLOGY_SPECIFICATION SQLPARAN IDENTIFIER SQRPARAN BLOCKOPEN topology_rules_list BLOCKCLOSE
        """
        pass

    def topology_rules_list(self, t):
        """
        topology_rules_list : topology_rule
                        | topology_rules_list topology_rule
        """
        pass

    def topology_rule(self, t):
        """
        topology_rule : IDENTIFIER topology_arrow IDENTIFIER SEMICOLON
                    | IDENTIFIER topology_arrow IDENTIFIER COLON FLOAT SEMICOLON
        """
        pass

    def topology_arrow(self, t):
        """
        topology_arrow : ARROWRIGHT
            | ARROWLEFT
            | ARROWBOTH
        """
        pass

    def algoriths_specification(self, t):
        """
        comm_specification : ALGORITHMS_SPECIFICATION BLOCKOPEN comm_algorithms_list BLOCKCLOSE
        """
        pass

    def comm_algorithms_list(self, t):
        """
        comm_algorithms_list : comm_algorithm
                        | comm_algorithms_list comm_algorithm
        """
        pass

    def comm_algorithm(self, t):
        """
        comm_algorithm : ALGORITHM IDENTIFIER LPARAN IDENTIFIER RPARAN BLOCKOPEN comm_algorithm_instructions BLOCKCLOSE
        """
        pass

    def comm_algorithm_instructions(self, t):
        """
        comm_algorithm_instructions : comm_algorithm_instruction
                                | comm_algorithm_instructions comm_algorithm_instruction
        """
        pass

    def comm_algorithm_instruction(self, t):
        """
        comm_algorithm_instruction : comm_algorithm_instruction_assignment SEMICOLON
                            | comm_algorithm_instruction_return SEMICOLON
                            | comm_algorithm_instruction_if
                            | comm_algorithm_instruction_while
        """
        pass

    def comm_algorithm_instruction_assignment(self, t):
        """
        comm_algorithm_instruction_assignment : IDENTIFIER EQUAL comm_algorithm_expression
        """
        pass

    def comm_algorithm_instruction_return(self, t):
        """
        comm_algorithm_instruction_return : RETURN comm_algorithm_expression
        """
        pass

    def comm_algorithm_instruction_if(self, t):
        """
        comm_algorithm_instruction_if : IF LPARAN comm_algorithm_expression_conditional RPARAN BLOCKOPEN comm_algorithm_instructions BLOCKCLOSE
            | IF LPARAN comm_algorithm_expression_conditional RPARAN BLOCKOPEN comm_algorithm_instructions BLOCKCLOSE ELSE BLOCKOPEN comm_algorithm_instructions BLOCKCLOSE
        """
        pass

    def comm_algorithm_instruction_while(self, t):
        """
        comm_algorithm_instruction_while : WHILE LPARAN comm_algorithm_expression_conditional RPARAN BLOCKOPEN comm_algorithm_instructions BLOCKCLOSE
        """
        pass

    def comm_algorithm_expression_conditional_comparison(self, t):
        """
        comm_algorithm_expression_conditional : comm_algorithm_expression EQUAL EQUAL comm_algorithm_expression
                                        | comm_algorithm_expression EXCLAMATION EQUAL comm_algorithm_expression
                                        | comm_algorithm_expression GREATER comm_algorithm_expression
                                        | comm_algorithm_expression GREATER EQUAL comm_algorithm_expression
                                        | comm_algorithm_expression SMALLER comm_algorithm_expression
                                        | comm_algorithm_expression SMALLER EQUAL comm_algorithm_expression
                                        | comm_algorithm_expression_conditional AND AND comm_algorithm_expression_conditional
                                        | comm_algorithm_expression_conditional OR OR comm_algorithm_expression_conditional
        """
        pass

    def comm_algorithm_expression_conditional_paran(self, t):
        """
        comm_algorithm_expression_conditional : LPARAN comm_algorithm_expression_conditional RPARAN
        """
        pass

    def comm_algorithm_expression_simple(self, t):
        """
        comm_algorithm_expression : number
                            | IDENTIFIER
        """
        pass

    def comm_algorithm_expression_uminus(self, t):
        """
        comm_algorithm_expression : COMM_MINUS comm_algorithm_expression %prec COMM_UMINUS
        """
        pass

    def comm_algorithm_expression_paran(self, t):
        """
        comm_algorithm_expression : LPARAN comm_algorithm_expression RPARAN
        """
        pass

    def comm_algorithm_expression_operations(self, t):
        """
        comm_algorithm_expression : comm_algorithm_expression COMM_PLUS comm_algorithm_expression
                            | comm_algorithm_expression COMM_MINUS comm_algorithm_expression
                            | comm_algorithm_expression COMM_TIMES comm_algorithm_expression
                            | comm_algorithm_expression COMM_DIVIDE comm_algorithm_expression
        """
        pass

    def comm_algorithm_expression_function(self, t):
        """
        comm_algorithm_expression : QUALITY LPARAN RPARAN
                                | SIZE LPARAN IDENTIFIER RPARAN
                                | SIZE LPARAN IDENTIFIER SQLPARAN INTEGER SQRPARAN RPARAN
        """
        pass
    
    def _extend(self):
        
        self.parser.add_state('communication', 'inclusive')

        self.parser.add_reserved_word('communication', 'COMMUNICATION_SPECIFICATION',
                                      func=self.word_communication_specification)
        self.parser.add_reserved_word('topology', 'TOPOLOGY_SPECIFICATION', state='communication',)
        self.parser.add_reserved_word('algorithms', 'ALGORITHMS_SPECIFICATION', state='communication')
        self.parser.add_reserved_word('alg', 'ALGORITHM', state='communication')
        self.parser.add_reserved_word('if', 'IF', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('while', 'WHILE', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('else', 'ELSE', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('quality', 'QUALITY', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('size', 'SIZE', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('return', 'RETURN', state='communication', case_sensitive=True)

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['communication'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['communication'])
        self.parser.add_token('ARROWRIGHT', r'\-\>', states=['communication'])
        self.parser.add_token('ARROWLEFT', r'\<\-', states=['communication'])
        self.parser.add_token('ARROWBOTH', r'\<\-\>', states=['communication'])

        self.parser.add_token('COMM_PLUS', r'\+', states=['communication'])
        self.parser.add_token('COMM_MINUS', r'\-', states=['communication'])
        self.parser.add_token('COMM_TIMES', r'\*', states=['communication'])
        self.parser.add_token('COMM_DIVIDE', r'/', states=['communication'])

        self.parser.add_token('GREATER', r'\>', states=['communication'])
        self.parser.add_token('SMALLER', r'\<', states=['communication'])
        self.parser.add_token('EXCLAMATION', r'\!', states=['communication'])
        self.parser.add_token('AND', r'\&', states=['communication'])
        self.parser.add_token('OR', r'\|', states=['communication'])

        self.parser.add_rule(self.communication_specification)
        self.parser.add_rule(self.comm_specifications)
        self.parser.add_rule(self.topology_specification)
        self.parser.add_rule(self.topology_rules_list)
        self.parser.add_rule(self.topology_rule)
        self.parser.add_rule(self.topology_arrow)
        self.parser.add_rule(self.algoriths_specification)
        self.parser.add_rule(self.comm_algorithms_list)
        self.parser.add_rule(self.comm_algorithm)
        self.parser.add_rule(self.comm_algorithm_instructions)
        self.parser.add_rule(self.comm_algorithm_instruction)
        self.parser.add_rule(self.comm_algorithm_instruction_assignment)
        self.parser.add_rule(self.comm_algorithm_instruction_return)
        self.parser.add_rule(self.comm_algorithm_instruction_if)
        self.parser.add_rule(self.comm_algorithm_instruction_while)
        self.parser.add_rule(self.comm_algorithm_expression_conditional_comparison)
        self.parser.add_rule(self.comm_algorithm_expression_conditional_paran)
        self.parser.add_rule(self.comm_algorithm_expression_simple)
        self.parser.add_rule(self.comm_algorithm_expression_uminus)
        self.parser.add_rule(self.comm_algorithm_expression_paran)
        self.parser.add_rule(self.comm_algorithm_expression_operations)
        self.parser.add_rule(self.comm_algorithm_expression_function)

        self.parser.add_precedence(['COMM_PLUS', 'COMM_MINUS'], 'left')
        self.parser.add_precedence(['COMM_TIMES', 'COMM_DIVIDE'], 'left')
        self.parser.add_precedence(['COMM_UMINUS'], 'right')


class ConfigParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        self.builder = Builder()
        self.open_blocks_cnt = 0

    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_communication_specification(self, t):
        t.lexer.push_state('versioncommunication')
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
    
    def version_communication(self, t):
        """
        version_communication : COMMUNICATION_SPECIFICATION BLOCKOPEN version_comm_specifications BLOCKCLOSE
        """
        pass
    
    
    def version_comm_specifications(self, t):
        """
        version_comm_specifications : version_comm_specification
                    | version_comm_specifications version_comm_specification
        """
        pass
    
    def version_topology_specification(self, t):
        """
        version_comm_specification : TOPOLOGY_SPECIFICATION SQLPARAN IDENTIFIER SQRPARAN BLOCKOPEN version_topology_rules_list BLOCKCLOSE
        """
        pass

    def version_topology_rules_list(self, t):
        """
        version_topology_rules_list : version_topology_rule
                        | version_topology_rules_list version_topology_rule
        """
        pass

    def version_topology_rule(self, t):
        """
        version_topology_rule : IDENTIFIER version_topology_arrow IDENTIFIER SEMICOLON
                    | IDENTIFIER version_topology_arrow IDENTIFIER COLON FLOAT SEMICOLON
                    | version_topology_host_with_indicies version_topology_arrow IDENTIFIER SEMICOLON
                    | version_topology_host_with_indicies version_topology_arrow IDENTIFIER COLON FLOAT SEMICOLON
                    | IDENTIFIER version_topology_arrow version_topology_host_with_indicies SEMICOLON
                    | IDENTIFIER version_topology_arrow version_topology_host_with_indicies COLON FLOAT SEMICOLON
                    | version_topology_host_with_indicies version_topology_arrow version_topology_host_with_indicies SEMICOLON
                    | version_topology_host_with_indicies version_topology_arrow version_topology_host_with_indicies COLON FLOAT SEMICOLON
                    | IDENTIFIER version_topology_arrow version_topology_host_with_i_index SEMICOLON
                    | version_topology_host_with_indicies version_topology_arrow version_topology_host_with_i_index SEMICOLON
        """
        pass
    
    def version_topology_host_with_indicies(self, t):
        """
        version_topology_host_with_indicies : IDENTIFIER SQLPARAN INTEGER SQRPARAN
                | IDENTIFIER SQLPARAN INTEGER COLON SQRPARAN
                | IDENTIFIER SQLPARAN COLON INTEGER SQRPARAN
                | IDENTIFIER SQLPARAN INTEGER COLON INTEGER SQRPARAN
        """
        pass
    
    def version_topology_host_with_i_index(self, t):
        """
        version_topology_host_with_i_index : IDENTIFIER SQLPARAN I_INDEX SQRPARAN
                | IDENTIFIER SQLPARAN I_INDEX COMM_PLUS INTEGER SQRPARAN
                | IDENTIFIER SQLPARAN I_INDEX COMM_MINUS INTEGER SQRPARAN
        """
        pass
        

    def version_topology_arrow(self, t):
        """
        version_topology_arrow : ARROWRIGHT
            | ARROWLEFT
            | ARROWBOTH
        """
        pass

    
    def _extend(self):
        
        self.parser.add_state('versioncommunication', 'inclusive')

        self.parser.add_reserved_word('communication', 'COMMUNICATION_SPECIFICATION',
                                      func=self.word_communication_specification)
        self.parser.add_reserved_word('topology', 'TOPOLOGY_SPECIFICATION', state='versioncommunication',)
        self.parser.add_reserved_word('i', 'I_INDEX', state='versioncommunication')

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['versioncommunication'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['versioncommunication'])
        self.parser.add_token('ARROWRIGHT', r'\-\>', states=['versioncommunication'])
        self.parser.add_token('ARROWLEFT', r'\<\-', states=['versioncommunication'])
        self.parser.add_token('ARROWBOTH', r'\<\-\>', states=['versioncommunication'])

        self.parser.add_token('COMM_PLUS', r'\+', states=['versioncommunication'])
        self.parser.add_token('COMM_MINUS', r'\-', states=['versioncommunication'])


        self.parser.add_rule(self.version_communication)
        self.parser.add_rule(self.version_comm_specifications)
        self.parser.add_rule(self.version_topology_specification)
        self.parser.add_rule(self.version_topology_rules_list)
        self.parser.add_rule(self.version_topology_rule)
        self.parser.add_rule(self.version_topology_host_with_indicies)
        self.parser.add_rule(self.version_topology_host_with_i_index)
        self.parser.add_rule(self.version_topology_arrow)



    