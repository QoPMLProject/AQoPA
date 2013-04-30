'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import sys
from qopml.interpreter.model.parser.lex_yacc.parser import LexYaccParserExtension


class Builder():

    pass

class ParserExtension(LexYaccParserExtension):
    """
    Extension for parsing functions
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
        self.builder = Builder()
        
    ##########################################
    #           RESERVED WORDS
    ##########################################
    
    def word_metrics_specification(self, t):
        t.lexer.push_state('metrics')
        return t
    
    def word_metrics_data(self, t):
        t.lexer.push_state('metricsdata')
        return t
    
    def word_metrics_configuration(self, t):
        t.lexer.push_state('metricsconfiguration')
        return t
    
    def word_metricsdata_primhead(self, t):
        t.lexer.push_state('metricsprimhead')
        return t
    
    def word_metricsdata_primitive(self, t):
        t.lexer.push_state('metricsprimitive')
        return t
    
    ##########################################
    #                TOKENS
    ##########################################

    def token_metricsconfiguration_block_open(self, t):
        r"\{"
        t.lexer.push_state('metricsconfigurationparams')
        return t

    def token_metricsconfigurationparams_block_close(self, t):
        r"\}"
        t.lexer.pop_state()
        t.lexer.pop_state()
        return t
    
    def token_metricsconfigurationparams_equal(self, t):
        r'\='
        t.lexer.push_state('metricsconfigurationparamsvalue')
        return t
    
    def token_metricsconfigurationparamsvalue_paramvalue(self, t):
        r'[^;]+'
        t.lexer.pop_state()
        return t
    
    def token_metricsdata_block_close(self, t):
        r"\}"
        t.lexer.pop_state()
        return t
    
    def token_metricsprimhead_semicolon(self, t):
        r"\;"
        t.lexer.pop_state()
        return t
    
    def token_metricsprimitive_sqlparan(self, t):
        r"\["
        t.lexer.push_state('metricsprimitiveargumentvalue')
        return t
    
    def token_metricsprimitive_semicolon(self, t):
        r"\;"
        t.lexer.pop_state()
        return t
    
    def token_metricsprimitiveargumentvalue_argumentvalue(self, t):
        r'[^]]+'
        t.lexer.pop_state()
        return t
    
    def token_error(self, t):
        sys.stderr.write("Line [%s:%s]: Illegal character '%s' \n" % (t.lexer.lineno, t.lexer.lexpos, t.value[0]))
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    

    ##########################################
    #                RULES
    ##########################################
    
    
    def metrics_specification(self, t):
        """
        specification : METRICS_SPECIFICATION BLOCKOPEN metrics_configurations metrics_datas metrics_sets BLOCKCLOSE
        """
        pass
    
    def metrics_configurations(self, t):
        """
        metrics_configurations : metrics_configuration
                            | metrics_configurations metrics_configuration
        """
        pass
    
    def metrics_configuration(self, t):
        """
        metrics_configuration : METRICS_CONFIGURATION LPARAN IDENTIFIER RPARAN BLOCKOPEN metrics_configuration_params BLOCKCLOSE
        """
        pass
    
    def metrics_configuration_params(self, t):
        """
        metrics_configuration_params : metrics_configuration_param
                                    | metrics_configuration_params metrics_configuration_param
        """
        pass
    
    def metrics_configuration_param(self, t):
        """
        metrics_configuration_param : IDENTIFIER EQUAL PARAMVALUE SEMICOLON
        """
        pass
    
    def metrics_datas(self, t):
        """
        metrics_datas : metrics_data 
                    | metrics_datas metrics_data
        """
        pass
        
    def metrics_data(self, t):
        """
        metrics_data : METRICS_DATA LPARAN IDENTIFIER RPARAN BLOCKOPEN metrics_data_blocks BLOCKCLOSE
                    | METRICS_DATA PLUS LPARAN QUALIFIED_IDENTIFIER RPARAN BLOCKOPEN metrics_data_blocks BLOCKCLOSE
                    | METRICS_DATA STAR LPARAN QUALIFIED_IDENTIFIER RPARAN BLOCKOPEN metrics_data_blocks BLOCKCLOSE
        """
        pass
        
    def metrics_data_blocks(self, t):
        """
        metrics_data_blocks : metrics_data_block
                            | metrics_data_blocks HASH metrics_data_block
        """
        pass
    
    def metrics_data_block(self, t):
        """
        metrics_data_block : metrics_primitives_head metrics_primitives 
        """
        pass
    
    def metrics_primitives_head(self, t):
        """
        metrics_primitives_head : METRICS_PRIMITIVES_HEAD metrics_params metrics_services_params SEMICOLON
        """
        pass
    
    def metrics_params(self, t):
        """
        metrics_params : metrics_param
                        | metrics_params metrics_param
        """
        pass
    
    def metrics_param(self, t):
        """
        metrics_param : SQLPARAN IDENTIFIER SQRPARAN
        """
        pass
    
    def metrics_services_params(self, t):
        """
        metrics_services_params : metrics_services_param
                            | metrics_services_params metrics_services_param
        """
        pass

    def metrics_primitives(self, t):
        """
        metrics_primitives : metrics_primitive
                            | metrics_primitives metrics_primitive
        """
        pass
    
    def metrics_primitive(self, t):
        """
        metrics_primitive : METRICS_PRIMITIVE metrics_primitive_arguments SEMICOLON
        """
        pass
    
    def metrics_primitive_arguments(self, t):
        """
        metrics_primitive_arguments : metrics_primitive_argument
                                | metrics_primitive_arguments metrics_primitive_argument
        """
        pass
        
    def metrics_primitive_argument(self, t):
        """
        metrics_primitive_argument : SQLPARAN ARGUMENTVALUE SQRPARAN
        """
        pass
    
    def metrics_sets(self, t):
        """
        metrics_sets : metrics_set
                    | metrics_sets metrics_set
        """
        pass
    
    def metrics_set(self, t):
        """
        metrics_set : METRICS_SET METRICS_HOST IDENTIFIER LPARAN IDENTIFIER RPARAN SEMICOLON
                | METRICS_SET METRICS_HOST IDENTIFIER LPARAN QUALIFIED_IDENTIFIER RPARAN SEMICOLON
        """
        pass

    #######################
    #    Metrics Size
    #######################
    
    def metrics_services_param_size(self, t):
        """
        metrics_services_param : SQLPARAN SIZE COLON metrics_services_size_type_unit LPARAN metrics_services_size_unit RPARAN SQRPARAN
                            | SQLPARAN SIZE COLON metrics_services_size_type_non_unit SQRPARAN
        """
        pass
    
    def metrics_services_size_type_unit(self, t):
        """
        metrics_services_size_type_unit : EXACT
        """
        pass
    
    def metrics_services_size_type_non_unit(self, t):
        """
        metrics_services_size_type_non_unit : RATIO
        """
        pass
    
    def metrics_services_size_unit(self, t):
        """
        metrics_services_size_unit : B
        """
        pass
    
    
    
    def _extend(self):
        
        self.parser.add_state('metrics', 'inclusive')
        self.parser.add_state('metricsdata', 'inclusive')
        self.parser.add_state('metricsprimhead', 'inclusive')
        
        self.parser.add_state('metricsconfiguration', 'inclusive')
        self.parser.add_state('metricsconfigurationparams', 'exclusive')
        self.parser.add_state('metricsconfigurationparamsvalue', 'exclusive')
        
        self.parser.add_state('metricsprimitive', 'inclusive')
        self.parser.add_state('metricsprimitiveargumentvalue', 'exclusive')

        self.parser.add_reserved_word('metrics', 'METRICS_SPECIFICATION', func=self.word_metrics_specification,)
        self.parser.add_reserved_word('conf', 'METRICS_CONFIGURATION', func=self.word_metrics_configuration, state='metrics')
        self.parser.add_reserved_word('set', 'METRICS_SET', state='metrics')
        self.parser.add_reserved_word('host', 'METRICS_HOST', state='metrics')
        self.parser.add_reserved_word('data', 'METRICS_DATA', func=self.word_metrics_data, state='metrics')
        self.parser.add_reserved_word('primhead', 'METRICS_PRIMITIVES_HEAD', func=self.word_metricsdata_primhead, state='metricsdata')
        self.parser.add_reserved_word('primitive', 'METRICS_PRIMITIVE', func=self.word_metricsdata_primitive, state='metricsdata')
    
        self.parser.add_token('QUALIFIED_IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*(\.[1-9][0-9]*)+', states=['metrics', 'metricsdata'])

        # METRICS CONFIGURATION    
        self.parser.add_token('BLOCKOPEN', func=self.token_metricsconfiguration_block_open, states=['metricsconfiguration'])
        
        # Metrics configuration params state
        self.parser.add_token('error', func=self.token_error, states=['metricsconfigurationparams'], include_in_tokens=False)
        self.parser.add_token('ignore', "\t ", states=['metricsconfigurationparams'], include_in_tokens=False)
        self.parser.add_token('newline', func=self.t_newline,  states=['metricsconfigurationparams'], include_in_tokens=False)
        self.parser.add_token('BLOCKCLOSE', func=self.token_metricsconfigurationparams_block_close, states=['metricsconfigurationparams'])
        self.parser.add_token('IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*', states=['metricsconfigurationparams'])
        self.parser.add_token('SEMICOLON', r'\;', states=['metricsconfigurationparams'])
        self.parser.add_token('EQUAL', func=self.token_metricsconfigurationparams_equal, states=['metricsconfigurationparams'])
        
        # Metrics configuration params value state
        self.parser.add_token('error', func=self.token_error, states=['metricsconfigurationparamsvalue'], include_in_tokens=False)
        self.parser.add_token('ignore', "\t ", states=['metricsconfigurationparamsvalue'], include_in_tokens=False)
        self.parser.add_token('newline', func=self.t_newline,  states=['metricsconfigurationparamsvalue'], include_in_tokens=False)
        self.parser.add_token('PARAMVALUE', func=self.token_metricsconfigurationparamsvalue_paramvalue, states=['metricsconfigurationparamsvalue'])

        # METRICS DATA
        self.parser.add_token('PLUS', r"\+", states=['metricsdata'])
        self.parser.add_token('HASH', r"\#", states=['metricsdata'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_metricsdata_block_close, states=['metricsdata'])

        # Primhead
        self.parser.add_token('SEMICOLON', func=self.token_metricsprimhead_semicolon, states=['metricsprimhead'])
        
        self.parser.add_reserved_word('size', 'SIZE', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('exact', 'EXACT', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('ratio', 'RATIO', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('B', 'B', state='metricsprimhead')
        
        #Primitive
        self.parser.add_token('SQLPARAN', func=self.token_metricsprimitive_sqlparan, states=['metricsprimitive'])
        self.parser.add_token('SEMICOLON', func=self.token_metricsprimitive_semicolon, states=['metricsprimitive'])
        
        self.parser.add_token('error', func=self.token_error, states=['metricsprimitiveargumentvalue'], include_in_tokens=False)
        self.parser.add_token('ignore', "\t ", states=['metricsprimitiveargumentvalue'], include_in_tokens=False)
        self.parser.add_token('newline', func=self.t_newline,  states=['metricsprimitiveargumentvalue'], include_in_tokens=False)
        self.parser.add_token('ARGUMENTVALUE', func=self.token_metricsprimitiveargumentvalue_argumentvalue, states=['metricsprimitiveargumentvalue'])
        
    
        self.parser.add_rule(self.metrics_specification)
        self.parser.add_rule(self.metrics_configurations)
        self.parser.add_rule(self.metrics_configuration)
        self.parser.add_rule(self.metrics_configuration_params)
        self.parser.add_rule(self.metrics_configuration_param)
        self.parser.add_rule(self.metrics_datas)
        self.parser.add_rule(self.metrics_data)
        self.parser.add_rule(self.metrics_data_blocks)
        self.parser.add_rule(self.metrics_data_block)
        self.parser.add_rule(self.metrics_primitives_head)
        self.parser.add_rule(self.metrics_params)
        self.parser.add_rule(self.metrics_param)
        self.parser.add_rule(self.metrics_services_params)
        self.parser.add_rule(self.metrics_primitives)
        self.parser.add_rule(self.metrics_primitive)
        self.parser.add_rule(self.metrics_primitive_arguments)
        self.parser.add_rule(self.metrics_primitive_argument)
        self.parser.add_rule(self.metrics_services_param_size)
        self.parser.add_rule(self.metrics_services_size_type_unit)
        self.parser.add_rule(self.metrics_services_size_type_non_unit)
        self.parser.add_rule(self.metrics_services_size_unit)
        self.parser.add_rule(self.metrics_sets)
        self.parser.add_rule(self.metrics_set)
    