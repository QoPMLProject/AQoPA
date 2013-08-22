#Module abstract

class Module():
    """
    Abstract class of module
    """
    
    def extend_model_parser(self, parser):
        """
        Method is called before parsing the qopml model file.
        Module can extend parser and add tokens, rules, etc.
        Method returns parser.
        """
        return parser
    
    def extend_metrics_parser(self, parser):
        """
        Method is called before parsing the qopml metrics file.
        Module can extend parser and add tokens, rules, etc.
        Method returns parser.
        """
        return parser
    
    def extend_config_parser(self, parser):
        """
        Method is called before parsing the qopml config file.
        Module can extend parser and add tokens, rules, etc.
        Method returns parser.
        """
        return parser
    
    def install(self, simulator):
        """
        Method is called before running simulation.
        Module installs itself in simulator. 
        It can register hooks, executors, etc.
        """
        return simulator