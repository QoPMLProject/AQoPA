'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import Channel, TopologyRuleHost, TopologyRule,\
    AlgWhile, AlgCallFunction, AlgIf, AlgReturn, AlgAssignment


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

    #  Medium

    def medium_specification(self, t):
        """
        comm_specification : MEDIUM_SPECIFICATION SQLPARAN IDENTIFIER SQRPARAN BLOCKOPEN medium_elements BLOCKCLOSE
        """
        self.parser.store.mediums[t[3]] = t[6]

    def medium_elements(self, t):
        """
        medium_elements : medium_default_parameters medium_topology
        """
        t[0] = {
            'topology': t[2],
            'default_parameters': t[1],
        }

    def medium_default_parameters(self, t):
        """
        medium_default_parameters : medium_default_parameter SEMICOLON
                                | medium_default_parameters medium_default_parameter SEMICOLON
        """
        t[0] = t[1]
        if len(t) == 4:
            t[0].update(t[2])

    def quality_default_parameter(self, t):
        """
        medium_default_parameter : QUALITY_DEFAULT_PARAMETER EQUAL number
        """
        t[0] = {'default_q': t[3]}

    #  Topology
    
    def medium_topology(self, t):
        """
        medium_topology : TOPOLOGY_SPECIFICATION BLOCKOPEN topology_rules_list BLOCKCLOSE
        """
        t[0] = {'rules': t[3]}

    def topology_rules_list(self, t):
        """
        topology_rules_list : topology_rule
                        | topology_rules_list topology_rule
        """
        if len(t) == 3:
            t[0] = t[1]
            t[0].append(t[2])
        else:
            t[0] = []
            t[0].append(t[1])

    def topology_rule_point_to_point(self, t):
        """
        topology_rule : IDENTIFIER topology_arrow IDENTIFIER SEMICOLON
                    | IDENTIFIER topology_arrow IDENTIFIER COLON topology_rule_parameters SEMICOLON
        """
        parameters = {}
        if len(t) == 7:
            parameters = t[5]
        l = TopologyRuleHost(t[1])
        r = TopologyRuleHost(t[3])
        t[0] = TopologyRule(l, t[2], r, parameters=parameters)

    def topology_rule_broadcast(self, t):
        """
        topology_rule : IDENTIFIER ARROWRIGHT STAR COLON topology_rule_parameters SEMICOLON
        """
        parameters = {}
        if len(t) == 7:
            parameters = t[5]
        l = TopologyRuleHost(t[1])
        r = TopologyRuleHost(t[3])
        t[0] = TopologyRule(l, t[2], r, parameters=parameters)

    def topology_rule_parameters(self, t):
        """
        topology_rule_parameters : topology_rule_parameter
                            | topology_rule_parameters COMMA topology_rule_parameter
        """
        t[0] = t[1]
        if len(t) == 4:
            t[0].update(t[3])

    def topology_rule_quality_parameter(self, t):
        """
        topology_rule_parameter : Q_PARAMETER EQUAL number
        """
        t[0] = {'q': t[3]}

    def topology_arrow(self, t):
        """
        topology_arrow : ARROWRIGHT
            | ARROWLEFT
            | ARROWBOTH
        """
        t[0] = t[1]

    def _extend(self):
        
        self.parser.add_state('communication', 'inclusive')

        self.parser.add_reserved_word('communication', 'COMMUNICATION_SPECIFICATION',
                                      func=self.word_communication_specification)
        self.parser.add_reserved_word('medium', 'MEDIUM_SPECIFICATION', state='communication',)
        self.parser.add_reserved_word('default_q', 'QUALITY_DEFAULT_PARAMETER', state='communication',)
        self.parser.add_reserved_word('q', 'Q_PARAMETER', state='communication',)
        self.parser.add_reserved_word('topology', 'TOPOLOGY_SPECIFICATION', state='communication',)

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['communication'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['communication'])
        self.parser.add_token('ARROWRIGHT', r'\-\>', states=['communication'])
        self.parser.add_token('ARROWLEFT', r'\<\-', states=['communication'])
        self.parser.add_token('ARROWBOTH', r'\<\-\>', states=['communication'])

        self.parser.add_rule(self.communication_specification)
        self.parser.add_rule(self.comm_specifications)
        self.parser.add_rule(self.medium_specification)
        self.parser.add_rule(self.medium_elements)
        self.parser.add_rule(self.medium_default_parameters)
        self.parser.add_rule(self.quality_default_parameter)
        self.parser.add_rule(self.medium_topology)
        self.parser.add_rule(self.topology_rules_list)
        self.parser.add_rule(self.topology_rule_point_to_point)
        self.parser.add_rule(self.topology_rule_broadcast)
        self.parser.add_rule(self.topology_rule_parameters)
        self.parser.add_rule(self.topology_rule_quality_parameter)
        self.parser.add_rule(self.topology_arrow)


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
        t[0] = {
            'mediums': t[3]
        }
    
    
    def version_comm_specifications(self, t):
        """
        version_comm_specifications : version_comm_specification
                    | version_comm_specifications version_comm_specification
        """
        t[0] = t[1]
        if len(t) == 3:
            t[0].update(t[2])

    #  Medium

    def version_medium_specification(self, t):
        """
        version_comm_specification : MEDIUM_SPECIFICATION SQLPARAN IDENTIFIER SQRPARAN BLOCKOPEN version_medium_elements BLOCKCLOSE
        """
        t[0] = {
            t[3]: t[6]
        }

    def version_medium_elements(self, t):
        """
        version_medium_elements : version_medium_default_parameters version_medium_topology
        """
        t[0] = {
            'topology': t[2],
            'default_parameters': t[1]
        }

    def version_medium_default_parameters(self, t):
        """
        version_medium_default_parameters : version_medium_default_parameter SEMICOLON
                                | version_medium_default_parameters version_medium_default_parameter SEMICOLON
        """
        t[0] = t[1]
        if len(t) == 4:
            t[0].update(t[2])

    def version_quality_default_parameter(self, t):
        """
        version_medium_default_parameter : QUALITY_DEFAULT_PARAMETER EQUAL number
        """
        t[0] = {'default_q': t[3]}

    def version_medium_topology(self, t):
        """
        version_medium_topology : TOPOLOGY_SPECIFICATION BLOCKOPEN version_topology_rules_list BLOCKCLOSE
        """
        t[0] = {'rules': t[3]}
    
    def version_topology_rules_list(self, t):
        """
        version_topology_rules_list : version_topology_rule
                        | version_topology_rules_list version_topology_rule
        """
        if len(t) == 3:
            t[0] = t[1]
            t[0].append(t[2])
        else:
            t[0] = []
            t[0].append(t[1])

    def version_topology_rule_point_to_point(self, t):
        """
        version_topology_rule : version_topology_rule_left_hosts version_topology_arrow version_topology_rule_right_hosts SEMICOLON
                    | version_topology_rule_left_hosts version_topology_arrow version_topology_rule_right_hosts COLON version_topology_rule_parameters SEMICOLON
        """
        parameters = {}
        if len(t) == 7:
            parameters = t[5]
        t[0] = TopologyRule(t[1], t[2], t[3], parameters=parameters)

    def version_topology_rule_boradcast(self, t):
        """
        version_topology_rule : version_topology_rule_left_hosts ARROWRIGHT STAR COLON version_topology_rule_parameters SEMICOLON
        """
        parameters = {}
        if len(t) == 7:
            parameters = t[5]
        t[0] = TopologyRule(t[1], t[2], None, parameters=parameters)

    def version_topology_rule_left_hosts(self, t):
        """
        version_topology_rule_left_hosts : IDENTIFIER
                        | version_topology_host_with_indicies
        """
        if isinstance(t[1], basestring):
            t[0] = TopologyRuleHost(t[1])
        else:
            t[0] = t[1]

    def version_topology_rule_right_hosts(self, t):
        """
        version_topology_rule_right_hosts : IDENTIFIER
                        | STAR
                        | version_topology_host_with_indicies
                        | version_topology_host_with_i_index
        """
        if isinstance(t[1], basestring):
            if t[1] == u"*":
                t[0] = None
            else:
                t[0] = TopologyRuleHost(t[1])
        else:
            t[0] = t[1]

    def version_topology_host_with_indicies(self, t):
        """
        version_topology_host_with_indicies : IDENTIFIER SQLPARAN INTEGER SQRPARAN
                | IDENTIFIER SQLPARAN INTEGER COLON SQRPARAN
                | IDENTIFIER SQLPARAN COLON INTEGER SQRPARAN
                | IDENTIFIER SQLPARAN INTEGER COLON INTEGER SQRPARAN
        """
        index_range = None
        if len(t) == 5:
            index_range = (t[3], t[3])
        elif len(t) == 6:
            if t[3] == ':':
                index_range = (None, t[4])
            else:
                index_range = (t[3], None)
        elif len(t) == 7:
            index_range = (t[3], t[5])
        t[0] = TopologyRuleHost(t[1], index_range=index_range)
    
    def version_topology_host_with_i_index(self, t):
        """
        version_topology_host_with_i_index : IDENTIFIER SQLPARAN I_INDEX SQRPARAN
                | IDENTIFIER SQLPARAN I_INDEX COMM_PLUS INTEGER SQRPARAN
                | IDENTIFIER SQLPARAN I_INDEX COMM_MINUS INTEGER SQRPARAN
        """
        
        i_shift = None
        if len(t) == 5:
            i_shift = 0
        elif len(t) == 7:
            if t[4] == '-':
                i_shift = - t[5]
            else:
                i_shift = t[5]
        t[0] = TopologyRuleHost(t[1], i_shift=i_shift)

    def version_topology_rule_parameters(self, t):
        """
        version_topology_rule_parameters : version_topology_rule_parameter
                            | version_topology_rule_parameters COMMA version_topology_rule_parameter
        """
        t[0] = t[1]
        if len(t) == 4:
            t[0].update(t[3])

    def version_topology_rule_quality_parameter(self, t):
        """
        version_topology_rule_parameter : Q_PARAMETER EQUAL number
        """
        t[0] = {'q': t[3]}

    def version_topology_arrow(self, t):
        """
        version_topology_arrow : ARROWRIGHT
            | ARROWLEFT
            | ARROWBOTH
        """
        t[0] = t[1]

    
    def _extend(self):
        
        self.parser.add_state('versioncommunication', 'inclusive')

        self.parser.add_reserved_word('communication', 'COMMUNICATION_SPECIFICATION',
                                      func=self.word_communication_specification)
        self.parser.add_reserved_word('medium', 'MEDIUM_SPECIFICATION', state='versioncommunication',)
        self.parser.add_reserved_word('default_q', 'QUALITY_DEFAULT_PARAMETER', state='versioncommunication',)
        self.parser.add_reserved_word('topology', 'TOPOLOGY_SPECIFICATION', state='versioncommunication',)
        self.parser.add_reserved_word('i', 'I_INDEX', state='versioncommunication')
        self.parser.add_reserved_word('q', 'Q_PARAMETER', state='versioncommunication',)

        self.parser.add_token('BLOCKOPEN', func=self.token_block_open, states=['versioncommunication'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_block_close, states=['versioncommunication'])
        self.parser.add_token('ARROWRIGHT', r'\-\>', states=['versioncommunication'])
        self.parser.add_token('ARROWLEFT', r'\<\-', states=['versioncommunication'])
        self.parser.add_token('ARROWBOTH', r'\<\-\>', states=['versioncommunication'])

        self.parser.add_token('COMM_PLUS', r'\+', states=['versioncommunication'])
        self.parser.add_token('COMM_MINUS', r'\-', states=['versioncommunication'])


        self.parser.add_rule(self.version_communication)
        self.parser.add_rule(self.version_comm_specifications)
        self.parser.add_rule(self.version_medium_specification)
        self.parser.add_rule(self.version_medium_elements)
        self.parser.add_rule(self.version_medium_default_parameters)
        self.parser.add_rule(self.version_quality_default_parameter)
        self.parser.add_rule(self.version_medium_topology)
        self.parser.add_rule(self.version_topology_rules_list)
        self.parser.add_rule(self.version_topology_rule_point_to_point)
        self.parser.add_rule(self.version_topology_rule_boradcast)
        self.parser.add_rule(self.version_topology_rule_left_hosts)
        self.parser.add_rule(self.version_topology_rule_right_hosts)
        self.parser.add_rule(self.version_topology_rule_parameters)
        self.parser.add_rule(self.version_topology_rule_quality_parameter)
        self.parser.add_rule(self.version_topology_host_with_indicies)
        self.parser.add_rule(self.version_topology_host_with_i_index)
        self.parser.add_rule(self.version_topology_arrow)



    