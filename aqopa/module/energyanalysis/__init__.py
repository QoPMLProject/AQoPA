from aqopa import module
from .gui import ModuleGui
from aqopa.module.energyanalysis.parser import MetricsParserExtension

class Module(module.Module):
    """
    """
    
    def __init__(self, timeanalysis_module):
        """ """
        self.guis = {}                                  # Divided by simulators - the reason for dict
        self.timeanalysis_module = timeanalysis_module

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

    def get_hosts_consumptions(self, simulator, hosts):
        """
        """
        metrics_manager = simulator.context.metrics_manager
        timetraces = self.timeanalysis_module.timetraces[simulator]

        # Clear results
        hosts_consumption = {}
        for h in hosts:
            hosts_consumption[h] = 0.0

        for timetrace in timetraces:

