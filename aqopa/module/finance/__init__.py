#!/usr/bin/env python

from aqopa import module
from aqopa import module
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION
from .gui import ModuleGui
from .console import PrintResultsHook
from .hook import PreInstructionHook

"""
@file       __init__.py
@brief      initial file for the finance module
@author     Katarzyna Mazur
"""

class Module(module.Module):

    def __init__(self):

        self.power = 0
        self.usage_time = 0
        self.price_per_kWh = 0
        self.final_cost = 0

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)

    def _install(self, simulator):
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