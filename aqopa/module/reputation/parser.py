'''
Created on 01-06-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model import MetricsServiceParam
from aqopa.model.parser.lex_yacc import LexYaccParserExtension


class Builder():
    
    def create_metrics_services_param_reputation(self, token):
        """
        metrics_services_param : SQLPARAN REPUTATION COLON ALGORITHM SQRPARAN
        """
        return MetricsServiceParam(token[2], token[4])


class MetricsParserExtension(LexYaccParserExtension):
    """
    Extension for parsing energy analysis module's metrics
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
        self.builder = Builder()

    ##########################################
    #           RESERVED WORDS
    ##########################################

    def word_reputation(self, t):
        t.lexer.push_state('reputationprimhead')
        return t

    def word_algorithm(self, t):
        t.lexer.pop_state()
        return t

    ##########################################
    #                TOKENS
    ##########################################


    ##########################################
    #                RULES
    ##########################################
    
    def rule_metrics_services_param_reputation(self, t):
        """
        metrics_services_param : SQLPARAN REPUTATION COLON ALGORITHM SQRPARAN
        """
        t[0] = self.builder.create_metrics_services_param_reputation(t)
    
    def _extend(self):
        """ """
        self.parser.add_state('reputationprimhead', 'inclusive')

        self.parser.add_reserved_word('reputation', 'REPUTATION', func=self.word_reputation, state='metricsprimhead',
                                      case_sensitive=True)

        self.parser.add_token('COLON', r':', states=['reputationprimhead'])
        self.parser.add_reserved_word('algorithm', 'ALGORITHM', func=self.word_algorithm, state='reputationprimhead',
                                      case_sensitive=True)

        self.parser.add_rule(self.rule_metrics_services_param_reputation)


class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for parsing energy analysis module's metrics
    """

    def __init__(self, module):
        LexYaccParserExtension.__init__(self)

        self.module = module
        self.builder = Builder()

        self.open_blocks_cnt = 0

    ##########################################
    #                TOKENS
    ##########################################

    def token_reputation(self, t):
        r'reputation'
        t.lexer.push_state('reputation')
        return t

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

    def reputation_specification(self, t):
        """
        module_specification : REPUTATION BLOCKOPEN reputation_init_vars reputation_algorithms BLOCKCLOSE
        """
        pass

    def reputation_algorithms(self, t):
        """
        reputation_algorithms : reputation_algorithm
                            | reputation_algorithms reputation_algorithm
        """
        pass

    def reputation_algorithm(self, t):
        """
        reputation_algorithm : ALGORITHM IDENTIFIER LPARAN identifiers_list RPARAN BLOCKOPEN reputation_instructions BLOCKCLOSE
        """
        self.module.algorithms[t[2]] = {
            'parameters': t[4],
            'instructions': t[7],
        }

    def reputation_init_vars(self, t):
        """
        reputation_init_vars : reputation_init_var
                            | reputation_init_vars reputation_init_var
        """
        pass

    def reputation_init_var(self, t):
        """
        reputation_init_var : HASH IDENTIFIER EQUAL number SEMICOLON
        """
        self.module.init_vars[t[2]] = t[4]

    def reputation_instructions(self, t):
        """
        reputation_instructions : reputation_instruction
                                | reputation_instructions reputation_instruction
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])


    def reputation_instruction(self, t):
        """
        reputation_instruction : reputation_instruction_assignment SEMICOLON
                                | reputation_instruction_conditional
                                | reputation_instruction_conditional SEMICOLON
        """
        t[0] = t[1]

    def reputation_instruction_assignment(self, t):
        """
        reputation_instruction_assignment : IDENTIFIER EQUAL reputation_expression
        """
        t[0] = {'type': 'assignment', 'identifier': t[1], 'expression': t[3]}

    def reputation_expression_operations(self, t):
        """
        reputation_expression : reputation_expression PLUS reputation_expression
                            | reputation_expression MINUS reputation_expression
                            | reputation_expression TIMES reputation_expression
                            | reputation_expression DIVIDE reputation_expression
        """
        t[0] = ''.join(t[1:])

    def reputation_expression_values(self, t):
        """
        reputation_expression : number
                            | IDENTIFIER
        """
        t[0] = str(t[1])

    def reputation_expression_uminus(self, t):
        """
        reputation_expression : MINUS reputation_expression %prec UMINUS
        """
        t[0] = ''.join(t[1:2])

    def reputation_expression_paran(self, t):
        """
        reputation_expression : LPARAN reputation_expression RPARAN
        """
        t[0] = ''.join(t[1:])

    def reputation_instruction_conditional(self, t):
        """
        reputation_instruction_conditional : IF LPARAN reputation_expression_conditional RPARAN BLOCKOPEN reputation_instructions BLOCKCLOSE
                                        | IF LPARAN reputation_expression_conditional RPARAN BLOCKOPEN reputation_instructions BLOCKCLOSE ELSE BLOCKOPEN reputation_instructions BLOCKCLOSE
        """

        if_instruction = {'type': 'if', 'condition': t[3], 'true_instructions': t[6], 'false_instructions': []}
        if len(t) > 8:
            if_instruction['false_instructions'] = t[10]
        t[0] = if_instruction

    def reputation_expression_conditional_comparison(self, t):
        """
        reputation_expression_conditional : reputation_expression EQUAL EQUAL reputation_expression
                                        | reputation_expression EXCLAMATION EQUAL reputation_expression
                                        | reputation_expression GREATER reputation_expression
                                        | reputation_expression GREATER EQUAL reputation_expression
                                        | reputation_expression SMALLER reputation_expression
                                        | reputation_expression SMALLER EQUAL reputation_expression
                                        | reputation_expression_conditional AND AND reputation_expression_conditional
                                        | reputation_expression_conditional OR OR reputation_expression_conditional
        """
        t[0] = ''.join(t[1:])

    def reputation_expression_conditional_operators(self, t):
        """
        reputation_expression_conditional : USED LPARAN IDENTIFIER RPARAN
                                        | EXISTS LPARAN IDENTIFIER RPARAN
        """
        t[0] = ''.join(t[1:])

    def reputation_expression_conditional_paran(self, t):
        """
        reputation_expression_conditional : LPARAN reputation_expression_conditional RPARAN
        """
        t[0] = ''.join(t[1:])

    def _extend(self):
        """ """
        self.parser.add_state('reputation', 'inclusive')

        self.parser.add_token('REPUTATION', func=self.token_reputation, states=['modules'])
        self.parser.add_reserved_word('algorithm', 'ALGORITHM', state='reputation', case_sensitive=True)
        self.parser.add_reserved_word('if', 'IF', state='reputation', case_sensitive=True)
        self.parser.add_reserved_word('else', 'ELSE', state='reputation', case_sensitive=True)
        self.parser.add_reserved_word('used', 'USED', state='reputation', case_sensitive=True)
        self.parser.add_reserved_word('exists', 'EXISTS', state='reputation', case_sensitive=True)

        self.parser.add_token('BLOCKOPEN', func=self.token_blockopen, states=['reputation'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_blockclose, states=['reputation'])

        self.parser.add_token('PLUS', r'\+', states=['reputation'])
        self.parser.add_token('MINUS', r'\-', states=['reputation'])
        self.parser.add_token('TIMES', r'\*', states=['reputation'])
        self.parser.add_token('DIVIDE', r'/', states=['reputation'])

        self.parser.add_token('HASH', r"\#", states=['reputation'])
        self.parser.add_token('GREATER', r'\>', states=['reputation'])
        self.parser.add_token('SMALLER', r'\<', states=['reputation'])
        self.parser.add_token('EXCLAMATION', r'\!', states=['reputation'])
        self.parser.add_token('AND', r'\&', states=['reputation'])
        self.parser.add_token('OR', r'\|', states=['reputation'])

        self.parser.add_precedence(['PLUS', 'MINUS'], 'left')
        self.parser.add_precedence(['TIMES', 'DIVIDE'], 'left')
        self.parser.add_precedence(['UMINUS'], 'right')

        # Rules

        self.parser.add_rule(self.reputation_specification)
        self.parser.add_rule(self.reputation_algorithms)
        self.parser.add_rule(self.reputation_algorithm)
        self.parser.add_rule(self.reputation_init_vars)
        self.parser.add_rule(self.reputation_init_var)
        self.parser.add_rule(self.reputation_instructions)
        self.parser.add_rule(self.reputation_instruction)
        self.parser.add_rule(self.reputation_instruction_assignment)
        self.parser.add_rule(self.reputation_expression_operations)
        self.parser.add_rule(self.reputation_expression_paran)
        self.parser.add_rule(self.reputation_expression_uminus)
        self.parser.add_rule(self.reputation_expression_values)
        self.parser.add_rule(self.reputation_instruction_conditional)
        self.parser.add_rule(self.reputation_expression_conditional_comparison)
        self.parser.add_rule(self.reputation_expression_conditional_operators)
        self.parser.add_rule(self.reputation_expression_conditional_paran)