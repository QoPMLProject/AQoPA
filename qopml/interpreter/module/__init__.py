#Module abstract

class Module():
    """
    Abstract class of module
    """
    
    def extend_parser(self, parser):
        """
        Method is called before parsing the qopml model.
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