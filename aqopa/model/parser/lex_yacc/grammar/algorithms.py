'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import AlgWhile, AlgCallFunction, AlgIf, AlgReturn, AlgAssignment


class Builder():
    """
    Builder for store objects
    """
    


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
    
    def word_algorithms_specification(self, t):
        t.lexer.push_state('algorithms')
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
    
    def algorithms_specification(self, t):
        """
        specification : ALGORITHMS_SPECIFICATION BLOCKOPEN algorithms_list BLOCKCLOSE
        """
        pass

    def algorithms_list(self, t):
        """
        algorithms_list : algorithm
                        | algorithms_list algorithm
        """
        pass

    def algorithm(self, t):
        """
        algorithm : ALGORITHM IDENTIFIER LPARAN IDENTIFIER RPARAN BLOCKOPEN algorithm_instructions BLOCKCLOSE
        """
        self.parser.store.algorithms[t[2]] = {'parameter': t[4], 'instructions': t[7]}

    def algorithm_instructions(self, t):
        """
        algorithm_instructions : algorithm_instruction
                                | algorithm_instructions algorithm_instruction
        """
        if len(t) == 3:
            t[0] = t[1]
            t[0].append(t[2])
        else:
            t[0] = []
            t[0].append(t[1])

    def algorithm_instruction(self, t):
        """
        algorithm_instruction : algorithm_instruction_assignment SEMICOLON
                            | algorithm_instruction_return SEMICOLON
                            | algorithm_instruction_if
                            | algorithm_instruction_while
        """
        t[0] = t[1]

    def algorithm_instruction_assignment(self, t):
        """
        algorithm_instruction_assignment : IDENTIFIER EQUAL algorithm_expression
        """
        t[0] = AlgAssignment(identifier=t[1], expression=t[3])

    def algorithm_instruction_return(self, t):
        """
        algorithm_instruction_return : RETURN algorithm_expression
        """
        t[0] = AlgReturn(expression=t[2])

    def algorithm_instruction_if(self, t):
        """
        algorithm_instruction_if : IF LPARAN algorithm_expression_conditional RPARAN BLOCKOPEN algorithm_instructions BLOCKCLOSE
            | IF LPARAN algorithm_expression_conditional RPARAN BLOCKOPEN algorithm_instructions BLOCKCLOSE ELSE BLOCKOPEN algorithm_instructions BLOCKCLOSE
        """
        if len(t) == 8:
            t[0] = AlgIf(condition=t[3], true_instructions=t[6], false_instructions=[])
        else:
            t[0] = AlgIf(condition=t[3], true_instructions=t[6], false_instructions=t[10])

    def algorithm_instruction_while(self, t):
        """
        algorithm_instruction_while : WHILE LPARAN algorithm_expression_conditional RPARAN BLOCKOPEN algorithm_instructions BLOCKCLOSE
        """
        t[0] = AlgWhile(condition=t[3], instructions=t[6])

    def algorithm_expression_conditional_comparison(self, t):
        """
        algorithm_expression_conditional : algorithm_expression EQUAL EQUAL algorithm_expression
                                        | algorithm_expression EXCLAMATION EQUAL algorithm_expression
                                        | algorithm_expression GREATER algorithm_expression
                                        | algorithm_expression GREATER EQUAL algorithm_expression
                                        | algorithm_expression SMALLER algorithm_expression
                                        | algorithm_expression SMALLER EQUAL algorithm_expression
                                        | algorithm_expression_conditional AND AND algorithm_expression_conditional
                                        | algorithm_expression_conditional OR OR algorithm_expression_conditional
        """
        t[0] = t[1]
        sign = t[2]
        if len(t) == 5:
            sign += t[3]
            t[0].append(sign)
            t[0].extend(t[4])
        else:
            t[0].append(sign)
            t[0].extend(t[3])

    def algorithm_expression_conditional_paran(self, t):
        """
        algorithm_expression_conditional : LPARAN algorithm_expression_conditional RPARAN
        """
        t[0] = t[2]
        t[0].prepend('(')
        t[0].append(')')

    def algorithm_expression_simple(self, t):
        """
        algorithm_expression : number
                            | IDENTIFIER
        """
        t[0] = [t[1]]

    def algorithm_expression_uminus(self, t):
        """
        algorithm_expression : MINUS algorithm_expression %prec UMINUS
        """
        t[0] = t[2]
        t[0].prepend('--')

    def algorithm_expression_paran(self, t):
        """
        algorithm_expression : LPARAN algorithm_expression RPARAN
        """
        t[0] = t[2]
        t[0].prepend('(')
        t[0].append(')')

    def algorithm_expression_operations(self, t):
        """
        algorithm_expression : algorithm_expression PLUS algorithm_expression
                            | algorithm_expression MINUS algorithm_expression
                            | algorithm_expression TIMES algorithm_expression
                            | algorithm_expression DIVIDE algorithm_expression
        """
        t[0] = t[1]
        t[0].append(t[2])
        t[0].extend(t[3])

    def algorithm_expression_function(self, t):
        """
        algorithm_expression : QUALITY LPARAN RPARAN
                                | SIZE LPARAN IDENTIFIER RPARAN
                                | SIZE LPARAN IDENTIFIER SQLPARAN INTEGER SQRPARAN RPARAN
        """
        args = []
        if len(t) == 5:
            args = [t[3]]
        elif len(t) == 8:
            args = [t[3], t[5]]
        t[0] = [AlgCallFunction(t[1], args)]

    #   Predefined functions
    
    def _extend(self):
        
        self.parser.add_state('algorithms', 'inclusive')

        self.parser.add_reserved_word('algorithms', 'ALGORITHMS_SPECIFICATION', func=self.word_algorithms_specification)
        self.parser.add_reserved_word('alg', 'ALGORITHM', state='algorithms')
        self.parser.add_reserved_word('if', 'IF', state='algorithms', case_sensitive=True)
        self.parser.add_reserved_word('while', 'WHILE', state='algorithms', case_sensitive=True)
        self.parser.add_reserved_word('else', 'ELSE', state='algorithms', case_sensitive=True)
        self.parser.add_reserved_word('quality', 'QUALITY', state='algorithms', case_sensitive=True)
        self.parser.add_reserved_word('size', 'SIZE', state='algorithms', case_sensitive=True)
        self.parser.add_reserved_word('return', 'RETURN', state='algorithms', case_sensitive=True)

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['algorithms'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['algorithms'])
        self.parser.add_token('ARROWRIGHT', r'\-\>', states=['algorithms'])
        self.parser.add_token('ARROWLEFT', r'\<\-', states=['algorithms'])
        self.parser.add_token('ARROWBOTH', r'\<\-\>', states=['algorithms'])

        self.parser.add_token('PLUS', r'\+', states=['algorithms'])
        self.parser.add_token('MINUS', r'\-', states=['algorithms'])
        self.parser.add_token('TIMES', r'\*', states=['algorithms'])
        self.parser.add_token('DIVIDE', r'/', states=['algorithms'])

        self.parser.add_token('GREATER', r'\>', states=['algorithms'])
        self.parser.add_token('SMALLER', r'\<', states=['algorithms'])
        self.parser.add_token('EXCLAMATION', r'\!', states=['algorithms'])
        self.parser.add_token('AND', r'\&', states=['algorithms'])
        self.parser.add_token('OR', r'\|', states=['algorithms'])

        self.parser.add_rule(self.algorithms_specification)
        self.parser.add_rule(self.algorithms_list)
        self.parser.add_rule(self.algorithm)
        self.parser.add_rule(self.algorithm_instructions)
        self.parser.add_rule(self.algorithm_instruction)
        self.parser.add_rule(self.algorithm_instruction_assignment)
        self.parser.add_rule(self.algorithm_instruction_return)
        self.parser.add_rule(self.algorithm_instruction_if)
        self.parser.add_rule(self.algorithm_instruction_while)
        self.parser.add_rule(self.algorithm_expression_conditional_comparison)
        self.parser.add_rule(self.algorithm_expression_conditional_paran)
        self.parser.add_rule(self.algorithm_expression_simple)
        self.parser.add_rule(self.algorithm_expression_uminus)
        self.parser.add_rule(self.algorithm_expression_paran)
        self.parser.add_rule(self.algorithm_expression_operations)
        self.parser.add_rule(self.algorithm_expression_function)

        self.parser.add_precedence(['PLUS', 'MINUS'], 'left')
        self.parser.add_precedence(['TIMES', 'DIVIDE'], 'left')
        self.parser.add_precedence(['UMINUS'], 'right')