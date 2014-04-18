from copy import copy, deepcopy
from aqopa import module
from aqopa.module.reputation.hook import PreInstructionHook
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION
from aqopa.model import CallFunctionExpression
from .parser import MetricsParserExtension, ModelParserExtension
from .gui import ModuleGui
from .console import PrintResultsHook

class Module(module.Module):
    """
    """
    
    def __init__(self):
        """ """
        self.guis = {}  # Divided by simulators - the reason for dict

        self.init_vars = {}  # Divided by name - the reason for dict
        self.algorithms = {}  # Divided by name - the reason for dict

        self.reputation_vars = {}  # Divided by hosts - the reason for dict

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

    def extend_model_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(ModelParserExtension(self))
        return parser
    
    def _install(self, simulator):
        """
        """
        hook = PreInstructionHook(self, simulator)
        simulator.register_hook(HOOK_TYPE_PRE_INSTRUCTION_EXECUTION, hook)
        return simulator
    
    def install_console(self, simulator):
        """ Install module for console simulation """
        self._install(simulator)
        hook = PrintResultsHook(self, simulator)
        simulator.register_hook(HOOK_TYPE_SIMULATION_FINISHED, hook)
        return simulator
        
    def install_gui(self, simulator):
        """ Install module for gui simulation """
        self._install(simulator)
        return simulator

    def get_algorithm(self, name):
        """
        Returns algorithm by name.
        """
        return deepcopy(self.algorithms[name])

    def set_reputation_var(self, host, var, val):
        """ """
        if host not in self.reputation_vars:
            self.reputation_vars[host] = {}
        self.reputation_vars[host][var] = val

    def get_host_vars(self, host):
        """
        """
        if host not in self.reputation_vars:
            return {}
        return copy(self.reputation_vars[host])


