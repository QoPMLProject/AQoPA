#!/usr/bin/env python

"""
@file       __init__.py
@brief      initial file for the qop module
@author     Katarzyna Mazur
"""

from aqopa import module
from .gui import ModuleGui

class Module(module.Module):

    def __init__(self):
        self.occuredFacts = []
        self.allFacts = []

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)

    def _install(self, simulator):
        """
        """
        return simulator

    def install_console(self, simulator):
        # """ Install module for console simulation """
        self._install(simulator)
        # hook = PrintResultsHook(self, simulator)
        # simulator.register_hook(HOOK_TYPE_SIMULATION_FINISHED, hook)
        return simulator

    def install_gui(self, simulator):
        """ Install module for gui simulation """
        self._install(simulator)
        return simulator