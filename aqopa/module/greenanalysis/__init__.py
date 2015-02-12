#!/usr/bin/env python

from aqopa import module
from .gui import ModuleGui
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED
from .console import PrintResultsHook

class Module(module.Module):
    def __init__(self, energyanalysis_module):
        self.energyanalysis_module = energyanalysis_module
        self.carbon_dioxide_emissions = {}
        self.pounds_of_co2_per_kWh = 0

    def get_pounds_of_co2_per_kWh(self):
        return self.pounds_of_co2_per_kWh

    def set_pounds_of_co2_per_kWh(self, pounds_of_co2_per_kWh):
        self.pounds_of_co2_per_kWh = pounds_of_co2_per_kWh

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

    def calculate_emission(self, consumed_joules, pounds_of_co2_per_kWh):
        kWhs = self.__convert_to_kWh(consumed_joules)
        pounds = kWhs * pounds_of_co2_per_kWh
        return pounds

    def calculate_emission_for_host(self, simulator, host, pounds_of_co2_per_kWh):
        all_consumptions = self.get_all_hosts_consumption(simulator)
        joules = all_consumptions[host]['energy']
        pounds_for_host = self.calculate_emission(joules, pounds_of_co2_per_kWh)
        return pounds_for_host

    def calculate_all_emissions(self, simulator, hosts, pounds_of_co2_per_kWh):
        all_emissions = {}
        for host in hosts:
            all_emissions[host] = self.calculate_emission_for_host(simulator, host, pounds_of_co2_per_kWh)
            self.add_co2_emission(simulator, host, all_emissions[host])
        return all_emissions

    def add_co2_emission(self, simulator, host, co2_emission):
        # add a new simulator if not available yet
        if simulator not in self.carbon_dioxide_emissions:
            self.carbon_dioxide_emissions[simulator] = {}
        # add a new host if not available yet
        if host not in self.carbon_dioxide_emissions[simulator]:
            self.carbon_dioxide_emissions[simulator][host] = []
        # add he amount of released carbon dioxide for the
        # host - but only if we have not added it yet and
        # if it is not 'empty'
        if co2_emission not in self.carbon_dioxide_emissions[simulator][host] and co2_emission:
            self.carbon_dioxide_emissions[simulator][host].append(co2_emission)

    def get_min_emission(self, simulator, hosts):
        host = hosts[0]
        min_cost = self.carbon_dioxide_emissions[simulator][hosts[0]]
        for h in hosts:
            if self.carbon_dioxide_emissions[simulator][h] < min_cost:
                min_cost = self.carbon_dioxide_emissions[simulator][h]
                host = h
        return min_cost[0], host

    def get_max_emission(self, simulator, hosts):
        host = hosts[0]
        max_cost = self.carbon_dioxide_emissions[simulator][hosts[0]]
        for h in hosts:
            if self.carbon_dioxide_emissions[simulator][h] > max_cost:
                max_cost = self.carbon_dioxide_emissions[simulator][h]
                host = h
        return max_cost[0], host

    def get_avg_emission(self, simulator, hosts):
        cost_sum = 0.0
        i = 0
        for host in hosts:
            for cost in self.carbon_dioxide_emissions[simulator][host]:
                cost_sum += cost
                i += 1
        if i != 0 :
            return cost_sum / i
        else :
            return 0

    def get_total_emission(self, simulator, hosts):
        cost_sum = 0.0
        for host in hosts:
            for cost in self.carbon_dioxide_emissions[simulator][host]:
                cost_sum += cost
        return cost_sum

    def get_all_emissions(self, simulator):
        if simulator not in self.carbon_dioxide_emissions:
            return []
        return self.carbon_dioxide_emissions[simulator]

    def get_all_hosts_consumption(self, simulator):
        hosts = simulator.context.hosts
        voltage = self.energyanalysis_module.get_voltage()
        consumptions = self.energyanalysis_module.get_hosts_consumptions(simulator, hosts, voltage)
        return consumptions
