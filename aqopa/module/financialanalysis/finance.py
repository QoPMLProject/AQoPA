#!/usr/bin/env python

"""
@file       finance.py
@brief      initial file for the financialanalysis module
@author     Katarzyna Mazur
"""

class Finance() :

    def __init__(self, watts=0, usage_time=0, price_per_kWh=0, final_cost = 0) :
        self.watts = watts
        self.usage_time = usage_time
        self.price_per_kWh = price_per_kWh
        self.final_cost = final_cost

