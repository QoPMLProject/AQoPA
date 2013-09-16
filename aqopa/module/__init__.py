#Module abstract

class Module():
    """
    Abstract class of module
    """
    
    def get_gui(self):
        """
        Method returns class that is used by GUI version of AQoPA.
        """
        return None
    
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
    
    def install_console(self, simulator):
        """
        Method is called before running simulation in console mode.
        Module installs itself in simulator. 
        It can register hooks, executors, etc.
        """
        return simulator
    
    def install_gui(self, simulator):
        """
        Method is called before running simulation in GUI mode.
        Module installs itself in simulator. 
        It can register hooks, executors, etc.
        """
        return simulator