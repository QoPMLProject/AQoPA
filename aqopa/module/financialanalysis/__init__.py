#!/usr/bin/env python

from aqopa import module
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION

"""
@file       __init__.py
@brief      initial file for the financialanalysis module
@author     Katarzyna Mazur
"""

class Module(module.Module):

    def __init__(self) :
        pass

    def calculate(self):
        """
        @brief calculates the total cost ($) of the host
        usage, its quite simple math:
        1) Watts / 1000 = X kWatts
        2) X kWatts * Y hours = Z kWh
        3) $/kWh * Z kWh = final cost
        """
