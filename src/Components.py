from math import ceil, log2

from jinja2.nodes import Pos
from veriloggen import *

from utils import initialize_regs, bits, readGRN, treat_functions


class Components:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cache = {}

    def create_PE(self, nodes, treated_functions, id_width=32, std_comm_width=32):
        # the std_comm_width is the standard width to build the circuit
        # every communication to and from PE will be done with this width
        config_counter_width = 1 if ceil(log2(ceil(len(nodes) / std_comm_width)) * 2) == 0 else ceil(log2(
            ceil(len(nodes) / std_comm_width) * 2))

        name = 'pe'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)

        # id for configuration -----------------------------------------------------------------------------------------
        id = m.Parameter('id', Int(0, id_width, 10))
        # --------------------------------------------------------------------------------------------------------------

        # standard I/O ports -------------------------------------------------------------------------------------------
        clk = m.Input('clk')
        rst = m.Input('rst')
        # PE configuration signal
        config = m.Input('config')
        input_id = m.Input('input_id', id_width)
        # start_process_signal
        start = m.Input('start')
        # --------------------------------------------------------------------------------------------------------------

        # used to receive any data to PE -------------------------------------------------------------------------------
        input_data_valid = m.Input('input_data_valid')
        input_data = m.Input('input_data', std_comm_width)
        # --------------------------------------------------------------------------------------------------------------

        # used to send any data from PE --------------------------------------------------------------------------------
        output_data_valid = m.Input('output_data_valid')
        output_data = m.Input('output_data', std_comm_width)
        # --------------------------------------------------------------------------------------------------------------

        # PE done_ signal
        done = m.OutputReg('done')
        # --------------------------------------------------------------------------------------------------------------

        # configuration sector -----------------------------------------------------------------------------------------
        m.EmbeddedCode('\n//configuration sector - begin')
        grn_init_conf = m.Reg('grn_init_conf', ceil(len(nodes) / std_comm_width) * std_comm_width)
        grn_end_conf = m.Reg('grn_end_conf', ceil(len(nodes) / std_comm_width) * std_comm_width)

        config_counter1 = m.Reg('config_counter1', config_counter_width)
        config_counter2 = m.Reg('config_counter2', config_counter_width)

        # PE configuration machine
        m.Always(Posedge(clk))(
            If(rst)(
                config_counter1(0),
                config_counter2(0),
            ).Else(
                If(config)(
                    If(input_id == id)(
                        If(Uand(config_counter1))(
                            If(~Uand(config_counter2))(
                                grn_end_conf(Cat(grn_end_conf[0:grn_end_conf.width - std_comm_width], input_data)
                                             if grn_end_conf.width > std_comm_width else input_data),
                                config_counter2.inc()
                            )
                        ).Else(
                            grn_init_conf(Cat(grn_init_conf[0:grn_init_conf.width - std_comm_width], input_data)
                                          if grn_init_conf.width > std_comm_width else input_data),
                            config_counter1.inc()
                        )
                    )

                )
            )
        )
        m.EmbeddedCode('//configuration sector - end')
        # configuration sector - end -----------------------------------------------------------------------------------

        # Acc working control - begin ----------------------------------------------------------------------------------
        m.EmbeddedCode('\n//Acc working control - begin')
        grn_input_data_valid = m.Reg('grn_input_data_valid')
        grn_output_data_valid = m.Wire('grn_output_data_valid')
        grn_output_data = m.Wire('grn_output_data', len(nodes))

        fsm_process = m.Reg('fsm_process', 3)
        fsm_process_init = m.Localparam('fsm_process_init', 0)
        fsm_process_loop_init = m.Localparam('fsm_process_loop_init', 1)
        fsm_process_loop = m.Localparam('fsm_process_loop', 2)
        fsm_process_discharge = m.Localparam('fsm_process_discharge', 3)
        fsm_process_verify = m.Localparam('fsm_process_verify', 4)
        fsm_process_done = m.Localparam('fsm_process_done', 5)

        acc = m.Reg('acc', len(nodes))
        base_state = m.Reg('base_state', len(nodes))

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_process(fsm_process_init)
            ).Elif(start)(
                Case(fsm_process)(
                    When(fsm_process_init)(
                        # here I initiate the base_state and ACC values
                        base_state(grn_init_conf[0:base_state.width]),
                        acc(grn_init_conf[0:base_state.width])
                    ),
                    When(fsm_process_loop_init)(
                        # here I initiate the 1-pass GRN output for base_state

                    ),
                    When(fsm_process_loop)(

                    ),
                    When(fsm_process_discharge)(

                    ),
                    When(fsm_process_verify)(
                        If(base_state != grn_end_conf)(
                            grn_init_conf.inc(),
                            fsm_process(fsm_process_init)
                        )
                    ),
                    When(fsm_process_done)(

                    ),
                ),

            )
        )

        # grn module instantiation sector - begin ----------------------------------------------------------------------
        m.EmbeddedCode('\n//grn module instantiation sector - begin')
        params = []
        con = [
            ('clk', clk),
            ('input_data_valid', grn_input_data_valid),
            ('input_data', acc),
            ('output_data_valid', grn_output_data_valid),
            ('output_data', grn_output_data)
        ]
        grn = self.create_grn_module(nodes, treated_functions)
        m.Instance(grn, grn.name, params, con)

        m.EmbeddedCode('//grn module instantiation sector - end')
        # grn module instantiation sector - end ------------------------------------------------------------------------

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_grn_module(self, nodes, treated_functions):
        data_width = len(nodes)
        wires = []
        regs = []

        name = 'grn'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)

        clk = m.Input('clk')
        input_data_valid = m.Input('input_data_valid')
        input_data = m.Input('input_data', data_width)
        output_data_valid = m.OutputReg('output_data_valid')
        output_data = m.Output('output_data', data_width)

        for node in nodes:
            regs.append(m.Reg(node + '_r'))
        for node in nodes:
            wires.append(m.Wire(node))
        tf = ''
        for i in range(len(treated_functions)):
            if i > 0:
                tf = tf + '\n'
            tf = tf + treated_functions[i].split('=')[0].replace(' ', '') + '_r <= ' + \
                 treated_functions[i].split('=')[1] + ';'

        m.Always(Posedge(clk))(
            output_data_valid(input_data_valid),
            EmbeddedNumeric(tf)
        )

        counter = 0
        for wire in wires:
            wire.assign(input_data[counter])
            counter = counter + 1

        counter = 0
        for reg in regs:
            output_data[counter].assign(regs[counter])
            counter = counter + 1
        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_xor_bit_counter_3b(self):
        input_width = 6
        output_width = 2
        mem_dimension = pow(2, 6)

        name = 'xor_bit_counter_3b'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input('clk')
        input_data_valid = m.Input('input_data_valid')
        input_data = m.Input('input_data', input_width)
        output_data_valid = m.OutputReg('output_data_valid')
        output_data = m.OutputReg('output_data', output_width)

        xor_bit_counter_rom = m.Wire('xor_bit_counter_rom', output_width, mem_dimension)

        m.Always(Posedge(clk))(
            output_data_valid(input_data_valid),
            output_data(xor_bit_counter_rom[input_data])
        )

        for i in range(0, 64):
            a = i & 0x7
            b = (i >> 3) & 0x7
            a = a ^ b
            counter = 0
            for j in range(0, 3):
                if a & 1 == 1:
                    counter = counter + 1
                a = a >> 1
            # print(bin(counter))
            xor_bit_counter_rom[i].assign(Int(counter, output_width, 2))

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_mux(self):
        name = 'mux'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)
        data_width = m.Parameter('data_width', 32)

        input_data_a = m.Input('input_data_a', data_width)
        input_data_b = m.Input('input_data_b', data_width)
        selector = m.Input('selector', )
        output_data = m.Output('output_data', data_width)

        output_data.assign(Mux(selector, input_data_b, input_data_a))
        self.cache[name] = m
        return m

    def create_histogram_memory(self, bit_depth, data_width):
        name = 'histogram_memory'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        rd_add = m.Input('rd_add', bit_depth)
        wr = m.Input('wr')
        wr_add = m.Input('wr_add', bit_depth)
        wr_data = m.Input('wr_data', data_width)
        rd_data = m.Output('rd_data', data_width)
        rdy = m.OutputReg('rdy')

        rst_counter = m.Reg('rst_counter', bit_depth)
        flag_rst = m.Reg('flag_rst')

        valid = m.Reg('valid', pow(2, bit_depth))
        mem = m.Reg('mem', data_width, pow(2, bit_depth))

        rd_data.assign(Mux(valid[rd_add], mem[rd_add], 0))

        m.Always(Posedge(clk))(
            If(rst)(
                rdy(0),
                flag_rst(1),
                rst_counter(0),
            ).Elif(flag_rst)(
                If(Uand(rst_counter))(
                    rdy(1),
                    flag_rst(0)
                ).Else(
                    valid[rst_counter](0),
                    rst_counter.inc(),
                )
            ).Elif(wr)(
                mem[wr_add](wr_data),
                valid[wr_add](1)
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_register_pipeline(self):
        name = 'reg_pipe'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        num_stages = m.Parameter('num_register', 1)
        data_width = m.Parameter('width', 16)

        clk = m.Input('clk')
        en = m.Input('en')
        rst = m.Input('rst')
        data_in = m.Input('in', data_width)
        data_out = m.Output('out', data_width)

        m.EmbeddedCode('(* keep = "true" *)')
        regs = m.Reg('regs', data_width, num_stages)
        i = m.Integer('i')
        m.EmbeddedCode('')
        data_out.assign(regs[num_stages - 1])
        m.Always(Posedge(clk))(
            If(rst)(
                regs[0](0),
            ).Else(
                If(en)(
                    regs[0](data_in),
                    For(i(1), i < num_stages, i.inc())(
                        regs[i](regs[i - 1])
                    )
                )
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m


components = Components()
functions = sorted(readGRN('../Benchmarks/Benchmark_5.txt'))
# functions = sorted(readGRN('../Benchmarks/B_bronchiseptica.txt'))
nodes, treated_functions = treat_functions(functions)
print(components.create_PE(nodes, treated_functions).to_verilog())
'''
print(components.create_histogram_memory(5, 32).to_verilog())
'''
'''
functions = sorted(readGRN('../Benchmarks/Benchmark_5.txt'))
nodes, treated_functions = treat_functions(functions)

print(components.create_grn_module(nodes, treated_functions).to_verilog())
'''
