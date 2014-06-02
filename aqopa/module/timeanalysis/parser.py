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


class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for timeanalysis module communications time
    """

    #######################
    #  Communication Time
    #######################

    def time_default_parameter(self, t):
        """
        medium_default_parameter : TIME_DEFAULT_PARAMETER EQUAL comm_time_value
        """
        t[0] = {'default_time': t[3]}

    def topology_rule_time_parameter(self, t):
        """
        topology_rule_parameter : TIME_PARAMETER EQUAL comm_time_value
        """
        t[0] = {'time': t[3]}

    def comm_time_value(self, t):
        """
        comm_time_value : comm_time_metric
                            | comm_time_algorithm
        """
        t[0] = t[1]

    def comm_time_metric(self, t):
        """
        comm_time_metric : number comm_time_metric_unit
        """
        t[0] = {
            'type': 'metric',
            'value': t[1],
            'unit': t[2]
        }

    def comm_time_algorithm(self, t):
        """
        comm_time_algorithm : IDENTIFIER SQLPARAN comm_time_metric_unit SQRPARAN
                        | IDENTIFIER
        """
        unit = 'ms'
        if len(t) == 5:
            unit = t[3]
        t[0] = {
            'type': 'algorithm',
            'name': t[1],
            'unit': unit
        }

    def comm_time_metric_unit(self, t):
        """
        comm_time_metric_unit : MS
                                | MSPBIT
                                | MSPBYTE
                                | KBYTEPS
                                | MBYTEPS
        """
        t[0] = t[1]

    def _extend(self):
        """ """

        self.parser.add_reserved_word('ms', 'MS', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('mspb', 'MSPBIT', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('mspB', 'MSPBYTE', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('kbps', 'KBYTEPS', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('mbps', 'MBYTEPS', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('default_time', 'TIME_DEFAULT_PARAMETER', state='communication',)
        self.parser.add_reserved_word('time', 'TIME_PARAMETER', state='communication',)

        self.parser.add_rule(self.time_default_parameter)
        self.parser.add_rule(self.topology_rule_time_parameter)
        self.parser.add_rule(self.comm_time_value)
        self.parser.add_rule(self.comm_time_metric)
        self.parser.add_rule(self.comm_time_metric_unit)
        self.parser.add_rule(self.comm_time_algorithm)


class ConfigParserExtension(LexYaccParserExtension):
    """
    Extension for timeanalysis module communications time
    """

    #######################
    #  Communication Time
    #######################

    def version_time_default_parameter(self, t):
        """
        version_medium_default_parameter : TIME_DEFAULT_PARAMETER EQUAL version_comm_time_value
        """
        t[0] = {'default_time': t[3]}

    def version_topology_rule_time_parameter(self, t):
        """
        version_topology_rule_parameter : TIME_PARAMETER EQUAL version_comm_time_value
        """
        t[0] = {'time': t[3]}

    def version_comm_time_value(self, t):
        """
        version_comm_time_value : version_comm_time_metric
                            | version_comm_time_algorithm
        """
        t[0] = t[1]

    def version_comm_time_metric(self, t):
        """
        version_comm_time_metric : number version_comm_time_metric_unit
        """
        t[0] = {
            'type': 'metric',
            'value': t[1],
            'unit': t[2]
        }

    def version_comm_time_algorithm(self, t):
        """
        version_comm_time_algorithm : IDENTIFIER SQLPARAN version_comm_time_metric_unit SQRPARAN
                                | IDENTIFIER
        """
        unit = 'ms'
        if len(t) == 5:
            unit = t[3]
        t[0] = {
            'type': 'algorithm',
            'name': t[1],
            'unit': unit
        }

    def version_comm_time_metric_unit(self, t):
        """
        version_comm_time_metric_unit : MS
                                | MSPBIT
                                | MSPBYTE
                                | KBYTEPS
                                | MBYTEPS
        """
        t[0] = t[1]

    def _extend(self):
        """ """

        self.parser.add_reserved_word('ms', 'MS', state='versioncommunication', case_sensitive=True)
        self.parser.add_reserved_word('mspb', 'MSPBIT', state='versioncommunication', case_sensitive=True)
        self.parser.add_reserved_word('mspB', 'MSPBYTE', state='versioncommunication', case_sensitive=True)
        self.parser.add_reserved_word('kbps', 'KBYTEPS', state='versioncommunication', case_sensitive=True)
        self.parser.add_reserved_word('mbps', 'MBYTEPS', state='versioncommunication', case_sensitive=True)
        self.parser.add_reserved_word('default_time', 'TIME_DEFAULT_PARAMETER', state='versioncommunication',)
        self.parser.add_reserved_word('time', 'TIME_PARAMETER', state='versioncommunication',)

        self.parser.add_rule(self.version_time_default_parameter)
        self.parser.add_rule(self.version_topology_rule_time_parameter)
        self.parser.add_rule(self.version_comm_time_value)
        self.parser.add_rule(self.version_comm_time_metric)
        self.parser.add_rule(self.version_comm_time_metric_unit)
        self.parser.add_rule(self.version_comm_time_algorithm)

class MetricsParserExtension(LexYaccParserExtension):
    """
    Extension for parsing timeanalysis module metrics
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
                                | ALGORITHM
        """
        t[0] = t[1].lower()

    def metrics_services_time_two_params_type(self, t):
        """
        metrics_services_time_two_params_type : BLOCK
        """
        t[0] = t[1].lower()
    
    def metrics_services_time_unit(self, t):
        """
        metrics_services_time_unit : S
                                | MS
                                | MSPBIT
                                | MSPBYTE
                                | KBYTEPS
                                | MBYTEPS
        """
        t[0] = t[1]

    def metrics_services_exact_time_unit(self, t):
        """
        metrics_services_exact_time_unit : S
                                        | MS
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
        self.parser.add_reserved_word('s', 'S', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('ms', 'MS', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('mspb', 'MSPBIT', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('mspB', 'MSPBYTE', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('kbps', 'KBYTEPS', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('mbps', 'MBYTEPS', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('algorithm', 'ALGORITHM', state='metricsprimhead', case_sensitive=True)

        self.parser.add_reserved_word('block', 'BLOCK', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('b', 'b', state='metricsprimhead', case_sensitive=True)
        self.parser.add_reserved_word('B', 'B', state='metricsprimhead', case_sensitive=True)
        
        self.parser.add_rule(self.metrics_services_param_time)
        self.parser.add_rule(self.metrics_services_time_one_param_type)
        self.parser.add_rule(self.metrics_services_time_two_params_type)
        self.parser.add_rule(self.metrics_services_time_unit)
        self.parser.add_rule(self.metrics_services_exact_time_unit)
        self.parser.add_rule(self.metrics_services_size_unit)