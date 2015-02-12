from aqopa import module
from aqopa.module.energyanalysis.console import PrintResultsHook
from aqopa.simulator.error import RuntimeException
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED
from .gui import ModuleGui
from aqopa.module.energyanalysis.parser import MetricsParserExtension, ConfigParserExtension, ModelParserExtension
from aqopa.model import WhileInstruction, AssignmentInstruction,\
    CallFunctionInstruction, CallFunctionExpression, IfInstruction

class Module(module.Module):
    """
    """
    
    def __init__(self, timeanalysis_module):
        """ """
        self.guis = {}                                  # Divided by simulators - the reason for dict
        self.timeanalysis_module = timeanalysis_module
        self.voltage = 0

    def get_voltage(self):
        return self.voltage

    def set_voltage(self, voltage):
        self.voltage = voltage

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)
    
    def extend_metrics_parser(self, parser):
        """
        Overridden
        """
        parser.add_extension(MetricsParserExtension())
        return parser

    def extend_model_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(ModelParserExtension())
        return parser

    def extend_config_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(ConfigParserExtension())
        return parser

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

    def _get_current_from_metric(self, metric, default=None):
        """
        Returns current in A
        """
        block = metric.block
        for i in range(0, len(block.service_params)):
            sparam = block.service_params[i]
            if sparam.service_name.lower() != "current":
                continue
            metric_type = sparam.param_name.lower()
            if metric_type != "exact":
                continue
            # metric_unit = sparam.unit - mA
            return float(metric.service_arguments[i]) / 1000.0
        return default

    def _get_current_for_expression(self, metrics_manager, host, expression):
        """
        Returns current (in A) from metric for cpu.
        """
        current = None
        
        # Get current metric for expression
        metric = metrics_manager.find_primitive(host, expression)
        if metric:
            current = self._get_current_from_metric(metric, default=None)

        # If metric not found, find default value    
        if current is None:
            expression = CallFunctionExpression('cpu')
            metric = metrics_manager.find_primitive(host, expression)
            if metric:
                current = self._get_current_from_metric(metric, default=None)

        if current is None:
            current = 0.0

        return current

    def _get_current_for_communication(self, context, host, channel, metric, message, receiver=None):
        """
        Returns current (in A) of sending/receiving'listening for a message
        """

        if metric['type'] == 'metric':
            metric_value = metric['value']
        elif metric['type'] == 'algorithm':
            algorithm_name = metric['name']
            if not context.algorithms_resolver.has_algorithm(algorithm_name):
                raise RuntimeException("Communication algorithm {0} undeclared.".format(algorithm_name))

            link_quality = context.channels_manager.get_router().get_link_quality(channel.tag_name,
                                                                                  message.sender,
                                                                                  receiver)
            alg = context.algorithms_resolver.get_algorithm(algorithm_name)
            variables = {
                'link_quality': link_quality,
                alg['parameter']: message.expression,
            }
            metric_value = context.algorithms_resolver.calculate(context, host, algorithm_name, variables)
        else:
            return 0
        # unit = metric['unit']
        # exact current (only mA)
        return metric_value / 1000.0

    def _get_current_sending_for_link(self, context, channel, sender, message, receiver):
        """
        Returns current (in A) of sending between sender and receiver.
        """
        metric = context.channels_manager.get_router().get_link_parameter_value('sending_current',
                                                                                channel.tag_name, sender, receiver)
        if metric is None:
            return 0.0
        return self._get_current_for_communication(context, sender, channel, metric, message, receiver)

    def _get_current_receiving_for_link(self, context, channel, sender, message, receiver):
        """
        Returns current (in A) of sending between sender and receiver.
        """
        metric = context.channels_manager.get_router().get_link_parameter_value('receiving_current',
                                                                                channel.tag_name, sender, receiver)
        if metric is None:
            return 0.0
        return self._get_current_for_communication(context, sender, channel, metric, message, receiver)

    def _get_current_waiting_for_link(self, context, channel, sender, message, receiver):
        """
        Returns current (in A) of sending between sender and receiver.
        """
        metric = context.channels_manager.get_router().get_link_parameter_value('listening_current',
                                                                                channel.tag_name, sender, receiver)
        if metric is None:
            return 0.0
        return self._get_current_for_communication(context, sender, channel, metric, message, receiver)

    def get_hosts_consumptions(self, simulator, hosts, voltage):
        """
        Calculates energy consumption of hosts.
        The unit of voltage is V (Volt).
        """

        def combine_waiting_time_tuples(unsorted_time_tuples):
            """
            Returns list of sorted time tuples (from, to) without overlapping.
            """
            unsorted_time_tuples.sort(key=lambda tt: tt[0])
            t_tuples = []
            if len(unsorted_time_tuples) > 0:
                current_time_from = unsorted_time_tuples[0][0]
                current_time_to = unsorted_time_tuples[0][1]
                current_current = unsorted_time_tuples[0][2]
                i = 0
                while i < len(unsorted_time_tuples):
                    t = unsorted_time_tuples[i]

                    # inside
                    # |---10---|
                    #   |-X--|
                    if t[0] >= current_time_from and t[1] <= current_time_to:
                        # if inside is more energy consuming
                        # |---10---|
                        #   |-15-|
                        if t[2] > current_current:
                            if t[0] > current_time_from:
                                t_tuples.append((current_time_from, t[0], current_current))
                            if current_time_to > t[1]:
                                new_tuple = (t[1], current_time_to, current_current)
                                added = False
                                j = i
                                while j < len(unsorted_time_tuples):
                                    tt = unsorted_time_tuples[j]
                                    if tt[0] > t[1]:
                                        unsorted_time_tuples.insert(j, new_tuple)
                                        added = True
                                        break
                                    j += 1
                                if not added:
                                    unsorted_time_tuples.append(new_tuple)

                            current_time_from = t[0]
                            current_time_to = t[1]
                            current_current = t[2]

                    # overlapping
                    # |---10--|
                    #       |--X--|
                    if t[0] < current_time_to and t[1] > current_time_to:

                        # Add left |---10|
                        if t[0] > current_time_from:
                            t_tuples.append((current_time_from, t[0], current_current))

                        # Add new tuple for right |X--|
                        new_tuple = (current_time_to, t[1], t[2])
                        added = False
                        j = i
                        while j < len(unsorted_time_tuples):
                            tt = unsorted_time_tuples[j]
                            if tt[0] > current_time_to:
                                unsorted_time_tuples.insert(j, new_tuple)
                                added = True
                                break
                            j += 1
                        if not added:
                            unsorted_time_tuples.append(new_tuple)

                        # Update currents
                        current_time_from = t[0]
                        current_time_to = current_time_to
                        current_current = max(current_current, t[2])

                    # later
                    # |---X--|
                    #           |-Y--|
                    if t[0] > current_time_to:
                        if current_time_to > current_time_from:
                            t_tuples.append((current_time_from, current_time_to, current_current))
                        current_time_from = t[0]
                        current_time_to = t[1]
                        current_current = t[2]
                    i += 1

                if current_time_to > current_time_from:
                    t_tuples.append((current_time_from, current_time_to, current_current))
            return t_tuples

        def calculate_consumptions_to_remove(waiting_tuples, transmitting_tuples):
            """
            Returns list of waiting tuples without times when host was transmitting.
            """
            consumptions = {
                'energy': 0.0,
                'amp-hour': 0.0,
            }
            for wtt in waiting_tuples:
                for ttt in transmitting_tuples:
                    # overlapping
                    if ttt[0] <= wtt[1] and ttt[1] >= wtt[0]:
                        time = 0

                        # inside
                        if ttt[0] >= wtt[0] and ttt[1] <= wtt[1]:
                            time = ttt[1] - ttt[0]

                        # oversize
                        if ttt[0] < wtt[0] and ttt[1] > wtt[1]:
                            time = wtt[1] - wtt[0]

                        # left side
                        if ttt[0] < wtt[0] and ttt[1] <= wtt[1]:
                            time = ttt[1] - wtt[0]

                        # right side
                        if ttt[0] >= wtt[0] and ttt[1] > wtt[1]:
                            time = wtt[1] - ttt[0]

                        consumptions['energy'] += voltage * wtt[2] * time / 1000.0
                        consumptions['amp-hour'] += wtt[2] * time / 1000.0 / 3600.0

            return consumptions

        metrics_manager = simulator.context.metrics_manager
        timetraces = self.timeanalysis_module.get_timetraces(simulator)

        # Clear results
        hosts_consumption = {}
        for h in hosts:
            hosts_consumption[h] = {
                'energy': 0.0,
                'amp-hour': 0.0,
            }

        # Traverse timetraces
        # Additionaly create list of finish times of instructions for each host
        # (List of times when instructions has been finished)  ze co

        for timetrace in timetraces:
            
            # Omit hosts that are not given in parameter
            if timetrace.host not in hosts:
                continue
            
            energy_consumption = 0.0
            amp_hour = 0.0
            # Get expressions from timetrace
            for simple_expression, time in timetrace.expressions_details:
                current = self._get_current_for_expression(metrics_manager, timetrace.host, simple_expression)
                # Calculate consumption
                energy_consumption += voltage * current * time
                amp_hour = current * time / 3600.0
                # print timetrace.host.name, 'cpu', unicode(simple_expression), current, time, voltage * time * current
            hosts_consumption[timetrace.host]['energy'] += energy_consumption
            hosts_consumption[timetrace.host]['amp-hour'] += amp_hour
            
        # Traverse channel traces
        # Look for times when host was waiting for message or sending a message

        channels_traces = self.timeanalysis_module.get_all_channel_message_traces(simulator)
        for channel in channels_traces:
            channel_traces = channels_traces[channel]

            host_channel_transmission_time_tuples = {}  # Keeps list of tuples when host was transmitting message
            host_channel_waiting_time_tuples = {}  # Keeps list of tuples when host was waiting for message

            # Traverse each trace and get the time of waiting
            for trace in channel_traces:

                # Add sending energy consumption for sender
                if trace.sender in hosts:
                    current_sending = self._get_current_sending_for_link(simulator.context, channel,
                                                                              trace.sender, trace.message,
                                                                              trace.receiver)
                    energy_consumption = (voltage * current_sending * trace.sending_time / 1000.0)
                    amp_hour = current_sending * trace.sending_time / 1000.0 / 3600.0
                    hosts_consumption[trace.sender]['energy'] += energy_consumption
                    hosts_consumption[trace.sender]['amp-hour'] += amp_hour

                    if trace.sender not in host_channel_transmission_time_tuples:
                        host_channel_transmission_time_tuples[trace.sender] = []
                    host_channel_transmission_time_tuples[trace.sender].append((trace.sent_at,
                                                                                trace.sent_at + trace.sending_time))

                # Add time tuple for receiver if he is in asked hosts
                if trace.receiver in hosts:
                    current_receiving = self._get_current_receiving_for_link(simulator.context, channel,
                                                                                trace.sender, trace.message,
                                                                                trace.receiver)
                    energy_consumption = voltage * current_receiving * trace.receiving_time / 1000.0
                    amp_hour = current_receiving * trace.receiving_time / 1000.0 / 3600.0
                    hosts_consumption[trace.receiver]['energy'] += energy_consumption
                    hosts_consumption[trace.receiver]['amp-hour'] += amp_hour

                    if trace.receiver not in host_channel_waiting_time_tuples:
                        host_channel_waiting_time_tuples[trace.receiver] = []

                    current_listening = self._get_current_waiting_for_link(simulator.context, channel,
                                                                           trace.sender, trace.message, trace.receiver)
                    host_channel_waiting_time_tuples[trace.receiver].append((trace.started_waiting_at,
                                                                             trace.started_receiving_at,
                                                                             current_listening))
                    if trace.receiver not in host_channel_transmission_time_tuples:
                        host_channel_transmission_time_tuples[trace.receiver] = []
                    host_channel_transmission_time_tuples[trace.receiver].append((trace.started_receiving_at,
                                                                                  trace.started_receiving_at
                                                                                  + trace.receiving_time))

            for host in hosts:

                # Handle waiting tuples
                if host in host_channel_waiting_time_tuples:
                    waiting_tuples = combine_waiting_time_tuples(host_channel_waiting_time_tuples[host])

                    # Calculate consumption when host theoretically was waiting
                    # but in fact it was sending or receiving message
                    # This value will be removed from host's consumption
                    consumptions_to_remove = {
                        'energy': 0.0,
                        'amp-hour': 0.0,
                    }
                    if host in host_channel_transmission_time_tuples:
                        consumptions_to_remove = calculate_consumptions_to_remove(
                            waiting_tuples, host_channel_transmission_time_tuples[host])

                    # Add waiting consumption
                    for tf, tt, c in waiting_tuples:
                        energy_consumption = voltage * c * (tt-tf) / 1000.0
                        amp_hour = voltage * c * (tt-tf) / 1000.0 / 3600.0
                        hosts_consumption[host]['energy'] += energy_consumption
                        hosts_consumption[host]['amp-hour'] += amp_hour

                    # Remove surplus consumption
                    hosts_consumption[host]['energy'] -= consumptions_to_remove['energy']
                    hosts_consumption[host]['amp-hour'] -= consumptions_to_remove['amp-hour']

        return hosts_consumption
            

