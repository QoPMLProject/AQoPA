'''
Created on 01-06-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model import MetricsServiceParam
from aqopa.model.parser.lex_yacc import LexYaccParserExtension


class Builder():
    
    def create_metrics_services_param_time(self, token):
        """
        metrics_services_param : SQLPARAN TIME COLON metrics_services_time_type LPARAN metrics_services_time_unit RPARAN SQRPARAN
                                | SQLPARAN TIME COLON metrics_services_time_two_params_type LPARAN metrics_services_exact_time_unit COMMA metrics_services_size_unit RPARAN SQRPARAN
        """
        if len(token) == 9:
            return MetricsServiceParam(token[2], token[4], token[6])
        else:
            return MetricsServiceParam(token[2], token[4], (token[6], token[8]))


class MetricsParserExtension(LexYaccParserExtension):
    """
    Extension for parsing timeanalysis module's metrics
    """
    
    def __init__(self):
        LexYaccParserExtension.__init__(self)
        
        self.builder = Builder()
    

    #######################
    #    Metrics Time
    #######################
    
    def metrics_services_param_time(self, t):
        """
        metrics_services_param : SQLPARAN TIME COLON metrics_services_time_type LPARAN metrics_services_time_unit RPARAN SQRPARAN
                                | SQLPARAN TIME COLON metrics_services_time_two_params_type LPARAN metrics_services_exact_time_unit COMMA metrics_services_size_unit RPARAN SQRPARAN
        """
        t[0] = self.builder.create_metrics_services_param_time(t)
    
    def metrics_services_time_one_param_type(self, t):
        """
        metrics_services_time_type : EXACT
                                | RANGE
        """
        t[0] = t[1].lower()

    def metrics_services_time_two_params_type(self, t):
        """
        metrics_services_time_two_params_type : BLOCK
        """
        t[0] = t[1].lower()
    
    def metrics_services_time_unit(self, t):
        """
        metrics_services_time_unit : MS
                                | MSPBIT
                                | MSPBYTE
        """
        t[0] = t[1]

    def metrics_services_exact_time_unit(self, t):
        """
        metrics_services_exact_time_unit : MS
        """
        t[0] = t[1].lower()

    def metrics_services_size_unit(self, t):
        """
        metrics_services_size_unit : B
                                | b
        """
        t[0] = t[1]
    
    def _extend(self):
        """ """

        self.parser.add_token('COMMA', r'\,', states=['metricsprimhead'])

        self.parser.add_reserved_word('time', 'TIME', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('exact', 'EXACT', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('range', 'RANGE', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('ms', 'MS', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('mspb', 'MSPBIT', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('mspB', 'MSPBYTE', state='metricsprimhead', case_sensitive=True)

        self.parser.add_reserved_word('block', 'BLOCK', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('b', 'b', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('B', 'B', state='metricsprimhead', case_sensitive=True)
        
        self.parser.add_rule(self.metrics_services_param_time)
        self.parser.add_rule(self.metrics_services_time_one_param_type)
        self.parser.add_rule(self.metrics_services_time_two_params_type)
        self.parser.add_rule(self.metrics_services_time_unit)
        self.parser.add_rule(self.metrics_services_exact_time_unit)
        self.parser.add_rule(self.metrics_services_size_unit)