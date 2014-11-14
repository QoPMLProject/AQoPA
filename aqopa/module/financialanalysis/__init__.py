#!/usr/bin/env python

from aqopa import module
from .gui import ModuleGui
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION
from aqopa.module.energyanalysis.console import PrintResultsHook
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED

"""
@file       __init__.py
@brief      initial file for the financialanalysis module
@author     Katarzyna Mazur
"""


class Module(module.Module):
    def __init__(self, energyanalysis_module):
        self.guis = {}
        self.energyanalysis_module = energyanalysis_module
        self.consumption_costs = {}

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

    def get_all_hosts_consumption(self, simulator):
        hosts = simulator.context.hosts
        voltage = self.energyanalysis_module.get_voltage()
        consumptions = self.energyanalysis_module.get_hosts_consumptions(simulator, hosts, voltage)
        return consumptions
        # lblText = ""
        # for h in hosts:
        #     lblText += "%s: %.2f mJ" % (h.name, consumptions[h])
        # print lblText