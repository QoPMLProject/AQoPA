'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import wx
import wx.lib.newevent
import threading
from aqopa.model.parser import ParserException, ModelParserException,\
    MetricsParserException, ConfigurationParserException
from aqopa.model.store import QoPMLModelStore
from aqopa.model import HostProcess, name_indexes, original_name,\
    HostSubprocess, WhileInstruction, IfInstruction
from aqopa.simulator import Simulator,\
    expression, state, equation, metrics, communication, scheduler
    
from aqopa.simulator.state import Executor,\
    AssignmentInstructionExecutor, IfInstructionExecutor,\
    ProcessInstructionExecutor, SubprocessInstructionExecutor,\
    FinishInstructionExecutor, CommunicationInstructionExecutor,\
    ContinueInstructionExecutor, WhileInstructionExecutor, Host, Process,\
    CallFunctionInstructionExecutor, PrintExecutor
    
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
    
    def _build_hosts(self, store, version, functions, populator, reducer):
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
            
        def build_host_instructions_list(parsed_host, run_host, repetition_number):
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
                    
                for i in range(0, run_process.repetitions):
                    
                    # Create instructions list
                    instructions_list = remove_unused_subprocesses(parsed_process.instructions_list, run_process)
                    
                    # Create new simulation process
                    simulated_process = Process(parsed_process.name, instructions_list)
                    
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
                            
                        # Update follower index
                        follower_number = processes_numbers[run_process.follower.process_name] + i
                        simulated_follower.add_name_index(follower_number)
                        
                        simulated_process.follower = simulated_follower
                        
                    host_instructions_list.append(simulated_process)
            
            return host_instructions_list
            
        def set_predefined_variables(host, predefined_values, populator, reducer):
            """
            Populate predefined values with expressions 
            and save them as variables in host
            """
            for predefined_value in predefined_values:
                host.set_variable(predefined_value.variable_name, 
                                  populator.populate(predefined_value.expression, 
                                                     host.get_variables(), 
                                                     reducer))
        
        def set_scheduler(host, algorithm):
            """
            Build and set host's scheduler
            """
            host.set_scheduler(scheduler.create(host, algorithm))
        
        built_hosts = []
            
        # Hosts numbers dict keeps the last used number of repeated channel for hosts.
        # For example:
        # run A(*){5} { ... } - will create channels ch1.1, ch1.2, ch1.3, ch1.4 and ch1.5
        # run A(ch1,ch2){2} { ... } - will create channels for next numers which are ch1.6, ch2.6 and ch1.7, ch2.7
        hosts_numbers = {} 
        
        for run_host in version.run_hosts:
            
            if run_host.host_name not in hosts_numbers:
                hosts_numbers[run_host.host_name] = 0
            
            # Create prototype parsed host for this "run host"
            parsed_host = store.find_host(run_host.host_name)
            
            for i in range(0, run_host.repetitions):

                # Build next instructions list for next repeated host                
                instructions_list = build_host_instructions_list(parsed_host, run_host, i)
                
                simulation_host = Host(parsed_host.name, instructions_list)
                    
                # Set the number of host    
                host_number = hosts_numbers[run_host.host_name] + i
                simulation_host.add_name_index(host_number)
                
                # Set scheduler
                set_scheduler(simulation_host, parsed_host.schedule_algorithm)
                
                # Save predefined values as variables
                set_predefined_variables(simulation_host, 
                                         parsed_host.predefined_values, 
                                         populator, 
                                         reducer)
                built_hosts.append(simulation_host)
                
            hosts_numbers[run_host.host_name] += run_host.repetitions 
            
        return built_hosts
    
    def _build_expression_populator(self):
        """
        Build and return object that populates expressions
        with variables' values.
        """
        return expression.Populator()
    
    def _build_expression_checker(self):
        """
        Build and return object that checks the logic value of expressions.
        """
        return expression.Checker()
    
    def _build_expression_reducer(self, equations):
        """
        Build and return object that reduces expressions.
        """
        return expression.Reducer(equations)
    
    def _build_channels(self, store, version, built_hosts):
        """
        Validate, build and return simulation channels build from parsed channels.
        Includes channel repetitions.
        """
        
        def find_channel(channels, name):
            """
            Find channel by name.
            """
            for ch in channels:
                if ch.name == name:
                    return ch
            return None
        
        def find_built_host(built_hosts, name):
            for h in built_hosts:
                if h.name == name:
                    return h
            return None
            
        def find_parsed_process(instructions_list, process_name):
            for instr in instructions_list:
                if not isinstance(instr, HostProcess):
                    continue
                if instr.name == process_name:
                    return instr
            return None
        
        def get_or_create_channel(existing_channels, channel_name):
            """
            Get existing channel by name or create new channel.
            """
            # Find repeated channel with indexes by name 
            channel = find_channel(existing_channels, channel_name)
            # If repeated channel with indexes does not exist
            if channel is None:
                # Find first channel (zero indexes) with original name of repeated channel
                channel = find_channel(existing_channels, original_name(channel_name) + '.0.0')
                channel = channel.clone()
                indexes = name_indexes(channel_name)
                
                for i in range(0, len(indexes)):
                    channel.add_name_index(indexes[i])
                indexes = name_indexes(channel.name)
                
                for i in range(len(indexes), 2):
                    channel.add_name_index(0)
                    
                existing_channels.append(channel)
            return channel
        
        built_channels = []
        original_channels = []
        
        for parsed_channel in store.channels:
            channel = communication.Channel(parsed_channel.name, parsed_channel.buffor_size)
            channel.add_name_index(0)
            channel.add_name_index(0)
            built_channels.append(channel)
            original_channels.append(channel)
            
        # Hosts numbers dict keeps the last used number of repeated channel for hosts.
        # For example:
        # run A(*){5} { ... } - will create channels ch1.1, ch1.2, ch1.3, ch1.4 and ch1.5
        # run A(ch1,ch2){2} { ... } - will create channels for next numers which are ch1.6, ch2.6 and ch1.7, ch2.7
        hosts_numbers = {} 
        
        for run_host in version.run_hosts:
            parsed_host = store.find_host(run_host.host_name)
            # Load all channels names that host can use
            # Firstly it is checked in version, secondly in parsed host
            # List channel_names contains clean channel names (ch1, ch2) 
            channel_names = []
            if run_host.all_channels_active:
                if parsed_host.all_channels_active:
                    channel_names += [ c.original_name() for c in original_channels ]
                else:
                    channel_names += [ c for c in parsed_host.active_channels ]
            else:
                channel_names += [ c for c in run_host.active_channels ]
            # channel_names - clean names of channels that host can use

            if parsed_host.name not in hosts_numbers:
                hosts_numbers[parsed_host.name] = 0
                
            host_first_number = hosts_numbers[parsed_host.name]
            
            # HOST-CHANNELS ASSIGNATION
            # Algorithm:
            # - For each channel name
            #     - Check if channel is repeated
            #     - Get the name of repeated shannel
            #     - If yes:
            #         - Find channel with repeated name with indexes
            #         - If channel with indexes does not exist: 
            #             - Find channel with original name (zero indexes)
            #             - Clone it and add indexes 
            #             - Add new channel to built channels  
            #     - If no 
            
            for channel_name in channel_names:
                
                # Calculate the name of repeated channel (if it is repeated) 
                # with indexes
                repeated_name = ""
                for repeated_channel in run_host.repeated_channels:
                    repeated_channel_basename = original_name(repeated_channel)
                    if channel_name == repeated_channel_basename:
                        indexes = name_indexes(repeated_channel)
                        if len(indexes) > 0:
                            repeated_name = repeated_channel_basename + '.' + str(indexes[0]) + '.0'
                        else:
                            repeated_name += repeated_channel_basename + '.0.0'
                        break
                    
                # If channel is repeated
                if repeated_name != "":
                    
                    channel = get_or_create_channel(built_channels, repeated_name)
                    
                    # Assign channel to hosts created on the base of this "run host"
                    for i in range(0, run_host.repetitions):
                        host_number = host_first_number + i
                        host_name = run_host.host_name + '.' + str(host_number)
                        built_host = find_built_host(built_hosts, host_name)
                        built_host.connect_with_channel(channel)
                    
                else: # Channel is not repeated
                    
                    # New channel is created for each channel name
                    # starting from the lately used number (hosts_numbers)
                    
                    for i in range(0, run_host.repetitions):
                        host_number = host_first_number + i
                        host_name = run_host.host_name + '.' + str(host_number)
                        
                        new_channel_name = channel_name + '.' + str(host_number) + '.0'
                        channel = get_or_create_channel(built_channels, new_channel_name)
                        
                        built_host = find_built_host(built_hosts, host_name)
                        built_host.connect_with_channel(channel)
                        
            # PROCESS-CHANNEL ASSIGNATION
            # Update process-channel assignations in each build host 
            # created on the base of this "run host"
            
            for i in range(0, run_host.repetitions):
                # Process numbers dict keeps the last used number of repeated channel for processes.
                # Works the same like hosts_numbers for hosts.
                processes_numbers = {} 
                
                host_number = host_first_number + i
                host_name = run_host.host_name + '.' + str(host_number)
                
                built_host = find_built_host(built_hosts, host_name)
                parsed_host = store.find_host(built_host.original_name()) 
                
                instruction_index = 0
                for run_process in run_host.run_processes:
                    
                    # Find next process om host's instructions list
                    while instruction_index < len(built_host.instructions_list):
                        if isinstance(built_host.instructions_list[instruction_index], Process):
                            break
                        instruction_index += 1
                        
                    # If no process found raise exception
                    if instruction_index >= len(built_host.instructions_list):
                        raise EnvironmentDefinitionException("Process '%s' not found in host '%s'." % (run_process.process_name, built_host.name))
        
                    if run_process.process_name not in processes_numbers:
                        processes_numbers[run_process.process_name] = 0
                        
                    # Get number of next channel for this process name 
                    process_first_number = processes_numbers[run_process.process_name]
                    
                    # Get process for this "run process"
                    parsed_process = find_parsed_process(parsed_host.instructions_list, run_process.process_name)
                    
                    process_channel_names = []
                    # Get channel names uded by process
                    if parsed_process.all_channels_active:
                        process_channel_names = channel_names
                    else:
                        for process_channel_name in parsed_process.active_channels:
                            process_channel_names.append(process_channel_name)
                            
                    for process_channel_name in process_channel_names:
                        
                        # Calculate the name of repeated channel (if it is repeated) 
                        # with indexes
                        process_channel_repeated_name = "" # Name of repeated channel (may be with indexes)
                        for repeated_channel in run_process.repeated_channels:
                            process_channel_repeated_name_basename = original_name(repeated_channel)
                            if process_channel_name == process_channel_repeated_name_basename:
                                process_channel_repeated_name = repeated_channel
                        
                        # If channel is repeated
                        if process_channel_repeated_name != "":
                            repeated_indexes = name_indexes(process_channel_repeated_name)
                            # If repeated channel is the same, that host is connected with (no indexes)
                            if len(repeated_indexes) == 0:
                                channel = built_host.find_channel(process_channel_repeated_name)
                                # If host does not have channel with this name
                                if  channel is None:
                                    # Generate channel name for this process
                                    ch_name = original_name(process_channel_repeated_name) + '.' +\
                                                str(host_number) + '.' + str(process_first_number)
                                    channel = get_or_create_channel(built_channels, ch_name)
                                    
                            elif len(repeated_indexes) == 1:
                                # Repeated index is the process index in channels (second index)
                                #
                                # Repeated channel has defined numer of channel from channels of current host 
                                # (for different copies of hosts, these are different channels)
                                # For example: Repeated channel name ch1.1 in host A.5 means that all messages
                                # from all copies of process will be sent through channel ch1.x.1 
                                # (where x is the number of channel ch1 in hist A.5 - firstly it would be propably 5)
                                
                                channel = built_host.find_channel(original_name(process_channel_repeated_name))
                                
                                if channel:
                                    # Host has channel with this original name
                                    # Lets check if its second index (process index) is the same 
                                    # with repeated index
                                    
                                    ch_indexes = channel.indexes()
                                    # If channel proces index (2nd) is different from repeated index
                                    if ch_indexes[1] != repeated_indexes[0]:
                                        ch_name = original_name(process_channel_repeated_name) + '.' +\
                                                    str(ch_indexes[0]) + '.' + str(repeated_indexes[0])
                                        channel = get_or_create_channel(built_channels, ch_name)
                                
                                else:
                                    # Channel is not connected with host
                                    # Generate channel name for this process and host
                                    ch_name = original_name(process_channel_repeated_name) + '.' +\
                                                str(host_number) + '.' + str(repeated_indexes[0])
                                    channel = get_or_create_channel(built_channels, ch_name)
                                 
                            elif len(repeated_indexes) == 2:
                                ch_name = process_channel_repeated_name
                                channel = get_or_create_channel(built_channels, ch_name)
                                    
                            else:
                                raise EnvironmentDefinitionException(
                                        'Invalid repeated channel definition %s in process %s (host %s).'\
                                        % (process_channel_repeated_name, run_process.process_name, built_host.name))
                            
                            # Connect repeated channel with all repeated processes
                            # Repeated processes are found as list of next instructions in host's instructions list
                            for i in range(0, run_process.repetitions):
                                built_process = built_host.instructions_list[instruction_index+i]
                                if not isinstance(built_process, Process):
                                    raise EnvironmentDefinitionException(
                                        'Isntruction nr %d of host %s expected to be process.'\
                                        % (instruction_index+i, built_host.name))
                                built_process.connect_with_channel(channel) 
                        
                        else: # Channel is not repeated
                            
                                current_host_channel_index = host_number
                                
                                # Check if host is connected with any channel of this original name
                                channel = built_host.find_channel(original_name(process_channel_name))
                                if channel:
                                    # Get current host channel index 
                                    # from the second index of found channel indexes
                                    ch_indexes = channel.indexes()
                                    current_host_channel_index = ch_indexes[0]
                                    
                                for i in range(0, run_process.repetitions):
                                    # Generate the channel name for all repetitions
                                    process_number = process_first_number + i
                                    
                                    # Search for channel with generated name or create one
                                    ch_name = original_name(process_channel_name) + '.' +\
                                            str(current_host_channel_index) + '.' + str(process_number)
                                    channel = get_or_create_channel(built_channels, ch_name)
                                    
                                    # Connect channel with process  
                                    built_process = built_host.instructions_list[instruction_index+i]
                                    
                                    if not isinstance(built_process, Process):
                                        raise EnvironmentDefinitionException(
                                            'Isntruction nr %d of host %s expected to be process.'\
                                            % (instruction_index+i, built_host.name))
                                    built_process.connect_with_channel(channel)
                    
                    # Update process numbers dict
                    processes_numbers[run_process.process_name] += run_process.repetitions
                    instruction_index += run_process.repetitions
        
            # Update hosts numbers dict
            hosts_numbers[run_host.host_name] += run_host.repetitions
                                
        return built_channels
    
    def _build_channels_manager(self, channels):
        """ 
        Build channels manager
        """
        return communication.Manager(channels)
        
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
    
    def _build_context(self, store, version):
        """
        Builds context with initial state.
        """
        functions = self._build_functions(store)
        equations = self._build_equations(store, functions)
        expression_reducer = self._build_expression_reducer(equations)
        expression_populator = self._build_expression_populator()
        expression_checker = self._build_expression_checker()
        hosts = self._build_hosts(store, version, functions, 
                                  expression_populator, expression_reducer)
        channels = self._build_channels(store, version, hosts)

        c = state.Context(version)
        c.functions = functions
        c.hosts = hosts
        c.expression_reducer = expression_reducer
        c.expression_checker = expression_checker
        c.expression_populator = expression_populator
        c.metrics_manager = self._build_metrics_manager(store, hosts, version);
        c.channels_manager = self._build_channels_manager(channels)
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
                hosts, metrics
        
        parser = LexYaccParser()
        parser.set_store(store) \
                .add_extension(main.ModelParserExtension()) \
                .add_extension(functions.ModelParserExtension()) \
                .add_extension(channels.ModelParserExtension()) \
                .add_extension(equations.ModelParserExtension()) \
                .add_extension(expressions.ModelParserExtension()) \
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
        from aqopa.model.parser.lex_yacc.grammar import main, metrics
        
        parser = LexYaccParser()
        parser.set_store(store)\
                .add_extension(main.MetricsParserExtension())\
                .add_extension(metrics.MetricsParserExtension())
                
        for m in modules:
            parser = m.extend_metrics_parser(parser)
                
        return parser.build()
    
    def build_config_parser(self, store, modules):
        """
        Builder parser that parses config written in QoPML
        and populates the store.
        """
        from aqopa.model.parser.lex_yacc import LexYaccParser
        from aqopa.model.parser.lex_yacc.grammar import versions, main
        
        parser = LexYaccParser()
        parser.set_store(store)\
                .add_extension(main.ConfigParserExtension())\
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
        
    def parse(self):
        """
        Parses the model from model_as_text field and populates the store.
        """
        if len(self.model_as_text) == 0:
            raise EnvironmentDefinitionException("QoPML Model not provided.")
    
        self.store = self.builder.build_store()
    
        parser = self.builder.build_model_parser(self.store, self._modules)
        parser.parse(self.model_as_text)
        if len(parser.get_syntax_errors()) > 0:
            raise ModelParserException('Invalid syntax.', syntax_errors=parser.get_syntax_errors())
    
        parser = self.builder.build_metrics_parser(self.store, self._modules)
        parser.parse(self.metrics_as_text)
        if len(parser.get_syntax_errors()) > 0:
            raise MetricsParserException('Invalid syntax.', syntax_errors=parser.get_syntax_errors())
    
        parser = self.builder.build_config_parser(self.store, self._modules)
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
