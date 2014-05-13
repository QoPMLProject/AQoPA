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
        metrics_services_param : SQLPARAN ENERGY COLON metrics_services_energy_type LPARAN metrics_services_energy_unit RPARAN SQRPARAN
                               | SQLPARAN ENERGY COLON LISTENING COLON EXACT LPARAN metrics_services_energy_unit RPARAN SQRPARAN
        """
        t[0] = self.builder.create_metrics_services_param_energy(t)
    
    def metrics_services_energy_param_type(self, t):
        """
        metrics_services_energy_type : EXACT
                                    | ALGORITHM
        """
        t[0] = t[1].lower()

    def metrics_services_energy_unit(self, t):
        """
        metrics_services_energy_unit : MA
        """
        t[0] = t[1].lower()

    def _extend(self):
        """ """

        self.parser.add_reserved_word('energy', 'ENERGY', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('exact', 'EXACT', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('listening', 'LISTENING', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('algorithm', 'ALGORITHM', state='metricsprimhead', case_sensitive=False)
        self.parser.add_reserved_word('mA', 'MA', state='metricsprimhead', case_sensitive=True)

        self.parser.add_rule(self.metrics_services_param_energy)
        self.parser.add_rule(self.metrics_services_energy_param_type)
        self.parser.add_rule(self.metrics_services_energy_unit)
