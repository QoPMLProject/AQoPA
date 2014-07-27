#!/usr/bin/env python

from aqopa import module
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION
from .gui import ModuleGui
from .console import PrintResultsHook
from .hook import PreInstructionHook

"""
@file       __init__.py
@brief      initial file for the qop module
@author     Katarzyna Mazur
"""

class Module(module.Module):

    def __init__(self):

        # all available facts in a host, format, simulator is the dict's key:
        # { simulator: {host0: [f1,f2, ... fn], host1: [f1,f2, ..., fm]} }
        self.occuredFacts = {}

        # all occured facts in a host, format, simulator is the dict's key:
        # { simulator: {host0: [f1,f2, ... fn], host1: [f1,f2, ..., fm]} }
        self.allFacts = {}

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

    def add_new_fact(self, simulator, host, fact):
        """
        @brief adds a new fact to the list of all facts
        for the particular host present in the
        QoP-ML's model
        """
        # add a new simulator if not available yet
        if simulator not in self.allFacts:
            self.allFacts[simulator] = {}
        # add a new host if not available yet
        if host not in self.allFacts[simulator] :
            self.allFacts[simulator][host] = []
        # add a new fact for the host - but only if we
        # have not added it yet and if it is not empty
        if str(fact) not in self.allFacts[simulator][host] and str(fact) != '[]' and str(fact) != 'None':
            self.allFacts[simulator][host].append(str(fact).replace("'",""))

    def get_all_facts(self, simulator, host):
        """
        @brief gets a list of all available facts
        for the particular host present in the
        QoP-ML's model
        """
        if simulator not in self.allFacts:
            self.allFacts[simulator] = {}
        if host not in self.allFacts[simulator]:
            self.allFacts[simulator][host] = []
        return self.allFacts[simulator][host]

    def add_occured_fact(self, simulator, host, fact):
        """
        @brief adds a new, occured fact to the list
        of occured facts for the particular host
        present in the QoP-ML's model
        """
        # add a new simulator if not available yet
        if simulator not in self.occuredFacts:
            self.occuredFacts[simulator] = {}
        # add a new host if not available yet
        if host not in self.occuredFacts[simulator] :
            self.occuredFacts[simulator][host] = []
        # add a new fact for the host
        self.occuredFacts[simulator][host].append(fact)

    def get_occured_facts(self, simulator, host) :
        """
        @brief gets a list of all occured facts
        for the particular host present in the
        QoP-ML's model
        """
        if simulator not in self.occuredFacts:
            self.occuredFacts[simulator] = {}
        if host not in self.occuredFacts[simulator]:
            self.occuredFacts[simulator][host] = []
        return self.occuredFacts[simulator][host]