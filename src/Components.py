from veriloggen import *
from utils import initialize_regs, bits


class Components:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cache = {}

    def create_xor_bit_counter_3b(self):
        input_width = 6
        output_width = 2
        mem_dimension = pow(2, 6)

        name = 'xor_bit_counter_3b'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input('clk')
        input_valid = m.Input('input_valid')
        input_data = m.Input('input_data', input_width)
        output_valid = m.OutputReg('output_valid')
        output_data = m.OutputReg('output_data', output_width)

        xor_bit_counter_rom = m.Wire('xor_bit_counter_rom', output_width, mem_dimension)

        m.Always(Posedge(clk))(
            output_valid(input_valid),
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

    def create_register_pipeline(self):
        name = 'reg_pipe'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module('reg_pipe')
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

