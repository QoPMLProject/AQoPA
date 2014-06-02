'''
Created on 01-06-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

from aqopa.model import MetricsServiceParam
from aqopa.model.parser.lex_yacc import LexYaccParserExtension


class Builder():
    
    def create_metrics_services_param_energy(self, token):
        """
        metrics_services_param : SQLPARAN ENERGY COLON metrics_services_energy_type LPARAN metrics_services_energy_unit RPARAN SQRPARAN
                               | SQLPARAN ENERGY COLON LISTENING COLON EXACT LPARAN metrics_services_energy_unit RPARAN SQRPARAN
        """
        if len(token) == 9:
            return MetricsServiceParam(token[2], token[4], token[6])
        else:
            param_name = token[4] + ':' + token[6]
            return MetricsServiceParam(token[2], param_name, token[6])

class ModelParserExtension(LexYaccParserExtension):
    """
    Extension for timeanalysis module communications time
    """

    #######################
    #  Communication Time
    #######################

    def sending_current_default_parameter(self, t):
        """
        medium_default_parameter : SENDING_CURRENT_DEFAULT_PARAMETER EQUAL comm_current_value
        """
        t[0] = {'default_sending_current': t[3]}

    def receiving_current_default_parameter(self, t):
        """
        medium_default_parameter : RECEIVING_CURRENT_DEFAULT_PARAMETER EQUAL comm_current_value
        """
        t[0] = {'default_receiving_current': t[3]}

    def listening_current_default_parameter(self, t):
        """
        medium_default_parameter : LISTENING_CURRENT_DEFAULT_PARAMETER EQUAL comm_current_value
        """
        t[0] = {'default_listening_current': t[3]}

    def topology_rule_sending_current_parameter(self, t):
        """
        topology_rule_parameter : SENDING_CURRENT_PARAMETER EQUAL comm_current_value
        """
        t[0] = {'sending_current': t[3]}

    def topology_rule_receiving_current_parameter(self, t):
        """
        topology_rule_parameter : RECEIVING_CURRENT_PARAMETER EQUAL comm_current_value
        """
        t[0] = {'receiving_current': t[3]}

    def topology_rule_listening_current_parameter(self, t):
        """
        topology_rule_parameter : LISTENING_CURRENT_PARAMETER EQUAL comm_current_value
        """
        t[0] = {'listening_current': t[3]}

    def comm_current_value(self, t):
        """
        comm_current_value : comm_current_metric
                            | comm_current_algorithm
        """
        t[0] = t[1]

    def comm_current_metric(self, t):
        """
        comm_current_metric : number comm_current_metric_unit
        """
        t[0] = {
            'type': 'metric',
            'value': t[1],
            'unit': t[2]
        }

    def comm_current_algorithm(self, t):
        """
        comm_current_algorithm : IDENTIFIER SQLPARAN comm_current_metric_unit SQRPARAN
                            | IDENTIFIER
        """
        unit = 'mA'
        if len(t) == 5:
            unit = t[3]
        t[0] = {
            'type': 'algorithm',
            'name': t[1],
            'unit': unit
        }

    def comm_current_metric_unit(self, t):
        """
        comm_current_metric_unit : MA
        """
        t[0] = t[1]

    def _extend(self):
        """ """

        self.parser.add_reserved_word('mA', 'MA', state='communication', case_sensitive=True)
        self.parser.add_reserved_word('default_sending_current', 'SENDING_CURRENT_DEFAULT_PARAMETER',
                                      state='communication',)
        self.parser.add_reserved_word('default_receiving_current', 'RECEIVING_CURRENT_DEFAULT_PARAMETER',
                                      state='communication',)
        self.parser.add_reserved_word('default_listening_current', 'LISTENING_CURRENT_DEFAULT_PARAMETER',
                                      state='communication',)
        self.parser.add_reserved_word('sending_current', 'SENDING_CURRENT_PARAMETER',
                                      state='communication',)
        self.parser.add_reserved_word('receiving_current', 'RECEIVING_CURRENT_PARAMETER',
                                      state='communication',)
        self.parser.add_reserved_word('listening_current', 'LISTENING_CURRENT_PARAMETER',
                                      state='communication',)

        self.parser.add_rule(self.sending_current_default_parameter)
        self.parser.add_rule(self.receiving_current_default_parameter)
        self.parser.add_rule(self.listening_current_default_parameter)
        self.parser.add_rule(self.topology_rule_sending_current_parameter)
        self.parser.add_rule(self.topology_rule_receiving_current_parameter)
        self.parser.add_rule(self.topology_rule_listening_current_parameter)
        self.parser.add_rule(self.comm_current_value)
        self.parser.add_rule(self.comm_current_metric)
        self.parser.add_rule(self.comm_current_algorithm)
        self.parser.add_rule(self.comm_current_metric_unit)

class ConfigParserExtension(LexYaccParserExtension):
    """
    Extension for timeanalysis module communications time
    """

    #######################
    #  Communication Time
    #######################

    def version_sending_current_default_parameter(self, t):
        """
        version_medium_default_parameter : SENDING_CURRENT_DEFAULT_PARAMETER EQUAL version_comm_current_value
        """
        t[0] = {'default_sending_current': t[3]}

    def version_receiving_current_default_parameter(self, t):
        """
        version_medium_default_parameter : RECEIVING_CURRENT_DEFAULT_PARAMETER EQUAL version_comm_current_value
        """
        t[0] = {'default_receiving_current': t[3]}

    def version_topology_rule_sending_current_parameter(self, t):
        """
        version_topology_rule_parameter : SENDING_CURRENT_PARAMETER EQUAL version_comm_current_value
        """
        t[0] = {'sending_current': t[3]}

    def version_topology_rule_receiving_current_parameter(self, t):
        """
        version_topology_rule_parameter : RECEIVING_CURRENT_PARAMETER EQUAL version_comm_current_value
        """
        t[0] = {'receiving_current': t[3]}

    def version_listening_current_default_parameter(self, t):
        """
        version_medium_default_parameter : LISTENING_CURRENT_DEFAULT_PARAMETER EQUAL version_comm_current_value
        """
        t[0] = {'default_listening_current': t[3]}

    def version_topology_rule_listening_current_parameter(self, t):
        """
        version_topology_rule_parameter : LISTENING_CURRENT_PARAMETER EQUAL version_comm_current_value
        """
        t[0] = {'listening_current': t[3]}

    def version_comm_current_value(self, t):
        """
        version_comm_current_value : version_comm_current_metric
                            | version_comm_current_algorithm
        """
        t[0] = t[1]

    def version_comm_current_metric(self, t):
        """
        version_comm_current_metric : number version_comm_current_metric_unit
        """
        t[0] = {
            'type': 'metric',
            'value': t[1],
            'unit': t[2]
        }

    def version_comm_current_algorithm(self, t):
        """
        version_comm_current_algorithm : IDENTIFIER SQLPARAN version_comm_current_metric_unit SQRPARAN
                                | IDENTIFIER
        """
        unit = 'mA'
        if len(t) == 5:
            unit = t[3]
        t[0] = {
            'type': 'algorithm',
            'name': t[1],
            'unit': unit
        }

    def version_comm_current_metric_unit(self, t):
        """
        version_comm_current_metric_unit : MA
        """
        t[0] = t[1]

    def _extend(self):
        """ """

        self.parser.add_reserved_word('mA', 'MA', state='versioncommunication', case_sensitive=True)
        self.parser.add_reserved_word('default_sending_current', 'SENDING_CURRENT_DEFAULT_PARAMETER',
                                      state='versioncommunication',)
        self.parser.add_reserved_word('default_receiving_current', 'RECEIVING_CURRENT_DEFAULT_PARAMETER',
                                      state='versioncommunication',)
        self.parser.add_reserved_word('default_listening_current', 'LISTENING_CURRENT_DEFAULT_PARAMETER',
                                      state='versioncommunication',)
        self.parser.add_reserved_word('sending_current', 'SENDING_CURRENT_PARAMETER',
                                      state='versioncommunication',)
        self.parser.add_reserved_word('receiving_current', 'RECEIVING_CURRENT_PARAMETER',
                                      state='versioncommunication',)
        self.parser.add_reserved_word('listening_current', 'LISTENING_CURRENT_PARAMETER',
                                      state='versioncommunication',)

        self.parser.add_rule(self.version_sending_current_default_parameter)
        self.parser.add_rule(self.version_receiving_current_default_parameter)
        self.parser.add_rule(self.version_topology_rule_sending_current_parameter)
        self.parser.add_rule(self.version_topology_rule_receiving_current_parameter)
        self.parser.add_rule(self.version_listening_current_default_parameter)
        self.parser.add_rule(self.version_topology_rule_listening_current_parameter)
        self.parser.add_rule(self.version_comm_current_value)
        self.parser.add_rule(self.version_comm_current_metric)
        self.parser.add_rule(self.version_comm_current_algorithm)
        self.parser.add_rule(self.version_comm_current_metric_unit)

class MetricsParserExtension(LexYaccParserExtension):
    """
    Extension for parsing energy analysis module's metrics
    """

    def __init__(self):
        LexYaccParserExtension.__init__(self)

        self.builder = Builder()


    ##################################
    #    Metrics energy consumption
    ##################################

    def metrics_services_param_energy(self, t):
        """
        metrics_services_param : SQLPARAN CURRENT COLON metrics_services_energy_type LPARAN metrics_services_energy_unit RPARAN SQRPARAN
        """
        t[0] = self.builder.create_metrics_services_param_energy(t)

    def metrics_services_energy_param_type(self, t):
        """
        metrics_services_energy_type : EXACT
        """
        t[0] = t[1].lower()

    def metrics_services_energy_unit(self, t):
        """
        metrics_services_energy_unit : MA
        """
        t[0] = t[1].lower()

    def _extend(self):
        """ """

        self.parser.add_reserved_word('current', 'CURRENT', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('exact', 'EXACT', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('mA', 'MA', state='metricsprimhead', case_sensitive=True)

        self.parser.add_rule(self.metrics_services_param_energy)
        self.parser.add_rule(self.metrics_services_energy_param_type)
        self.parser.add_rule(self.metrics_services_energy_unit)
