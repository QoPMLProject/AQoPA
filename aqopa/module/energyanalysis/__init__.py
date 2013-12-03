from aqopa import module
from .gui import ModuleGui
from aqopa.module.energyanalysis.parser import MetricsParserExtension

class Module(module.Module):
    """
    """
    
    def __init__(self):
        """ """
        self.guis           = {}        # Divided by simulators - the reason for dict
        

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)
    
    def extend_metrics_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(MetricsParserExtension())
        return parser
    
    def _install(self, simulator):
        """
        """
        return simulator
    
    def install_console(self, simulator):
        """ Install module for console simulation """
        self._install(simulator)
        return simulator
        
    def install_gui(self, simulator):
        """ Install module for gui simulation """
        self._install(simulator)
        return simulator
