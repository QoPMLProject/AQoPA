'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model.parser.lex_yacc import LexYaccParserExtension
from aqopa.model import MetricsConfiguration, MetricsData,\
    MetricsPrimitiveBlock, MetricsPrimitiveHeader, MetricsPrimitive, \
    MetricsServiceParam


class Builder():

    def create_metrics_configuration(self, token):
        """
        metrics_configuration : METRICS_CONFIGURATION LPARAN IDENTIFIER RPARAN BLOCKOPEN metrics_configuration_params BLOCKCLOSE
        """
        hostname = token[3]
        host_conf_params = token[6]
        return MetricsConfiguration(hostname, host_conf_params)
    
    def create_metrics_data(self, token):
        """
        metrics_data : METRICS_DATA LPARAN IDENTIFIER RPARAN BLOCKOPEN metrics_data_blocks BLOCKCLOSE
                    | METRICS_DATA PLUS LPARAN QUALIFIED_IDENTIFIER RPARAN BLOCKOPEN metrics_data_blocks BLOCKCLOSE
                    | METRICS_DATA STAR LPARAN QUALIFIED_IDENTIFIER RPARAN BLOCKOPEN metrics_data_blocks BLOCKCLOSE
        """
        
        if len(token) == 8:
            name = token[3]
            blocks = token[6]
            md = MetricsData(name, blocks)
        elif len(token) == 9:
            name = token[4]
            blocks = token[7]
            plus = token[2] == '+' 
            star = token[2] == '*'
            md = MetricsData(name, blocks, plus, star)
            
        return md 
    
    def create_metrics_block(self, token):
        """
        metrics_data_block : metrics_primitives_head metrics_primitives 
        """
        return MetricsPrimitiveBlock(token[1], token[2])
    
    def create_metrics_header(self, token):
        """
        metrics_primitives_head : METRICS_PRIMITIVES_HEAD metrics_params metrics_services_params SEMICOLON
        """
        return MetricsPrimitiveHeader(token[2], token[3])
    
    def create_metrics_primitive(self, token):
        """
        metrics_primitive : METRICS_PRIMITIVE metrics_primitive_arguments SEMICOLON
        """
        return MetricsPrimitive(token[2])
    
    def create_metrics_services_param_size(self, token):
        """
        metrics_services_param : SQLPARAN SIZE COLON metrics_services_size_type_unit LPARAN metrics_services_size_unit RPARAN SQRPARAN
                            | SQLPARAN SIZE COLON metrics_services_size_type_non_unit SQRPARAN
        """
        unit = token[6] if len(token) == 9 else None
        return MetricsServiceParam(token[2], token[4], unit)
        

class MetricsParserExtension(LexYaccParserExtension):
    """
    Extension for parsing metrics
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
    
    def token_metrics_block_close(self, t):
        r"\}"
        t.lexer.pop_state()
        return t

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
        self.parser.t_error(t)
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    

    ##########################################
    #                RULES
    ##########################################
    
    
    def metrics_specification(self, t):
        """
        specification : METRICS_SPECIFICATION BLOCKOPEN metrics_configurations metrics_datas BLOCKCLOSE
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
        self.parser.store.metrics_configurations.append(self.builder.create_metrics_configuration(t))
    
    def metrics_configuration_params(self, t):
        """
        metrics_configuration_params : metrics_configuration_param
                                    | metrics_configuration_params metrics_configuration_param
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
    
    def metrics_configuration_param(self, t):
        """
        metrics_configuration_param : IDENTIFIER EQUAL PARAMVALUE SEMICOLON
        """
        t[0] = (t[1], t[2])
    
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
        self.parser.store.metrics_datas.append(self.builder.create_metrics_data(t))
        
    def metrics_data_blocks(self, t):
        """
        metrics_data_blocks : metrics_data_block
                            | metrics_data_blocks HASH metrics_data_block
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[3])
    
    def metrics_data_block(self, t):
        """
        metrics_data_block : metrics_primitives_head metrics_primitives 
        """
        t[0] = self.builder.create_metrics_block(t)
    
    def metrics_primitives_head(self, t):
        """
        metrics_primitives_head : METRICS_PRIMITIVES_HEAD metrics_params metrics_services_params SEMICOLON
        """
        t[0] = self.builder.create_metrics_header(t)
    
    def metrics_params(self, t):
        """
        metrics_params : metrics_param
                        | metrics_params metrics_param
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
    
    def metrics_param(self, t):
        """
        metrics_param : SQLPARAN IDENTIFIER SQRPARAN
        """
        t[0] = t[2]
    
    def metrics_services_params(self, t):
        """
        metrics_services_params : metrics_services_param
                            | metrics_services_params metrics_services_param
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])

    def metrics_primitives(self, t):
        """
        metrics_primitives : metrics_primitive
                            | metrics_primitives metrics_primitive
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
    
    def metrics_primitive(self, t):
        """
        metrics_primitive : METRICS_PRIMITIVE metrics_primitive_arguments SEMICOLON
        """
        t[0] = self.builder.create_metrics_primitive(t)
    
    def metrics_primitive_arguments(self, t):
        """
        metrics_primitive_arguments : metrics_primitive_argument
                                | metrics_primitive_arguments metrics_primitive_argument
        """
        if len(t) == 2:
            t[0] = []
            t[0].append(t[1])
        else:
            t[0] = t[1]
            t[0].append(t[2])
        
    def metrics_primitive_argument(self, t):
        """
        metrics_primitive_argument : SQLPARAN ARGUMENTVALUE SQRPARAN
        """
        t[0] = t[2].strip()

    #######################
    #    Metrics Size
    #######################
    
    def metrics_services_param_size(self, t):
        """
        metrics_services_param : SQLPARAN SIZE COLON metrics_services_size_type_unit LPARAN metrics_services_size_unit RPARAN SQRPARAN
                            | SQLPARAN SIZE COLON metrics_services_size_type_non_unit SQRPARAN
        """
        t[0] = self.builder.create_metrics_services_param_size(t)
    
    def metrics_services_size_type_unit(self, t):
        """
        metrics_services_size_type_unit : EXACT
                                        | BLOCK
        """
        t[0] = t[1].lower()
    
    def metrics_services_size_type_non_unit(self, t):
        """
        metrics_services_size_type_non_unit : RATIO
                                            | SUM_RATIO
                                            | NESTED
        """
        t[0] = t[1].lower()
    
    def metrics_services_size_unit(self, t):
        """
        metrics_services_size_unit : B
        """
        t[0] = t[1].lower()
    
    
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
        self.parser.add_reserved_word('data', 'METRICS_DATA', func=self.word_metrics_data, state='metrics')
        self.parser.add_reserved_word('primhead', 'METRICS_PRIMITIVES_HEAD', func=self.word_metricsdata_primhead, state='metricsdata')
        self.parser.add_reserved_word('primitive', 'METRICS_PRIMITIVE', func=self.word_metricsdata_primitive, state='metricsdata')
    
        self.parser.add_token('QUALIFIED_IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*(\.[1-9][0-9]*)+', states=['metrics', 'metricsdata'])
        self.parser.add_token('BLOCKCLOSE', func=self.token_metrics_block_close, states=['metrics'])

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
        self.parser.add_reserved_word('sum_ratio', 'SUM_RATIO', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('block', 'BLOCK', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('nested', 'NESTED', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('B', 'B', state='metricsprimhead')
        self.parser.add_reserved_word('ms', 'ms', state='metricsprimhead')
        
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
    