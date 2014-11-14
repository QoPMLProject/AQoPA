#!/usr/bin/env python

from aqopa import module
from .gui import ModuleGui
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION
from aqopa.module.energyanalysis.console import PrintResultsHook
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED

class Module(module.Module):

    def __init__(self, energyanalysis_module) :
        self.guis = {}
        self.energyanalysis_module = energyanalysis_module
        self.co2_per_kWh = 0.0

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)

    def _install(self, simulator):
        """
        """
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

    def get_co2_per_kWh(self):
        return self.co2_per_kWh

    def set_co2_per_kWh(self, co2):
        self.co2_per_kWh = co2

    def get_total_co2_consumption(self):
        pass