'''
Created on 27-12-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.model import IfInstruction, WhileInstruction, AssignmentInstruction
from aqopa.model.parser.lex_yacc import LexYaccParser, LexYaccParserExtension
from aqopa.simulator.state import Process


class ComputionalParserExtension(LexYaccParserExtension):

    def __init__(self):
        LexYaccParserExtension.__init__(self)

        self.open_blocks_cnt = 0

    ##########################################
    #                TOKENS
    ##########################################

    def token_identifier(self, t):
        r'[_a-zA-Z][_a-zA-Z0-9]*'

        words = self.parser.get_reserved_words()

        states_stack = []
        states_stack.extend(t.lexer.lexstatestack)
        states_stack.append(t.lexer.current_state())

        i = len(states_stack)-1
        while i >= 0:
            state = states_stack[i]
            if state in words:
                state_words = words[state]
                for state_word in state_words:

                    tvalue = t.value
                    state_word_value = state_word
                    word_tuple = state_words[state_word]

                    # if not case sensitive
                    if not word_tuple[2]:
                        tvalue = tvalue.lower()
                        state_word_value = state_word_value.lower()

                    if tvalue == state_word_value:
                        # If function exists
                        if word_tuple[1]:
                            t = word_tuple[1](t)
                        t.type = word_tuple[0]
                        break
            i -= 1

        return t

    def token_float(self, t):
        r'([1-9][0-9]*\.[0-9]+)|(0\.[0-9]+)'
        t.value = float(t.value)
        return t

    def token_integer(self, t):
        r'0|[1-9][0-9]*'
        t.value = int(t.value)
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

    def rule_number(self, t):
        """
        number : FLOAT
                | INTEGER
        """
        t[0] = t[1]

    def reputation_expression_operations(self, t):
        """
        reputation_expression : reputation_expression PLUS reputation_expression
                            | reputation_expression MINUS reputation_expression
                            | reputation_expression TIMES reputation_expression
                            | reputation_expression DIVIDE reputation_expression
        """
        if t[2] == '+':
            t[0] = t[1] + t[3]
        elif t[2] == '-':
            t[0] = t[1] - t[3]
        elif t[2] == '/':
            t[0] = t[1] / t[3]
        elif t[2] == '*':
            t[0] = t[1] * t[3]

    def reputation_expression_values(self, t):
        """
        reputation_expression : number
                            | IDENTIFIER
        """
        try:
            t[0] = float(t[1])
        except ValueError:
            t[0] = self.parser.vars[t[1]]

    def reputation_expression_uminus(self, t):
        """
        reputation_expression : MINUS reputation_expression %prec UMINUS
        """
        t[0] = - t[2]

    def reputation_expression_paran(self, t):
        """
        reputation_expression : LPARAN reputation_expression RPARAN
        """
        t[0] = t[2]

    def reputation_expression_conditional_comparison(self, t):
        """
        reputation_expression_conditional : reputation_expression EQUAL EQUAL reputation_expression
                                        | reputation_expression EXCLAMATION EQUAL reputation_expression
                                        | reputation_expression GREATER reputation_expression
                                        | reputation_expression GREATER EQUAL reputation_expression
                                        | reputation_expression SMALLER reputation_expression
                                        | reputation_expression SMALLER EQUAL reputation_expression
                                        | reputation_expression AND AND reputation_expression
                                        | reputation_expression OR OR reputation_expression
        """
        if t[3] == '=':
            if t[2] == '=':
                t[0] = t[1] == t[4]
            elif t[2] == '!':
                t[0] = t[1] != t[4]
            elif t[2] == '>':
                t[0] = t[1] >= t[4]
            elif t[2] == '<':
                t[0] = t[1] <= t[4]
        elif t[2] == '>':
            t[0] = t[1] > t[3]
        elif t[2] == '<':
            t[0] = t[1] < t[3]
        elif t[2] == '&' and t[3] == '&':
            t[0] = t[1] and t[4]
        elif t[2] == '|' and t[3] == '|':
            t[0] = t[1] or t[4]
        else:
            t[0] = False

    def reputation_expression_conditional_operators(self, t):
        """
        reputation_expression_conditional : USED LPARAN IDENTIFIER RPARAN
                                        | EXISTS LPARAN IDENTIFIER RPARAN
        """
        if t[1].lower() == 'used':
            t[0] = self.parser.process_uses_variable(t[3])
        else:
            t[0] = self.parser.host.has_variable(t[3])


    def reputation_expression_conditional_paran(self, t):
        """
        reputation_expression_conditional : LPARAN reputation_expression_conditional RPARAN
        """
        t[0] = t[2]

    def _extend(self):
        """ """
        self.parser.add_reserved_word('if', 'IF', case_sensitive=True)
        self.parser.add_reserved_word('else', 'ELSE', case_sensitive=True)
        self.parser.add_reserved_word('used', 'USED', case_sensitive=True)
        self.parser.add_reserved_word('exists', 'EXISTS', case_sensitive=True)

        self.parser.add_token('FLOAT', func=self.token_float)
        self.parser.add_token('INTEGER', func=self.token_integer)
        self.parser.add_token('IDENTIFIER', func=self.token_identifier)

        self.parser.add_token('SEMICOLON', r';')
        self.parser.add_token('EQUAL', r'\=')

        self.parser.add_token('LPARAN', r'\(')
        self.parser.add_token('RPARAN', r'\)')
        self.parser.add_token('SQLPARAN', r'\[')
        self.parser.add_token('SQRPARAN', r'\]')
        self.parser.add_token('BLOCKOPEN', func=self.token_blockopen)
        self.parser.add_token('BLOCKCLOSE', func=self.token_blockclose)

        self.parser.add_token('PLUS', r'\+')
        self.parser.add_token('MINUS', r'\-')
        self.parser.add_token('TIMES', r'\*')
        self.parser.add_token('DIVIDE', r'/')

        self.parser.add_token('GREATER', r'\>')
        self.parser.add_token('SMALLER', r'\<')
        self.parser.add_token('EXCLAMATION', r'\!')
        self.parser.add_token('AND', r'\&')
        self.parser.add_token('OR', r'\|')

        self.parser.add_precedence(['PLUS', 'MINUS'], 'left')
        self.parser.add_precedence(['TIMES', 'DIVIDE'], 'left')
        self.parser.add_precedence(['UMINUS'], 'right')

        # Rules

        self.parser.add_rule(self.rule_number)
        self.parser.add_rule(self.reputation_expression_operations)
        self.parser.add_rule(self.reputation_expression_paran)
        self.parser.add_rule(self.reputation_expression_uminus)
        self.parser.add_rule(self.reputation_expression_values)
        self.parser.add_rule(self.reputation_expression_conditional_comparison)
        self.parser.add_rule(self.reputation_expression_conditional_operators)
        self.parser.add_rule(self.reputation_expression_conditional_paran)

class ComputionalParser(LexYaccParser):

    _conditional_expression_instance = None
    _simple_expression_instance = None

    def __init__(self):
        self.host = None
        self.vars = {}
        LexYaccParser.__init__(self)

    def restart(self):
        self.yaccer.restart()

    def parse_expression(self, s, host, rep_vars):
        self.host = host
        self.vars = rep_vars
        return self.yaccer.parse(input=s, lexer=self.lexer)

    def process_uses_variable(self, variable_name):
        """ Returns True if variable with given name is defined anywhere in process """
        index = 0
        instructions = self.host.get_current_process().instructions_list
        while index < len(instructions):
            instruction = instructions[index]
            if isinstance(instruction, IfInstruction):
                instructions.extend(instruction.true_instructions)
                instructions.extend(instruction.false_instructions)
            elif isinstance(instruction, WhileInstruction):
                instructions.extend(instruction.instructions)
            elif isinstance(instruction, AssignmentInstruction):
                if instruction.variable_name == variable_name:
                    return True
            index += 1
        return False

    @staticmethod
    def conditional_expression_instance():
        if ComputionalParser._conditional_expression_instance is None:
            parser_ext = ComputionalParserExtension()
            ComputionalParser._conditional_expression_instance = ComputionalParser()
            ComputionalParser._conditional_expression_instance.add_extension(parser_ext)
            ComputionalParser._conditional_expression_instance.start_symbol = 'reputation_expression_conditional'
            ComputionalParser._conditional_expression_instance.build()
        else:
            ComputionalParser._conditional_expression_instance.restart()

        return ComputionalParser._conditional_expression_instance

    @staticmethod
    def simple_expression_instance():
        if ComputionalParser._simple_expression_instance is None:
            parser_ext = ComputionalParserExtension()
            ComputionalParser._simple_expression_instance = ComputionalParser()
            ComputionalParser._simple_expression_instance.add_extension(parser_ext)
            ComputionalParser._simple_expression_instance.start_symbol = 'reputation_expression'
            ComputionalParser._simple_expression_instance.build()
        else:
            ComputionalParser._conditional_expression_instance.restart()

        return ComputionalParser._simple_expression_instance



def compute_conditional_expression(host, expression, vars):
    """
    Computes the result of conditional expression.
    """
    parser = ComputionalParser.conditional_expression_instance()
    return parser.parse_expression(expression, host, vars)

def compute_simple_expression(host, expression, vars):
    """
    Computes the result of simple expression.
    """
    parser = ComputionalParser.simple_expression_instance()
    return parser.parse_expression(expression, host, vars)

def update_vars(host, instructions, vars):
    """
    Updae vars according to the instructions of algorithm.
    """
    index = 0
    while index < len(instructions):
        instruction = instructions[index]
        if instruction['type'] == 'assignment':
            vars[instruction['identifier']] = compute_simple_expression(host, instruction['expression'], vars)
        elif instruction['type'] == 'if':
            condition = compute_conditional_expression(host, instruction['condition'], vars)
            if condition:
                if_instructions = instruction['true_instructions']
            else:
                if_instructions = instruction['false_instructions']
            if_index = index + 1
            for i in if_instructions:
                instructions.insert(if_index, i)
                if_index += 1
        index += 1
    return vars
