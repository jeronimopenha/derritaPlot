from math import ceil, log2

from jinja2.nodes import Pos
from setuptools.command.bdist_rpm import bdist_rpm
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

    def create_pe(self, nodes, treated_functions, hist_mem_bit_depth, std_comm_width=32):
        # the std_comm_width is the standard width to build the circuit
        # every communication to and from PE will be done with this width
        config_counter_width = 1 if ceil(log2(ceil(len(nodes) / std_comm_width)) * 2) == 0 else ceil(log2(
            ceil(len(nodes) / std_comm_width) * 2))

        name = 'pe'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)

        # standard I/O ports -------------------------------------------------------------------------------------------
        clk = m.Input('clk')
        rst = m.Input('rst')
        # --------------------------------------------------------------------------------------------------------------

        # PE configuration signals
        config_input_done = m.Input('config_input_done')
        config_input_valid = m.Input('config_input_valid')
        config_input = m.Input('config_input', std_comm_width)
        config_output = m.OutputReg('config_output', std_comm_width)
        # --------------------------------------------------------------------------------------------------------------

        # used to send any data from PE --------------------------------------------------------------------------------
        output_data_read = m.Input('output_data_read')
        output_data_valid = m.OutputReg('output_data_valid')
        output_data_sum = m.OutputReg('output_data_sum', std_comm_width)
        output_data_qty = m.OutputReg('output_data_qty', std_comm_width)
        # --------------------------------------------------------------------------------------------------------------

        # PE done_ signal
        done = m.OutputReg('done')
        # --------------------------------------------------------------------------------------------------------------

        # configuration wires and regs begin ---------------------------------------------------------------------------
        m.EmbeddedCode('\n//configuration wires and regs - begin')
        pe_init_conf = m.Reg('pe_init_conf', ceil(len(nodes) / std_comm_width) * std_comm_width)
        pe_end_conf = m.Reg('pe_end_conf', ceil(len(nodes) / std_comm_width) * std_comm_width)
        config_forward = m.Wire('config_forward', std_comm_width)
        config_output_forward = m.Wire('config_output_forward', std_comm_width)
        m.EmbeddedCode('//configuration wires and regs - end')
        # configuration wires and regs end -----------------------------------------------------------------------------

        # grn instantiation module wires and regs - begin --------------------------------------------------------------
        m.EmbeddedCode('\n//grn instantiation module wires and regs - begin')
        grn_input_data_valid = m.Reg('grn_input_data_valid', 2)
        grn_input_data = m.Reg('grn_input_data', len(nodes))
        grn_output_data_valid = m.Wire('grn_output_data_valid', 2)
        grn_output_data = m.Wire('grn_output_data', len(nodes))
        m.EmbeddedCode('//grn instantiation module wires and regs - end')
        # grn instantiation module wires and regs - end ----------------------------------------------------------------

        # Internal loop control wires and regs - begin -----------------------------------------------------------------
        m.EmbeddedCode('\n//Internal loop control wires and regs - begin')
        last_loop = m.Reg('last_loop')
        ctrl_hm_rd_add = m.Reg('ctrl_hm_rd_add', hist_mem_bit_depth)
        b_r = m.Reg('b_r', len(nodes))
        b_r_next = m.Reg('b_r_next', len(nodes))
        al_r = m.Reg('al_r', len(nodes))
        bl_r = m.Reg('bl_r', len(nodes))
        bl_r_v = m.Reg('bl_r_v')
        flag_first_iteration = m.Reg('flag_first_iteration')
        fsm_process = m.Reg('fsm_process', 5)
        fsm_process_init = m.Localparam('fsm_process_init', 0)
        fsm_process_loop = m.Localparam('fsm_process_loop', 1)
        fsm_process_wait_pipeline = m.Localparam('fsm_process_wait_pipeline', 2)
        fsm_process_discharge = m.Localparam('fsm_process_discharge', 3)
        fsm_process_verify = m.Localparam('fsm_process_verify', 4)
        fsm_process_done = m.Localparam('fsm_process_done', 5)
        m.EmbeddedCode('//Internal loop control wires and regs - end')
        # Internal loop control wires and regs - end -------------------------------------------------------------------

        # xor bit counters instantiation wires and regs - begin --------------------------------------------------------
        m.EmbeddedCode('\n//xor bit counters instantiation wires and regs - begin')
        qty_xbc3 = ceil(len(nodes) / 3)
        xbc3_add_output_data_valid = m.Wire('xbc3_add_output_data_valid', qty_xbc3)
        xbc3_add_output_data = m.Wire('xbc3_add_output_data', 2, qty_xbc3)
        xbc3_data_output_data_valid = m.Wire('xbc3_data_output_data_valid', qty_xbc3)
        xbc3_data_output_data = m.Wire('xbc3_data_output_data', 2, qty_xbc3)
        m.EmbeddedCode('//xor bit counters instantiation wires and regs - end')
        # xor bit counters instantiation wires and regs - end ----------------------------------------------------------

        # Histogram memory instantiation wires and regs - begin --------------------------------------------------------
        m.EmbeddedCode('\n//Histogram memory instantiation wires and regs - begin')
        hm_rd_data = m.Wire('hm_rd_data', std_comm_width)
        hm_rd_qtdy = m.Wire('hm_rd_qtdy', std_comm_width)
        hm_rdy = m.Wire('hm_rdy')
        hm_rd_add = m.Wire('hm_rd_add', hist_mem_bit_depth)
        hm_rd_add_selector = m.Reg('hm_rd_add_selector')
        m.EmbeddedCode('//Histogram memory instantiation wires and regs - end')
        # Histogram memory instantiation wires and regs - end ----------------------------------------------------------

        # sum loops for address and data lines wires and regs - begin --------------------------------------------------
        m.EmbeddedCode('\n//sum loops for address and data lines wires and regs - begin')
        xbc3_output_buses = ['xbc3_add_output_data[' + str(i) + ']' for i in range(qty_xbc3)]
        sum_counter = 0
        reg_counter = 0
        add_pipe_counter = 1
        str_embedded_add = ''
        sum_width = len(nodes)
        while len(xbc3_output_buses) > 1:
            process_items = []
            add_pipe_counter = add_pipe_counter + 1
            for i in range(len(xbc3_output_buses)):
                process_items.append(xbc3_output_buses.pop())
            while (len(process_items) > 0):
                if (len(process_items) > 1):
                    o_d_u1 = process_items.pop()
                    o_d_u2 = process_items.pop()
                    str_embedded_add = str_embedded_add + 'sum_add[' + str(
                        sum_counter) + '] <= ' + o_d_u1 + ' + ' + o_d_u2 + ';\n'
                    xbc3_output_buses.append('sum_add[' + str(sum_counter) + ']')
                    sum_counter = sum_counter + 1
                else:
                    o_d_u = process_items.pop()
                    str_embedded_add = str_embedded_add + 'reg_add[' + str(reg_counter) + '] <= ' + o_d_u + ';\n'
                    xbc3_output_buses.append('reg_add[' + str(reg_counter) + ']')
                    reg_counter = reg_counter + 1
        str_embedded_add = str_embedded_add + 'reg_add[' + str(reg_counter) + '] <= ' + 'sum_add[' + str(
            sum_counter - 1) + '];'
        sum_add = m.Reg('sum_add', sum_width, sum_counter)
        reg_add = m.Reg('reg_add', sum_width, reg_counter + 1)
        reg_add_valid_pipe = m.Reg('reg_add_valid_pipe', add_pipe_counter)
        wr_address = m.Wire('wr_address', hist_mem_bit_depth)
        wr = m.Wire('wr')

        xbc3_output_buses = ['xbc3_data_output_data[' + str(i) + ']' for i in range(qty_xbc3)]
        sum_counter = 0
        reg_counter = 0
        data_pipe_counter = 0
        str_embedded_data = ''
        while len(xbc3_output_buses) > 1:
            process_items = []
            data_pipe_counter = data_pipe_counter + 1
            for i in range(len(xbc3_output_buses)):
                process_items.append(xbc3_output_buses.pop())
            while (len(process_items) > 0):
                if (len(process_items) > 1):
                    o_d_u1 = process_items.pop()
                    o_d_u2 = process_items.pop()
                    str_embedded_data = str_embedded_data + 'sum_data[' + str(
                        sum_counter) + '] <= ' + o_d_u1 + ' + ' + o_d_u2 + ';\n'
                    xbc3_output_buses.append('sum_data[' + str(sum_counter) + ']')
                    sum_counter = sum_counter + 1
                else:
                    o_d_u = process_items.pop()
                    str_embedded_data = str_embedded_data + 'reg_data[' + str(reg_counter) + '] <= ' + o_d_u + ';\n'
                    xbc3_output_buses.append('reg_data[' + str(reg_counter) + ']')
                    reg_counter = reg_counter + 1

        sum_data = m.Reg('sum_data', sum_width, sum_counter)
        reg_data = m.Reg('reg_data', sum_width, reg_counter)
        reg_data_valid_pipe = m.Reg('reg_data_valid_pipe', data_pipe_counter)
        wr_data = m.Wire('wr_data', std_comm_width)
        wr_data_valid = m.Wire('wr_data_valid')
        m.EmbeddedCode('//sum loops for address and data lines wires and regs - end')
        # sum loops for address and data lines wires and regs - end ----------------------------------------------------

        # configuration sector -----------------------------------------------------------------------------------------
        m.EmbeddedCode('\n//configuration sector - begin')
        if pe_init_conf.width > std_comm_width:
            config_forward.assign(pe_end_conf[0:pe_end_conf.width - std_comm_width])
            config_output_forward.assign(pe_init_conf[0:pe_init_conf.width - std_comm_width])
        else:
            config_forward.assign(pe_end_conf)
            config_output_forward.assign(pe_init_conf)

        # PE configuration machine
        m.Always(Posedge(clk))(
            If(config_input_valid)(
                pe_end_conf(Cat(config_input, pe_end_conf[pe_end_conf.width - std_comm_width:pe_end_conf.width])
                            if pe_end_conf.width > std_comm_width else config_input),
                pe_init_conf(Cat(config_forward, pe_init_conf[pe_init_conf.width - std_comm_width:pe_init_conf.width])
                             if pe_init_conf.width > std_comm_width else config_forward),
                config_output(config_output_forward),
            ),
        )
        m.EmbeddedCode('//configuration sector - end')
        # configuration sector - end -----------------------------------------------------------------------------------

        # Internal loop control - begin --------------------------------------------------------------------------------
        m.EmbeddedCode('\n//Internal loop control - begin')
        m.Always(Posedge(clk))(
            If(grn_output_data_valid[1])(
                al_r(grn_output_data),
            ),
            If(grn_output_data_valid[0])(
                bl_r(grn_output_data),
                bl_r_v(1),
            ).Else(
                bl_r_v(0),
            )
        )

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_process(fsm_process_init),
                grn_input_data_valid(0),
                last_loop(0),
                done(0),
            ).Elif(AndList(config_input_done, hm_rdy))(
                Case(fsm_process)(
                    When(fsm_process_init)(
                        # here I initiate the a_r and ACC values
                        b_r(pe_init_conf[0:b_r.width]),
                        grn_input_data_valid(2),
                        b_r_next(pe_init_conf[0:b_r_next.width] + 1),
                        flag_first_iteration(1),
                        fsm_process(fsm_process_loop),
                        hm_rd_add_selector(0),
                    ),
                    When(fsm_process_loop)(
                        # here I initiate the 1-pass GRN output for a_r
                        grn_input_data(b_r),
                        b_r.inc(),
                        b_r_next.inc(),
                        grn_input_data_valid(1),
                        If(b_r_next == pe_init_conf[0:b_r_next.width])(
                            grn_input_data_valid(0),
                            pe_init_conf(pe_init_conf[0:b_r_next.width] + 1),
                            fsm_process(fsm_process_verify),
                        ),
                    ),
                    When(fsm_process_verify)(
                        fsm_process(fsm_process_init),
                        If(pe_init_conf[0:b_r_next.width] == pe_end_conf[0:b_r_next.width])(
                            last_loop(1),
                        ).Elif(last_loop)(
                            fsm_process(fsm_process_wait_pipeline),
                        )
                    ),
                    When(fsm_process_wait_pipeline)(
                        If(~wr)(
                            fsm_process(fsm_process_discharge),
                            hm_rd_add_selector(1),
                            ctrl_hm_rd_add(0),
                        )
                    ),
                    When(fsm_process_discharge)(
                        output_data_sum(hm_rd_data),
                        output_data_qty(hm_rd_qtdy),
                        If(output_data_read)(
                            ctrl_hm_rd_add.inc(),
                        ),
                        If(Uand(ctrl_hm_rd_add))(
                            output_data_valid(0),
                            fsm_process(fsm_process_done),
                        ).Else(
                            output_data_valid(1),
                        )
                    ),

                    When(fsm_process_done)(
                        done(1),
                    ),
                ),
            )
        )
        m.EmbeddedCode('//Internal loop control - end')
        # Internal loop control - end ----------------------------------------------------------------------------------

        # sum loop for address line sector - begin ---------------------------------------------------------------------
        m.EmbeddedCode('\n//sum loop for address line sector - begin')
        wr_address.assign(sum_add[sum_counter - 1])
        wr.assign(reg_add_valid_pipe[add_pipe_counter - 1])
        m.Always(Posedge(clk))(
            EmbeddedNumeric(str_embedded_add)
        )
        str_embedded = 'reg_add_valid_pipe[0] <= xbc3_add_output_data_valid[0];\n'
        for i in range(1, add_pipe_counter):
            str_embedded = str_embedded + 'reg_add_valid_pipe[' + str(i) + '] <= reg_add_valid_pipe[' + str(
                i - 1) + '];\n'
        m.Always(Posedge(clk))(
            EmbeddedNumeric(str_embedded)
        )
        m.EmbeddedCode('//sum loop for address line sector - end')
        # sum loop for address line sector - end -----------------------------------------------------------------------

        # sum loop for data line sector - begin ------------------------------------------------------------------------
        m.EmbeddedCode('\n//sum loop for data line sector - begin')
        wr_data.assign(sum_data[sum_counter - 1])
        wr_data_valid.assign(reg_data_valid_pipe[data_pipe_counter - 1])

        m.Always(Posedge(clk))(
            EmbeddedNumeric(str_embedded_data)
        )

        str_embedded = 'reg_data_valid_pipe[0] <= xbc3_data_output_data_valid[0];\n'
        for i in range(1, data_pipe_counter):
            str_embedded = str_embedded + 'reg_data_valid_pipe[' + str(i) + '] <= reg_data_valid_pipe[' + str(
                i - 1) + '];\n'

        m.Always(Posedge(clk))(
            EmbeddedNumeric(str_embedded)
        )
        m.EmbeddedCode('//sum loop for data line sector - end')
        # sum loop for data line sector - begin ------------------------------------------------------------------------

        # grn module instantiation sector - begin ----------------------------------------------------------------------
        m.EmbeddedCode('\n//grn module instantiation sector - begin')
        params = []
        con = [
            ('clk', clk),
            ('input_data_valid', grn_input_data_valid),
            ('input_data', b_r),
            ('output_data_valid', grn_output_data_valid),
            ('output_data', grn_output_data)
        ]
        grn = self.create_grn_module(nodes, treated_functions)
        m.Instance(grn, grn.name, params, con)
        m.EmbeddedCode('//grn module instantiation sector - end')
        # grn module instantiation sector - end ------------------------------------------------------------------------

        # xor bit counters instantiation sector - begin ----------------------------------------------------------------
        m.EmbeddedCode('\n//xor bit counters instantiation sector - begin')
        params = []
        for i in range(0, qty_xbc3):
            b_init = i * 3
            b_fim = i * 3 + 3 if b_r.width >= i * 3 + 3 else b_r.width
            dif_width = i * 3 + 3 - b_r.width
            flag_cat = True if b_r.width >= i * 3 + 3 else False
            con = [
                ('clk', clk),
                ('input_data_valid', grn_input_data_valid[0]),
                ('input_data', Cat(pe_init_conf[b_init: b_fim], b_r[b_init: b_fim]) if flag_cat else Cat(
                    Cat(Int(0, dif_width, 10), pe_init_conf[b_init: b_fim]),
                    Cat(Int(0, dif_width, 10), b_r[b_init: b_fim]))),
                ('output_data_valid', xbc3_add_output_data_valid[i]),
                ('output_data', xbc3_add_output_data[i]),
            ]
            grn = self.create_xor_bit_counter_3b()
            m.Instance(grn, grn.name + '_add_' + str(i), params, con)

        for i in range(0, qty_xbc3):
            b_init = i * 3
            b_fim = i * 3 + 3 if b_r.width >= i * 3 + 3 else b_r.width
            dif_width = i * 3 + 3 - b_r.width
            flag_cat = True if b_r.width >= i * 3 + 3 else False
            con = [
                ('clk', clk),
                ('input_data_valid', grn_output_data_valid[0]),
                ('input_data', Cat(al_r[b_init: b_fim], grn_output_data[b_init: b_fim]) if flag_cat else Cat(
                    Cat(Int(0, dif_width, 10), al_r[b_init: b_fim]),
                    Cat(Int(0, dif_width, 10), grn_output_data[b_init: b_fim]))),
                ('output_data_valid', xbc3_data_output_data_valid[i]),
                ('output_data', xbc3_data_output_data[i]),
            ]
            grn = self.create_xor_bit_counter_3b()
            m.Instance(grn, grn.name + '_data_' + str(i), params, con)

        m.EmbeddedCode('//xor bit counters instantiation sector - end')
        # xor bit counters instantiation sector - end ------------------------------------------------------------------

        # histogram memory sector - Begin ------------------------------------------------------------------------------
        m.EmbeddedCode('\n//histogram memory sector - Begin')
        hm_rd_add.assign(Mux(hm_rd_add_selector, ctrl_hm_rd_add, wr_address))
        params = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('rd_add', hm_rd_add[0:hist_mem_bit_depth] if len(nodes) > hist_mem_bit_depth else hm_rd_add),
            ('wr', wr),
            ('wr_add', wr_address),
            ('wr_data', wr_data),
            ('rd_data', hm_rd_data),
            ('rdy', hm_rdy)
        ]
        hm = self.create_histogram_memory(hist_mem_bit_depth, std_comm_width)
        m.Instance(hm, hm.name, params, con)
        m.EmbeddedCode('//histogram memory sector - Begin')
        # histogram memory sector - End --------------------------------------------------------------------------------

        # simulation sector - begin ------------------------------------------------------------------------------------
        m.EmbeddedCode('\n//simulation sector - begin')
        initialize_regs(m)
        m.EmbeddedCode('//simulation sector - begin')
        # simulation sector - end --------------------------------------------------------------------------------------
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
        input_data_valid = m.Input('input_data_valid', 2)
        input_data = m.Input('input_data', data_width)
        output_data_valid = m.OutputReg('output_data_valid', 2)
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
        rd_qty = m.Output('rd_qty', data_width)
        rdy = m.OutputReg('rdy')

        rst_counter = m.Reg('rst_counter', bit_depth)
        flag_rst = m.Reg('flag_rst')

        valid = m.Reg('valid', pow(2, bit_depth))
        sum_m = m.Reg('sum_m', data_width, pow(2, bit_depth))
        qty_m = m.Reg('qty_m', data_width, pow(2, bit_depth))

        rd_data.assign(Mux(valid[rd_add], sum_m[rd_add], 0))
        rd_qty.assign(qty_m[rd_add])

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
                    qty_m[rst_counter](0),
                    rst_counter.inc(),
                )
            ).Elif(wr)(
                sum_m[wr_add](wr_data + rd_data),
                qty_m[wr_data](rd_qty + 1),
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


'''components = Components()
functions = sorted(readGRN('../Benchmarks/Benchmark_5.txt'))
# functions = sorted(readGRN('../Benchmarks/B_bronchiseptica.txt'))
nodes, treated_functions = treat_functions(functions)
print(components.create_PE(nodes, treated_functions).to_verilog())
'''
'''
print(components.create_histogram_memory(5, 32).to_verilog())
'''
'''
functions = sorted(readGRN('../Benchmarks/Benchmark_5.txt'))
nodes, treated_functions = treat_functions(functions)

print(components.create_grn_module(nodes, treated_functions).to_verilog())
'''
