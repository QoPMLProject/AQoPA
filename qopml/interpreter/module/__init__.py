#Module abstract

class Module():
    """
    Abstract class of module
    """
    
    def extend_parser(self, parser):
        """
        This method is called before parsing the qopml model.
        Module can extend parser and add tokens, rules, etc.
        Method returns parser.
        """
        return parser