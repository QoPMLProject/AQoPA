#!/usr/bin/env python

from aqopa import module
from .gui import ModuleGui
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED
from .console import PrintResultsHook

"""
@file       __init__.py
@brief      initial file for the financialanalysis module
@author     Katarzyna Mazur
"""


class Module(module.Module):
    def __init__(self, energyanalysis_module):
        self.energyanalysis_module = energyanalysis_module
        self.consumption_costs = {}
        self.cost_per_kWh = 0

    def get_cost_per_kWh(self):
        return self.cost_per_kWh

    def set_cost_per_kWh(self, cost_per_kWh):
        self.cost_per_kWh = cost_per_kWh

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

    def __convert_to_joules(self, millijoules):
        return millijoules / 1000.0

    def __convert_to_kWh(self, joules):
        return joules / 3600000.0

    def calculate_cost(self, consumed_joules, cost_per_kWh):
        kWhs = self.__convert_to_kWh(consumed_joules)
        cost = kWhs * cost_per_kWh
        return cost

    def calculate_cost_for_host(self, simulator, host, cost_per_kWh):
        all_consumptions = self.get_all_hosts_consumption(simulator, simulator.context.hosts)
        joules = all_consumptions[host]['energy']
        cost_for_host = self.calculate_cost(joules, cost_per_kWh)
        return cost_for_host

    def calculate_all_costs(self, simulator, hosts, cost_per_kWh):
        all_costs = {}
        for host in hosts:
            all_costs[host] = self.calculate_cost_for_host(simulator, host, cost_per_kWh)
            self.add_cost(simulator, host, all_costs[host])
        return all_costs

    def add_cost(self, simulator, host, cost):
        """
        @brief adds cost of power consumption to
        the list of cost consumptions for the
        particular host present in the
        QoP-ML's model
        """
        # add a new simulator if not available yet
        if simulator not in self.consumption_costs:
            self.consumption_costs[simulator] = {}
        # add a new host if not available yet
        if host not in self.consumption_costs[simulator]:
            self.consumption_costs[simulator][host] = []
        # add cost for the host - but only if we
        # have not added it yet and if it is not 'empty'
        if cost not in self.consumption_costs[simulator][host] and cost:
            self.consumption_costs[simulator][host].append(cost)

    def get_min_cost(self, simulator, hosts):
        host = hosts[0]
        min_cost = self.consumption_costs[simulator][hosts[0]]
        for h in hosts:
            if self.consumption_costs[simulator][h] < min_cost:
                min_cost = self.consumption_costs[simulator][h]
                host = h
        return min_cost[0], host

    def get_max_cost(self, simulator, hosts):
        host = hosts[0]
        max_cost = self.consumption_costs[simulator][hosts[0]]
        for h in hosts:
            if self.consumption_costs[simulator][h] > max_cost:
                max_cost = self.consumption_costs[simulator][h]
                host = h
        return max_cost[0], host

    def get_avg_cost(self, simulator, hosts):
        cost_sum = 0.0
        i = 0
        for host in hosts:
            for cost in self.consumption_costs[simulator][host]:
                cost_sum += cost
                i += 1
        if i != 0:
            return cost_sum / i
        else:
            return 0

    def get_total_cost(self, simulator, hosts):
        cost_sum = 0.0
        for host in hosts:
            for cost in self.consumption_costs[simulator][host]:
                cost_sum += cost
        return cost_sum

    def get_all_costs(self, simulator):
        if simulator not in self.consumption_costs:
            return []
        return self.consumption_costs[simulator]

    # def set_all_costs(self, consumption_costs):
    # self.consumption_costs = copy.deepcopy(consumption_costs)

    def get_all_hosts_consumption(self, simulator, hosts):
        voltage = self.energyanalysis_module.get_voltage()
        consumptions = self.energyanalysis_module.get_hosts_consumptions(simulator, hosts, voltage)
        return consumptions