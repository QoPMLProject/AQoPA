#!/usr/bin/env python

from aqopa import module
from aqopa import module
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION

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
