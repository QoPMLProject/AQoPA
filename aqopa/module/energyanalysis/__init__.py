from aqopa import module
from aqopa.module.energyanalysis.console import PrintResultsHook
from aqopa.simulator.state import HOOK_TYPE_SIMULATION_FINISHED
from .gui import ModuleGui
from aqopa.module.energyanalysis.parser import MetricsParserExtension
from aqopa.model import WhileInstruction, AssignmentInstruction,\
    CallFunctionInstruction, CallFunctionExpression, IfInstruction

class Module(module.Module):
    """
    """
    
    def __init__(self, timeanalysis_module):
        """ """
        self.guis = {}                                  # Divided by simulators - the reason for dict
        self.timeanalysis_module = timeanalysis_module

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)
    
    def extend_metrics_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(MetricsParserExtension())
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

    def _get_current_for_expression(self, metrics_manager, host, expression):
        """
        Returns current from metric for cpu.
        """
        current = None
        
        # Get current metric for expression
        metric = metrics_manager.find_primitive(host, expression)
        if metric:
            block = metric.block
            
            for i in range(0, len(block.service_params)):
                sparam = block.service_params[i]
                
                if sparam.service_name.lower() != "energy":
                    continue

                metric_type = sparam.param_name.lower()
                
                if metric_type != "current":
                    continue
                
                # metric_unit = sparam.unit - mA
                
                current = float(metric.service_arguments[i])
            
        # If metric not found, find default value    
        if current is None:
            expression = CallFunctionExpression('cpu')
            metric = metrics_manager.find_primitive(host, expression)
            if metric:
                block = metric.block
                
                for i in range(0, len(block.service_params)):
                    sparam = block.service_params[i]
                    
                    if sparam.service_name.lower() != "energy":
                        continue
    
                    metric_type = sparam.param_name.lower()
                    
                    if metric_type != "current":
                        continue
                    
                    # metric_unit = sparam.unit - mA
                    
                    current = float(metric.service_arguments[i])
        
        if current is None:
            current = 0

        return current

    def _get_current_from_metric(self, metric):
        """
        """
        block = metric.block
        for i in range(0, len(block.service_params)):
            sparam = block.service_params[i]
            if sparam.service_name.lower() != "energy":
                continue
            metric_type = sparam.param_name.lower()
            if metric_type != "current":
                continue
            # metric_unit = sparam.unit - mA
            return float(metric.service_arguments[i])
        return 0.0

    def _get_current_sending_for_host(self, metrics_manager, host, channel):
        """
        Returns current from metric for radion in listening state.
        """
        metric = None
        if channel.tag_name is not None:
            expression = CallFunctionExpression('out', [], [channel.tag_name])
            metric = metrics_manager.find_primitive(host, expression)
        if not metric:
            expression = CallFunctionExpression('out', [], [])
            metric = metrics_manager.find_primitive(host, expression)
        if metric:
            return self._get_current_from_metric(metric)
        return 0.0

    def _get_current_waiting_for_host(self, metrics_manager, host, channel):
        """
        Returns current from metric for radion in listening state.
        """
        metric = None
        if channel.tag_name is not None:
            expression = CallFunctionExpression('in', [], [channel.tag_name])
            metric = metrics_manager.find_primitive(host, expression)
        if not metric:
            expression = CallFunctionExpression('in', [], [])
            metric = metrics_manager.find_primitive(host, expression)
        if metric:
            return self._get_current_from_metric(metric)
        return 0.0

    def get_hosts_consumptions(self, simulator, hosts, voltage):
        """
        """
        metrics_manager = simulator.context.metrics_manager

        timetraces = self.timeanalysis_module.get_timetraces(simulator)

        # Clear results
        hosts_consumption = {}
        for h in hosts:
            hosts_consumption[h] = 0.0

        # Traverse timetraces
        # Additionaly create list of finish times of instructions for each host
        # (List of times when instructions has been finished)  

        for timetrace in timetraces:
            
            # Omit hosts that are not given in parameter
            if timetrace.host not in hosts:
                continue
            
            # Get time from timetrace
            time_sec = timetrace.length / 1000.0
            
            consumption = 0.0
            # Get expressions from timetrace
            for simple_expression, time in timetrace.expressions_details:
                current = self._get_current_for_expression(metrics_manager, timetrace.host, simple_expression)
            
                # Calculate consumption
                consumption = voltage * current * time_sec
                
            hosts_consumption[timetrace.host] += consumption / 1000000.0
            
        # Traverse channel traces
        # Look for times when host was waiting for message or sending a message

        channels_traces = self.timeanalysis_module.get_all_channel_message_traces(simulator)
        for channel in channels_traces:
            channel_traces = channels_traces[channel]

            host_channel_sending_time_tuples = {}  # Keeps list of tuples when host was sending message
            host_channel_waiting_time_tuples = {}  # Keeps list of tuples when host was waiting for message

            # Traverse each trace and get the time of waiting
            for trace in channel_traces:

                # Add time tuple for sender if he is in asked hosts
                if trace.sender in hosts:
                    if trace.sender not in host_channel_sending_time_tuples:
                        host_channel_sending_time_tuples[trace.sender] = []
                    host_channel_sending_time_tuples[trace.sender].append((trace.sent_at,
                                                                           trace.sent_at + trace.sending_time))

                # Add time tuple for receiver if he is in asked hosts
                if trace.receiver in hosts:
                    if trace.receiver not in host_channel_waiting_time_tuples:
                        host_channel_waiting_time_tuples[trace.receiver] = []
                    host_channel_waiting_time_tuples[trace.receiver].append((trace.started_waiting_at,
                                                                             trace.received_at))

            for host in hosts:

                # Sort sending tuples
                if host in host_channel_sending_time_tuples:
                    host_channel_sending_time_tuples[host].sort(key=lambda t: t[0])
                    time_tuples = host_channel_sending_time_tuples[host]
                    sending_tuples = []
                    if len(time_tuples) > 0:
                        current_t_from = 0
                        current_t_to = 0
                        for i in range(0, len(time_tuples)):
                            t = time_tuples[i]
                            if t[0] > current_t_to:
                                if current_t_to > 0:
                                    sending_tuples.append((current_t_from, current_t_to))
                                current_t_from = t[0]
                            current_t_to = t[1]
                        if current_t_to > 0:
                            sending_tuples.append((current_t_from, current_t_to))
                else:
                    sending_tuples = []
                # Sort waiting tuples
                if host in host_channel_waiting_time_tuples:
                    host_channel_waiting_time_tuples[host].sort(key=lambda t: t[0])
                    time_tuples = host_channel_waiting_time_tuples[host]
                    waiting_tuples = []
                    if len(time_tuples) > 0:
                        current_t_from = 0
                        current_t_to = 0
                        for i in range(0, len(time_tuples)):
                            t = time_tuples[i]
                            if t[0] > current_t_to:
                                if current_t_to > 0:
                                    waiting_tuples.append((current_t_from, current_t_to))
                                current_t_from = t[0]
                            current_t_to = t[1]
                        if current_t_to > 0:
                            waiting_tuples.append((current_t_from, current_t_to))
                else:
                    waiting_tuples = []

                # Get currents
                current_sending = self._get_current_sending_for_host(metrics_manager, host, channel)
                current_waiting = self._get_current_waiting_for_host(metrics_manager, host, channel)

                sending_time = 0.0
                waiting_time = 0.0

                for s_from, s_to in sending_tuples:
                    sending_time += s_to - s_from
                for w_from, w_to in waiting_tuples:
                    waiting_time += w_to - w_from

                overlapping_time = 0.0
                w_index = 0
                for s_from, s_to in sending_tuples:
                    while w_index < len(waiting_tuples):
                        wtuple = waiting_tuples[w_index]
                        if wtuple[1] > s_from:
                            min_end = min(s_to, wtuple[1])
                            max_start = max(s_from, wtuple[0])
                            overlapping_time += min_end - max_start
                        if wtuple[1] > s_to:
                            break
                        else:
                            w_index += 1

                if current_sending > current_waiting:
                    waiting_time -= overlapping_time
                else:
                    sending_time -= overlapping_time

                hosts_consumption[host] += (voltage * current_sending * sending_time) / 1000000.0
                hosts_consumption[host] += (voltage * current_waiting * waiting_time) / 1000000.0
            
        return hosts_consumption
            

