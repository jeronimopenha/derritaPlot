from setuptools.command.register import register
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


#components = Components()
'''
print(components.create_histogram_memory(5, 32).to_verilog())
'''
'''
functions = sorted(readGRN('../Benchmarks/Benchmark_5.txt'))
nodes, treated_functions = treat_functions(functions)

print(components.create_grn_module(nodes, treated_functions).to_verilog())
'''
