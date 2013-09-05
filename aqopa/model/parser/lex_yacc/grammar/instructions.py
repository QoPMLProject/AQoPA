'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import AssignmentInstruction,\
    CommunicationInstruction,\
    WhileInstruction, IfInstruction, ContinueInstruction, FinishInstruction,\
    CallFunctionInstruction, COMMUNICATION_TYPE_OUT, COMMUNICATION_TYPE_IN,\
    HostSubprocess


class Builder():

    def build_subprocess(self, token):
        """
        host_subprocess : SUBPROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE
                    | SUBPROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
        """
        s = HostSubprocess(token[2], token[5])
        
        all_channels_active = '*' in token[3]
        if all_channels_active:
            s.all_channels_active = True
        else:
            s.active_channels = token[3]
        
        return s

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
    
    def word_subprocess_specification(self, t):
        t.lexer.push_state('subprocess')
        return t
    
    ##########################################
    #                TOKENS
    ##########################################
    
    def token_block_open(self, t):
        r'{'
        state = t.lexer.current_state()
        state += str(t.lexer.lexstatestack.count(state))
        
        if state not in self.open_blocks_cnt_by_state:
            self.open_blocks_cnt_by_state[state] = 0 
        self.open_blocks_cnt_by_state[state] += 1
        return t
    
    def token_block_close(self, t):
        r'}'
        state = t.lexer.current_state()
        state += str(t.lexer.lexstatestack.count(state))
        
        self.open_blocks_cnt_by_state[state] -= 1
        if self.open_blocks_cnt_by_state[state] == 0:
            t.lexer.pop_state()
        return t
    
    def token_host_rparan(self, t):
        r'\)'
        t.lexer.push_state('hostrparan')
        return t

    ##########################################
    #                RULES
    ##########################################
    
    def instructions_list(self, t):
        """
        instructions_list : instruction
                        | instructions_list instruction
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
    
    def instruction(self, t):
        """
        instruction : instruction_assignment
                | instruction_subprocess
                | instruction_communication
                | instruction_while
                | instruction_if
                | instruction_special_command
                | instruction_call_function
        """
        t[0] = t[1]
    
    def instruction_subprocess(self, t):
        """
        instruction_subprocess : SUBPROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE
                    | SUBPROCESS IDENTIFIER host_channels BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
        """
        t[0] = self.builder.build_subprocess(t)
    
    def instruction_assignment(self, t):
        """
        instruction_assignment : IDENTIFIER EQUAL expression_simple SEMICOLON
        """
        t[0] = AssignmentInstruction(t[1], t[3])
    
    def instruction_communication(self, t):
        """
        instruction_communication : IN LPARAN IDENTIFIER COLON identifiers_list RPARAN SEMICOLON
                                | OUT LPARAN IDENTIFIER COLON identifiers_list RPARAN SEMICOLON
        """
        communication_type = COMMUNICATION_TYPE_OUT
        if t[1].lower() == 'in':
            communication_type = COMMUNICATION_TYPE_IN
            
        t[0] = CommunicationInstruction(communication_type, t[3], t[5])
    
    def instruction_while(self, t):
        """
        instruction_while : WHILE LPARAN expression_conditional RPARAN BLOCKOPEN instructions_list BLOCKCLOSE
                        | WHILE LPARAN expression_conditional RPARAN BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
        """
        t[0] = WhileInstruction(t[3], t[6])
    
    def instruction_if(self, t):
        """
        instruction_if : IF LPARAN expression_conditional RPARAN BLOCKOPEN instructions_list BLOCKCLOSE 
                    | IF LPARAN expression_conditional RPARAN BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
                    | IF LPARAN expression_conditional RPARAN BLOCKOPEN instructions_list BLOCKCLOSE ELSE BLOCKOPEN instructions_list BLOCKCLOSE
                    | IF LPARAN expression_conditional RPARAN BLOCKOPEN instructions_list BLOCKCLOSE ELSE BLOCKOPEN instructions_list BLOCKCLOSE SEMICOLON
        """
        
        conditional = t[3]
        true_instructions = t[6]
        false_instructions = []
        if len(t) > 10:
            false_instructions = t[10]
        
        t[0] = IfInstruction(conditional, true_instructions, false_instructions)
    
    def instruction_special_command(self, t):
        """
        instruction_special_command : CONTINUE SEMICOLON
                                | STOP SEMICOLON
                                | END SEMICOLON
        """
        if t[1].lower() == 'continue':
            t[0] = ContinueInstruction()
        elif t[1].lower() == 'end':
            t[0] = FinishInstruction('end')
        elif t[1].lower() == 'stop':
            t[0] = FinishInstruction('stop')
    
    def instruction_call_function(self, t):
        """
        instruction_call_function : expression_call_function SEMICOLON
        """
        t[0] = CallFunctionInstruction(t[1].function_name, t[1].arguments, t[1].qop_arguments)
    
    
    def _extend(self):
        
        self.parser.add_state('subprocess', 'inclusive')
        self.parser.add_reserved_word('subprocess', 'SUBPROCESS', func=self.word_subprocess_specification, state='process')
           
        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['subprocess'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['subprocess'])
        self.parser.add_token('RPARAN', func=self.token_host_rparan, states=['subprocess'])
        
        self.parser.add_rule(self.instructions_list)
        self.parser.add_rule(self.instruction)
        self.parser.add_rule(self.instruction_subprocess)
        self.parser.add_rule(self.instruction_assignment)
        self.parser.add_rule(self.instruction_communication)
        self.parser.add_rule(self.instruction_while)
        self.parser.add_rule(self.instruction_if)
        self.parser.add_rule(self.instruction_special_command)
        self.parser.add_rule(self.instruction_call_function)
        

    