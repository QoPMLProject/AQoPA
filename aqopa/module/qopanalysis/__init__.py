#!/usr/bin/env python

from aqopa import module
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION
from .gui import ModuleGui
from .console import PrintResultsHook
from .hook import PreInstructionHook

"""
@file       __init__.py
@brief      initial file for the qopanalysis module
@author     Katarzyna Mazur
"""

class Module(module.Module):

    def __init__(self):

        # all occured facts in a host, format: (simulator is the dict's key):
        # { simulator: {host0: [f1,f2, ... fn], host1: [f1,f2, ..., fm]} }
        self.occured_facts = {}

        # all facts in a model
        self.all_facts = []

        # qopanalysis params list in a host, format: (simulator is the dict's key):
        # { simulator: {host0: [[qop1, qop2, ..., qopn], ..., [qop1, qop2, ..., qopm]], host1: [[qop1, qop2, ..., qopk], ...,  [qop1, qop2, ..., qopx]]} }
        self.qopParams = {}

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

    def get_all_facts(self):
        """
        @brief returns a list which contains
        all the facts available in a model
        """
        return self.all_facts

    def set_all_facts(self, facts_list):
        """
        @brief sets all facts for the loaded
        model
        """
        self.all_facts = facts_list[:]

    def add_occured_fact(self, simulator, host, fact):
        """
        @brief adds a new, occured fact to the list
        of occured facts for the particular host
        present in the QoP-ML's model
        """
        # add a new simulator if not available yet
        if simulator not in self.occured_facts:
            self.occured_facts[simulator] = {}
        # add a new host if not available yet
        if host not in self.occured_facts[simulator] :
            self.occured_facts[simulator][host] = []
        # add a new fact for the host - but only if we
        # have not added it yet and if it is not empty
        if str(fact) not in self.occured_facts[simulator][host] and fact:
            # if the fact is actually a list of facts,
            if type(fact) is list:
                # add all the elements from the facts list
                for f in fact :
                    if str(f) not in self.occured_facts[simulator][host]:
                        self.occured_facts[simulator][host].append(str(f))
            else:
                self.occured_facts[simulator][host].append(str(fact))

    def get_occured_facts(self, simulator, host) :
        """
        @brief gets a list of all occured facts
        for the particular host present in the
        QoP-ML's model
        """
        if simulator not in self.occured_facts:
            self.occured_facts[simulator] = {}
        if host not in self.occured_facts[simulator]:
            self.occured_facts[simulator][host] = []
        return self.__make_list_flat(self.occured_facts[simulator][host])

    def get_qop_params(self):
        pass

    def add_qop_param(self):
        pass

    def __make_list_flat(self, l) :
        """
        @brief sometimes an element of the list
        might be a list too, so we need to flat
        the list given in the argument and return
        the oblate list
        """
        ans = []
        for i in l:
            if type(i) is list:
                ans = self.__make_list_flat(i)
            else:
                ans.append(i)
        return ans