'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import wx
import wx.lib.newevent
import threading
from aqopa.model.parser import ParserException, ModelParserException,\
    MetricsParserException, ConfigurationParserException
from aqopa.model.parser.lex_yacc.grammar import algorithms
from aqopa.model.store import QoPMLModelStore
from aqopa.model import HostProcess, name_indexes, original_name,\
    HostSubprocess, WhileInstruction, IfInstruction
from aqopa.simulator import Simulator,\
    expression, state, equation, metrics, communication, scheduler, predefined, algorithm

from aqopa.simulator.state import Executor,\
    AssignmentInstructionExecutor, IfInstructionExecutor,\
    ProcessInstructionExecutor, SubprocessInstructionExecutor,\
    FinishInstructionExecutor, CommunicationInstructionExecutor,\
    ContinueInstructionExecutor, WhileInstructionExecutor, Host, Process,\
    CallFunctionInstructionExecutor, PrintExecutor, BreakInstructionExecutor

from aqopa.simulator.error import EnvironmentDefinitionException

class Builder():
    """
    Builder that builds environment elements
    """
    
    def build_store(self):
        """
        Builds store - keeps all parsed elements from qopml model
        """
        return QoPMLModelStore()
    
    def _build_functions(self, store):
        """
        Validate and build functions
        """
        functions = []
        errors = []
        
        for f in store.functions:
            err = False
            for ef in functions:
                if ef.name == f.name:
                    errors.append("Function %s redeclared" % f.name)
                    err = True
                    break
            if not err:
                functions.append(f)
                
        if len(errors) > 0:
            raise EnvironmentDefinitionException('Functions redeclaration.', errors=errors)
        
        return functions
    
    def _build_equations(self, store, functions):
        """
        Validate, build and return simulation equations build from parsed equations.
        """
        validator = equation.Validator()
        validator.validate(store.equations, functions)
        
        equations = []
        for parsed_equation in store.equations:
            equations.append(equation.Equation(parsed_equation.composite, parsed_equation.simple))
        return equations
    
    def _build_hosts(self, store, version, functions, channels, populator, reducer):
        """
        Rebuild hosts - create new instances with updated instructions lists according to version.
        """
        
        def remove_unused_subprocesses(instructions_list, run_process): 
            """
            Create instruction lists according to "run process"
            Removes subprocesses that are not selected to run. 
            """
            if run_process.all_subprocesses_active:
                return instructions_list
            
            new_instructions_list = []
            
            for instruction in instructions_list:
                if isinstance(instruction, HostSubprocess):
                    subprocess = instruction
                    if subprocess.name in run_process.active_subprocesses:
                        new_instructions_list.append(subprocess)
                        subprocess.instructions_list = \
                            remove_unused_subprocesses(subprocess.instructions_list, 
                                                       run_process)
                else:
                    new_instructions_list.append(instruction)
                    
                    if isinstance(instruction, WhileInstruction):
                        instruction.instructions = \
                            remove_unused_subprocesses(instruction.instructions, 
                                                       run_process)
                    
                    if isinstance(instruction, IfInstruction):
                        instruction.true_instructions = \
                            remove_unused_subprocesses(instruction.true_instructions, 
                                                       run_process)
                        instruction.false_instructions = \
                            remove_unused_subprocesses(instruction.false_instructions, 
                                                       run_process)
            
            return new_instructions_list
            
        def get_channels_assgined_to_host(run_host, parsed_host, built_channels):
            """
            Creates list all channels that host can use.
            Firstly it is checked in version, secondly in parsed host.
            """
            channel_names = []
            if run_host.all_channels_active:
                if parsed_host.all_channels_active:
                    return built_channels
                else:
                    channel_names.extend([ c for c in parsed_host.active_channels ])
            else:
                channel_names.extend([ c for c in run_host.active_channels ])
            # channel_names - names of channels that host can use
            channels = [] 
            for channel_name in channel_names:
                for channel in built_channels:
                    if channel.name == channel_name:
                        channels.append(channel)
            return channels
        
        def get_channels_assigned_to_process(run_process, parsed_process, built_channels):
            """
            Creates list all channels that process can use.
            Firstly it is checked in version, secondly in parsed process.
            """
            channel_names = []
            # Get channel names uded by process
            if parsed_process.all_channels_active:
                return built_channels
            else:
                for channel_name in parsed_process.active_channels:
                    channel_names.append(channel_name)
            # channel_names - names of channels that host can use
            channels = [] 
            for channel_name in channel_names:
                for channel in built_channels:
                    if channel.name == channel_name:
                        channels.append(channel)
            return channels
            
        def build_host_instructions_list(parsed_host, run_host, repetition_number, channels):
            """
            Create host's  and its processes' instruction lists 
            according to "run host" (repetitions) 
            """
            
            def find_process(instructions_list, process_name):
                for instr in instructions_list:
                    if not isinstance(instr, HostProcess):
                        continue
                    if instr.name == process_name:
                        return instr
                return None
            
            
            processes_numbers = {}
            host_instructions_list = []
            
            for run_process in run_host.run_processes:
                
                # Find parsed process
                parsed_process = find_process(parsed_host.instructions_list, run_process.process_name)
                
                if parsed_process is None:
                    raise EnvironmentDefinitionException("Process '%s' does not exist in host '%s'." % 
                                                         (run_process.process_name, parsed_host.name))
                
                # Clone the parsed process, because builder 
                # may change its the instructions list
                # and remove some subprocesses that would be 
                # needed by other version 
                parsed_process = parsed_process.clone()
                
                # Define initial process number (if needed)
                if run_process.process_name not in processes_numbers:
                    processes_numbers[run_process.process_name] = 0
                
                # If process has follower
                if run_process.follower:
                    # Define initial process number for following process (if needed)
                    if run_process.follower.process_name not in processes_numbers:
                        processes_numbers[run_process.follower.process_name] = 0
                        
                # Get channels assigned to process and its follower (if needed)
                process_channels = get_channels_assigned_to_process(run_process, parsed_process, channels)
                follower_channels = []
                if run_process.follower:
                    follower_parsed_process = find_process(parsed_host.instructions_list, run_process.follower.process_name)
                    follower_channels = get_channels_assigned_to_process(run_process.follower, follower_parsed_process, channels)
                    
                for i in range(0, run_process.repetitions):
                    
                    # Create instructions list
                    instructions_list = remove_unused_subprocesses(parsed_process.instructions_list, run_process)
                    
                    # Create new simulation process
                    simulated_process = Process(parsed_process.name, instructions_list)

                    # Connect with channels
                    for ch in process_channels:
                        ch.connect_with_process(simulated_process)
                    
                    # Update process index
                    process_number = processes_numbers[run_process.process_name] + i
                    simulated_process.add_name_index(process_number)
                    
                    # Do the same fo the follower 
                    if run_process.follower:
                        
                        # Find process of follower
                        follower_parsed_process = find_process(parsed_host.instructions_list, run_process.follower.process_name)

                        # Build instructions list for follower
                        follower_instructions_list = remove_unused_subprocesses(follower_parsed_process.instructions_list, run_process.follower)

                        # Create simulated follower
                        simulated_follower = Process(follower_parsed_process.name, follower_instructions_list)

                        # Connect with channels
                        for ch in follower_channels:
                            ch.connect_with_process(simulated_follower)
                            
                        # Update follower index
                        follower_number = processes_numbers[run_process.follower.process_name] + i
                        simulated_follower.add_name_index(follower_number)
                        
                        simulated_process.follower = simulated_follower
                        
                    host_instructions_list.append(simulated_process)
            
            return host_instructions_list
        
        def set_scheduler(host, algorithm):
            """
            Build and set host's scheduler
            """
            host.set_scheduler(scheduler.create(host, algorithm))
        
        built_hosts = []
            
        # Hosts numbers dict keeps the last used number of repeated host.
        hosts_numbers = {} 
        
        for run_host in version.run_hosts:
            
            if run_host.host_name not in hosts_numbers:
                hosts_numbers[run_host.host_name] = 0
            
            # Create prototype parsed host for this "run host"
            parsed_host = store.find_host(run_host.host_name)
            
            assigned_channels = get_channels_assgined_to_host(run_host, parsed_host, channels)
            
            for i in range(0, run_host.repetitions):

                # Build next instructions list for next repeated host                
                instructions_list = build_host_instructions_list(parsed_host, run_host, i, channels)
                
                simulation_host = Host(parsed_host.name, instructions_list)
                    
                # Set the number of host    
                host_number = hosts_numbers[run_host.host_name] + i
                simulation_host.add_name_index(host_number)
                
                # Set scheduler
                set_scheduler(simulation_host, parsed_host.schedule_algorithm)
                
                for ch in assigned_channels:
                    ch.connect_with_host(simulation_host)
                
                built_hosts.append(simulation_host)
                
            hosts_numbers[run_host.host_name] += run_host.repetitions 
            
        return built_hosts

    def _set_hosts_predefined_values(self, store, hosts, populator):
            
        def set_predefined_variables(host, predefined_values, populator):
            """
            Populate predefined values with expressions 
            and save them as variables in host
            """
            for predefined_value in predefined_values:
                populated_value = populator.populate(predefined_value.expression.clone(), host)
                # print 'Setting predefined variable ', predefined_value.variable_name, \
                #     ' in host ', host.name, ' with value ', unicode(populated_value), \
                #     ' (', getattr(populated_value, '_host_name', 'None'), ')'
                host.set_variable(predefined_value.variable_name, populated_value)
        for host in hosts:
            parsed_host = store.find_host(host.original_name())
            # Save predefined values as variables
            set_predefined_variables(host, parsed_host.predefined_values, populator)
        return hosts
    
    def _build_expression_populator(self, reducer):
        """
        Build and return object that populates expressions
        with variables' values.
        """
        return expression.Populator(reducer)
    
    def _build_expression_checker(self, populator):
        """
        Build and return object that checks the logic value of expressions.
        """
        return expression.Checker(populator)
    
    def _build_expression_reducer(self, equations):
        """
        Build and return object that reduces expressions.
        """
        return expression.Reducer(equations)
    
    def _build_channels(self, store, version):
        """
        Validate, build and return simulation channels build from parsed channels.
        Includes channel repetitions.
        """
        
        built_channels = []
        for parsed_channel in store.channels:
            channel = communication.Channel(parsed_channel.name, parsed_channel.buffor_size, parsed_channel.tag_name)
            built_channels.append(channel)
        return built_channels
    
    def _build_topology(self, topology_rules, hosts):

        def find_left_hosts(topology_host, hosts):
            found_hosts = []
            for host in hosts:
                # If host has the same identifier
                if host.original_name() == topology_host.identifier:
                    # If no range is specified
                    if topology_host.index_range is None:
                        found_hosts.append(host)
                    else:
                        # Range is specified
                        start_i = topology_host.index_range[0]
                        end_i = topology_host.index_range[1]
                        i = host.get_name_index()
                        if (start_i is None or i >= start_i) and (end_i is None or i <= end_i):
                            found_hosts.append(host)
            return found_hosts
        
        def find_right_hosts(topology_host, hosts, current_host):
            if topology_host is None:
                return []
            found_hosts = []
            for host in hosts:
                # If host has the same identifier
                if host.original_name() == topology_host.identifier:
                    # If no range is specified
                    if topology_host.index_range is None:
                        # If no index shift is specified
                        if topology_host.i_shift is None:
                            found_hosts.append(host)
                        else:
                            # Index shift is specified
                            i = current_host.get_name_index()
                            i += topology_host.i_shift
                            shifted_host_name = topology_host.identifier + "." + str(i)
                            if host.name == shifted_host_name:
                                found_hosts.append(host)
                    else:
                        # Range is specified
                        start_i = topology_host.index_range[0]
                        end_i = topology_host.index_range[1]
                        i = host.get_name_index()
                        if (start_i is None or i >= start_i) and (end_i is None or i <= end_i):
                            found_hosts.append(host)
            return found_hosts
        
        def add_connection(topology, from_host, to_host, parameters):
            if from_host not in topology:
                topology[from_host] = {'hosts': [], 'parameters': {}}
            if to_host not in topology[from_host]['hosts']:
                topology[from_host]['hosts'].append(to_host)
                for parameter in parameters:
                    if parameter not in topology[from_host]['parameters']:
                        topology[from_host]['parameters'][parameter] = {}
                    topology[from_host]['parameters'][parameter][to_host] = parameters[parameter]
            return topology

        topology = {}
        for rule in topology_rules:
            for left_host in find_left_hosts(rule.left_host, hosts):
                for right_host in find_right_hosts(rule.right_host, hosts, left_host):
                    if rule.arrow == '->' or rule.arrow == '<->':
                        topology = add_connection(topology, left_host, right_host, rule.parameters)
                    if rule.arrow == '<-' or rule.arrow == '<->':
                        topology = add_connection(topology, right_host, left_host, rule.parameters)
        return topology
        
    
    def _build_channels_manager(self, channels, built_hosts, version, store):
        """ 
        Build channels manager
        """
        mgr = communication.Manager(channels)
        for name in version.communication['mediums']:
            topology_rules = version.communication['mediums'][name]['topology']['rules']
            default_params = version.communication['mediums'][name]['default_parameters']
            mgr.add_medium(name, self._build_topology(topology_rules, built_hosts), default_params)
        for name in store.mediums:
            if not mgr.has_medium(name):
                topology_rules = store.mediums[name]['topology']['rules']
                default_params = store.mediums[name]['default_parameters']
                mgr.add_medium(name, self._build_topology(topology_rules, built_hosts), default_params)
        return mgr
    
    def _build_predefined_functions_manager(self, context):
        """
        Build manager for predefined functions
        """
        return predefined.FunctionsManager(context)
        
    def _build_metrics_manager(self, store, hosts, version):
        """
        Build and return metrics manager.
        """
        host_metrics = []
        
        for metrics_data in store.metrics_datas:
            
            blocks = []
            # Build list of metrics blocks
            for block in metrics_data.blocks:
                
                params = block.header.params[1:]
                service_params = block.header.services_params
                metrics_block = metrics.Block(params, service_params)
                
                for metric in block.metrics:
                    m = metrics.Metric(metric.arguments[0], metric.arguments[1:len(params)+1], 
                                       metric.arguments[len(params)+1:])
                    metrics_block.add_metric(m)
                blocks.append(metrics_block)
            
            # get or create host metrics with given name
            hm = None
            for existing_hm in host_metrics:
                if existing_hm.name == metrics_data.name:
                    hm = existing_hm
                    break
            if hm is None:
                hm = metrics.HostMetrics(metrics_data.name)
                host_metrics.append(hm)
            
            if metrics_data.plus or metrics_data.star:
                if metrics_data.plus:
                    hm.plus_blocks = blocks
                else: # star
                    hm.star_blocks = blocks
                    
                # If host metrics does not have normal block
                # Search for them and assign if found in host metrics 
                # with simple name (not qualified like hm1.1)
                if len(hm.normal_blocks) == 0:
                    hm_original_name = original_name(hm.name)
                    hm_original = None
                    
                    for existing_hm in host_metrics:
                        if original_name(existing_hm.name) == hm_original_name \
                            and existing_hm != hm:
                            hm_original = existing_hm
                            break
                        
                    if hm_original:
                        hm.normal_blocks = hm_original.normal_blocks
                        
            else: # metrics_data normal
                hm_original_name = original_name(hm.name)
                
                # Assign normal block to all host metrics with the same original name
                for existing_hm in host_metrics:
                    if original_name(existing_hm.name) == hm_original_name:
                        # Assign notmal block to all host metrics with the same original name
                        # (including the current one - possibly created)
                        existing_hm.normal_blocks = blocks
                        
        # Connect host metrics with hosts
        for metrics_set in version.metrics_sets:
            for h in hosts:
                if h.original_name() == metrics_set.host_name:
                    for host_metric in host_metrics:
                        if host_metric.name == metrics_set.configuration_name:
                            host_metric.connected_hosts.append(h)
                            break
        
        return metrics.Manager(host_metrics)

    def _build_algorithms_resolver(self, store):
        """
        """
        resolver = algorithm.AlgorithmResolver()
        for alg_name in store.algorithms:
            resolver.add_algorithm(alg_name, store.algorithms[alg_name])
        return resolver
    
    def _build_context(self, store, version):
        """
        Builds context with initial state.
        """
        functions = self._build_functions(store)
        equations = self._build_equations(store, functions)
        expression_reducer = self._build_expression_reducer(equations)
        expression_populator = self._build_expression_populator(expression_reducer)
        expression_checker = self._build_expression_checker(expression_populator)
        channels = self._build_channels(store, version)
        hosts = self._build_hosts(store, version, functions, channels,
                                  expression_populator, expression_reducer)

        # Context
        c = state.Context(version)
        c.functions = functions
        c.hosts = hosts
        c.expression_reducer = expression_reducer
        c.expression_checker = expression_checker
        c.expression_populator = expression_populator
        c.metrics_manager = self._build_metrics_manager(store, hosts, version)
        c.channels_manager = self._build_channels_manager(channels, hosts, version, store)
        c.algorithms_resolver = self._build_algorithms_resolver(store)
        
        # Predefined manager
        predefined_functions_manager = self._build_predefined_functions_manager(c)
        expression_populator.predefined_functions_manager = predefined_functions_manager
        expression_reducer.predefined_functions_manager = predefined_functions_manager
        
        # Predefined hosts' variables
        self._set_hosts_predefined_values(store, hosts, expression_populator)
        
        return c
    
    def build_executor(self):
        """
        Creates executor for simulation
        """
        e = Executor()
        e.append_instruction_executor(AssignmentInstructionExecutor())
        e.append_instruction_executor(CallFunctionInstructionExecutor())
        e.append_instruction_executor(ProcessInstructionExecutor())
        e.append_instruction_executor(SubprocessInstructionExecutor())
        e.append_instruction_executor(CommunicationInstructionExecutor())
        e.append_instruction_executor(FinishInstructionExecutor())
        e.append_instruction_executor(ContinueInstructionExecutor())
        e.append_instruction_executor(BreakInstructionExecutor())
        e.append_instruction_executor(IfInstructionExecutor())
        e.append_instruction_executor(WhileInstructionExecutor())
        return e
    
    def build_simulator(self, store, version):
        """
        Creates simulator for particular version.
        """
        sim = Simulator(self._build_context(store, version))
        sim.set_executor(self.build_executor())
        return sim
    
    def build_model_parser(self, store, modules):
        """
        Builder parser that parses model written in QoPML
        and populates the store.
        """
        from aqopa.model.parser.lex_yacc import LexYaccParser
        from aqopa.model.parser.lex_yacc.grammar import main,\
                functions, channels, equations, expressions, instructions,\
                hosts, modules as modules_module, communication as comm_grammar
        
        parser = LexYaccParser()
        parser.set_store(store) \
                .add_extension(main.ModelParserExtension()) \
                .add_extension(modules_module.ModelParserExtension()) \
                .add_extension(functions.ModelParserExtension()) \
                .add_extension(channels.ModelParserExtension()) \
                .add_extension(equations.ModelParserExtension()) \
                .add_extension(expressions.ModelParserExtension()) \
                .add_extension(comm_grammar.ModelParserExtension()) \
                .add_extension(algorithms.ModelParserExtension()) \
                .add_extension(instructions.ModelParserExtension()) \
                .add_extension(hosts.ModelParserExtension())
                
        for m in modules:
            parser = m.extend_model_parser(parser)
                
        return parser.build()
    
    def build_metrics_parser(self, store, modules):
        """
        Builder parser that parses metrics written in QoPML
        and populates the store.
        """
        from aqopa.model.parser.lex_yacc import LexYaccParser
        from aqopa.model.parser.lex_yacc.grammar import main, metrics as metrics_grammar
        
        parser = LexYaccParser()
        parser.set_store(store)\
                .add_extension(main.MetricsParserExtension())\
                .add_extension(metrics_grammar.MetricsParserExtension())
                
        for m in modules:
            parser = m.extend_metrics_parser(parser)
                
        return parser.build()
    
    def build_config_parser(self, store, modules):
        """
        Builder parser that parses config written in QoPML
        and populates the store.
        """
        from aqopa.model.parser.lex_yacc import LexYaccParser
        from aqopa.model.parser.lex_yacc.grammar import versions, main, communication as comm_grammar
        
        parser = LexYaccParser()
        parser.set_store(store)\
                .add_extension(main.ConfigParserExtension())\
                .add_extension(comm_grammar.ConfigParserExtension()) \
                .add_extension(versions.ConfigParserExtension())
                
        for m in modules:
            parser = m.extend_config_parser(parser)
                
        return parser.build()
    
class Interpreter():
    """
    Interpreter is responsible for parsing the model,
    creating the environment for simulations,
    manipulating selected models.
    """
    
    def __init__(self, builder=None, model_as_text="", 
                 metrics_as_text="", config_as_text=""):
        self.builder = builder if builder is not None else Builder()
        self.model_as_text = model_as_text
        self.metrics_as_text = metrics_as_text 
        self.config_as_text = config_as_text
        
        self.store = None
        
        self._modules = []
        
    def set_qopml_model(self, model_as_text):
        """
        Set qopml model that will be interpreted.
        """
        self.model_as_text = model_as_text
        return self
    
    def set_qopml_metrics(self, metrics_as_text):
        """
        Set qopml metrics that will be interpreted.
        """
        self.metrics_as_text = metrics_as_text
        return self
    
    def set_qopml_config(self, config_as_text):
        """
        Set qopml configuration that will be interpreted.
        """
        self.config_as_text = config_as_text
        return self
    
    def register_qopml_module(self, qopml_module):
        """
        Registers new module
        """
        if qopml_module in self._modules:
            raise EnvironmentDefinitionException(u"QoPML Module '%s' is already registered." % unicode(qopml_module))
        self._modules.append(qopml_module)
        return self
        
    def parse(self, all_modules):
        """
        Parses the model from model_as_text field and populates the store.
        """
        if len(self.model_as_text) == 0:
            raise EnvironmentDefinitionException("QoPML Model not provided.")
    
        self.store = self.builder.build_store()
    
        parser = self.builder.build_model_parser(self.store, all_modules)
        parser.parse(self.model_as_text)
        if len(parser.get_syntax_errors()) > 0:
            raise ModelParserException('Invalid syntax.', syntax_errors=parser.get_syntax_errors())
    
        parser = self.builder.build_metrics_parser(self.store, all_modules)
        parser.parse(self.metrics_as_text)
        if len(parser.get_syntax_errors()) > 0:
            raise MetricsParserException('Invalid syntax.', syntax_errors=parser.get_syntax_errors())
    
        parser = self.builder.build_config_parser(self.store, all_modules)
        parser.parse(self.config_as_text)
        if len(parser.get_syntax_errors()) > 0:
            raise ConfigurationParserException('Invalid syntax.', syntax_errors=parser.get_syntax_errors())
    
    def install_modules(self, simulator):
        """ """
        raise NotImplementedError()
    
    def run(self):
        """ Runs all simulations """
        raise NotImplementedError()
            
class ConsoleInterpreter(Interpreter):
    
    def __init__(self, builder=None, model_as_text="", 
                 metrics_as_text="", config_as_text=""):
        Interpreter.__init__(self, builder, model_as_text, metrics_as_text, config_as_text)
        
        self.simulators = []

    def save_states_to_file(self, simulator):
        """ 
        Tells simulator to save states flow to file.
        """
        f = open('VERSION_%s_STATES_FLOW' % simulator.context.version.name, 'w')
        simulator.get_executor().prepend_instruction_executor(PrintExecutor(f))      

    def prepare(self):
        """ Prepares for run """
        
        for version in self.store.versions:
            simulator = self.builder.build_simulator(self.store, version)
            self.simulators.append(simulator)
            self.install_modules(simulator)
    
    def install_modules(self, simulator):
        """ """
        for m in self._modules:
            m.install_console(simulator)
        
    def run(self):
        """ Runs all simulations """

        for s in self.simulators:
            s.prepare()
            s.run()
            self.on_finished(s)
            
    def on_finished(self, simulator):
        pass

    def is_finished(self):
        for s in self.simulators:
            if not s.is_simulation_finished():
                return False
        return True

class GuiInterpreter(Interpreter):
    
    def __init__(self, builder=None, model_as_text="", 
                 metrics_as_text="", config_as_text=""):
        Interpreter.__init__(self, builder=builder, 
                             model_as_text=model_as_text, 
                             metrics_as_text=metrics_as_text, 
                             config_as_text=config_as_text)
        self.simulators = []

    def prepare(self):
        """ Prepares for run """
        for version in self.store.versions:
            simulator = self.builder.build_simulator(self.store, version)
            self.install_modules(simulator)
            self.simulators.append(simulator)
    
    def install_modules(self, simulator):
        """ """
        for m in self._modules:
            m.install_gui(simulator)
            
    def run_simulation(self, simulator):
        """ """
        simulator.prepare()
        simulator.run()
        return simulator
