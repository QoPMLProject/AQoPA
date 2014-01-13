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
    
    def _get_current_radio_listen_for_host(self, metrics_manager, host):
        """
        Returns current from metric for radion in listening state.
        """
        expression = CallFunctionExpression('radio', [], ['listen'])
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
                
                return float(metric.service_arguments[i])

        return 0.0

    def get_hosts_consumptions(self, simulator, hosts, voltage):
        """
        """
        metrics_manager = simulator.context.metrics_manager

        if simulator not in self.timeanalysis_module.timetraces:
            return []

        timetraces = self.timeanalysis_module.timetraces[simulator]

        # Clear results
        hosts_consumption = {}
        host_finish_times = {}
        for h in hosts:
            hosts_consumption[h] = 0.0
            host_finish_times[h] = [] # Item is a tuple: (finish time, chanel trace/None)

        # Traverse timetraces
        # Additionaly create list of finish times of instructions for each host
        # (List of times when instructions has been finished)  

        for timetrace in timetraces:
            
            # Omit hosts that are not given in parameter
            if timetrace.host not in hosts:
                continue
            
            host_finish_times[timetrace.host].append((timetrace.started_at + timetrace.length, None))
            
            # Get time from timetrace
            time_sec = timetrace.length / 1000.0
            
            consumption = 0.0
            # Get expressions from timetrace
            for simple_expression, time in timetrace.expressions_details:
                current = self._get_current_for_expression(metrics_manager, timetrace.host, simple_expression)
            
                # Calculate consumption
                consumption = voltage * current * time_sec
                
            hosts_consumption[timetrace.host] += consumption
            
        # Traverse channel traces
        # Look for times when host was waiting for message
        channel_traces = self.timeanalysis_module.channel_message_traces[simulator]
        
        hosts_listen_metric = {}
        
        # Firstly add the times of retrieving messages 
        for trace in channel_traces:
            if trace.receiver and trace.receiver in hosts:
                host_finish_times[trace.receiver].append((trace.received_at, trace))
                
        # Traverse each trace and get the time of waiting
        for trace in channel_traces:
            
            # Omit traces of not received messages
            host = trace.receiver
            if not host or host not in hosts:
                continue

            # Find or get metric
            if host not in hosts_listen_metric:
                hosts_listen_metric[host] = self._get_current_radio_listen_for_host(metrics_manager, host)
                
            current = hosts_listen_metric[host]
            
            # Find the time when host started to wait for this message
            started_at = 0.0
            for time, current_trace in host_finish_times[host]:
                if started_at < time < trace.received_at:
                    started_at = time
                     
            waiting_time = (trace.received_at - started_at) / 1000.0
            hosts_consumption[host] += voltage * current * waiting_time
            
        return hosts_consumption
            

