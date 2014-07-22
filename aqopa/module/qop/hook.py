#!/usr/bin/env python

from aqopa.simulator.state import Hook

"""
@file       hook.py
@author     Katarzyna Mazur
"""

class PreInstructionHook(Hook):

    """
    Execution hook executed before default core execution of each instruction.
    Returns execution result.
    """

    def __init__(self, module, simulator):
        """ """
        self.module = module
        self.simulator = simulator

    def execute(self, context, **kwargs):
        """
        """
        instruction = context.get_current_instruction()