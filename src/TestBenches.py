from veriloggen import *
from src.Components import Components
from src.utils import initialize_regs, treat_functions, readGRN
from math import pow, ceil, log2

p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if not p in sys.path:
    sys.path.insert(0, p)


class TestBenches:

    def __init__(self):
        self.components = Components()

    def create_xor_bit_counter_3b_test_bench(self):
        # DATA PRODUCER ------------------------------------------------------------------------------------------------
        dp_output_data_width = 6
        dp_num_data = pow(2, 6)
        dp = Module('data_producer')

        # Control signals for the component
        dp_clk = dp.Input('dp_clk')
        dp_rst = dp.Input('dp_rst')

        # Ports for delivery of data to the consumer
        dp_output_data_valid = dp.OutputReg('dp_output_data_valid')
        dp_output_data = dp.OutputReg('dp_output_data', dp_output_data_width)
        dp_done = dp.OutputReg('dp_done')

        dp_data_counter = dp.Reg('dp_data_counter', dp_output_data_width)

        dp_fsm = dp.Reg('dp_fsm')
        dp_fsm_to_produce = dp.Localparam('dp_fsm_to_produce', 0)
        dp_fsm_done = dp.Localparam('dp_fsm_done', 1)

        dp.Always(Posedge(dp_clk))(
            If(dp_rst)(
                dp_data_counter(0),
                dp_output_data_valid(0),
                dp_done(0),
                dp_output_data(0),
                dp_fsm(dp_fsm_to_produce),
            ).Else(
                Case(dp_fsm)(
                    When(dp_fsm_to_produce)(
                        dp_output_data_valid(1),
                        dp_output_data(dp_data_counter),
                        dp_data_counter.inc(),
                        If(dp_data_counter == dp_num_data - 1)(
                            dp_fsm(dp_fsm_done),
                        )
                    ),
                    When(dp_fsm_done)(
                        dp_output_data_valid(0),
                        dp_output_data(0),
                        dp_done(1),
                    ),
                )
            )
        )

        initialize_regs(dp)
        # END DATA PRODUCER --------------------------------------------------------------------------------------------

        # TEST BENCH MODULE --------------------------------------------------------------------------------------------
        xbc3_output_data_width = 2

        tb = Module('test_bench')
        tb_clk = tb.Reg('tb_clk')
        tb_rst = tb.Reg('tb_rst')

        tb_dp_output_data_valid = tb.Wire('tb_dp_output_data_valid')
        tb_dp_output_data = tb.Wire('tb_dp_output_data', dp_output_data_width)
        tb_dp_done = tb.Wire('tb_dp_done')

        xbc3_output_data_valid = tb.Wire('xbc3_output_data_valid')
        xbc3_output_data = tb.Wire('xbc3_output_data', xbc3_output_data_width)

        tb_done = tb.Wire('tb_done')

        params = []
        con = [('dp_clk', tb_clk),
               ('dp_rst', tb_rst),
               ('dp_output_data_valid', tb_dp_output_data_valid),
               ('dp_output_data', tb_dp_output_data),
               ('dp_done', tb_dp_done)
               ]
        tb.Instance(dp, dp.name, params, con)

        params = []
        con = [('clk', tb_clk),
               ('input_data_valid', tb_dp_output_data_valid),
               ('input_data', tb_dp_output_data),
               ('output_data_valid', xbc3_output_data_valid),
               ('output_data', xbc3_output_data)
               ]

        xbc3 = self.components.create_xor_bit_counter_3b()
        tb.Instance(xbc3, xbc3.name, params, con)

        tb_done.assign(tb_dp_done & ~xbc3_output_data_valid)

        initialize_regs(tb, {'tb_clk': 0, 'tb_rst': 1})

        simulation.setup_waveform(tb)

        tb.Initial(
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            tb_rst(0),
            Delay(10000), Finish()
        )
        tb.EmbeddedCode('always #5tb_clk=~tb_clk;')

        tb.Always(Posedge(tb_clk))(
            If(tb_done)(
                # Display('ACC DONE!'),
                Finish()
            )
        )

        tb.to_verilog("../test_benches/xor_bit_counter_3b_test_bench.v")
        sim = simulation.Simulator(tb, sim='iverilog')
        rslt = sim.run()

    def create_grn_test_bench(self, benchmark):
        functions = sorted(readGRN(benchmark))
        nodes, treated_functions = treat_functions(functions)

        # DATA PRODUCER ------------------------------------------------------------------------------------------------
        dp_output_data_width = len(nodes)
        dp_num_data = pow(2, dp_output_data_width)
        dp = Module('data_producer')

        # Control signals for the component
        dp_clk = dp.Input('dp_clk')
        dp_rst = dp.Input('dp_rst')

        # Ports for delivery of data to the consumer
        dp_output_data_valid = dp.OutputReg('dp_output_data_valid')
        dp_output_data = dp.OutputReg('dp_output_data', dp_output_data_width)
        dp_done = dp.OutputReg('dp_done')

        dp_data_counter = dp.Reg('dp_data_counter', dp_output_data_width)

        dp_fsm = dp.Reg('dp_fsm')
        dp_fsm_to_produce = dp.Localparam('dp_fsm_to_produce', 0)
        dp_fsm_done = dp.Localparam('dp_fsm_done', 1)

        dp.Always(Posedge(dp_clk))(
            If(dp_rst)(
                dp_data_counter(0),
                dp_output_data_valid(0),
                dp_done(0),
                dp_output_data(0),
                dp_fsm(dp_fsm_to_produce),
            ).Else(
                Case(dp_fsm)(
                    When(dp_fsm_to_produce)(
                        dp_output_data_valid(1),
                        dp_output_data(dp_data_counter),
                        dp_data_counter.inc(),
                        If(dp_data_counter == dp_num_data - 1)(
                            dp_fsm(dp_fsm_done),
                        )
                    ),
                    When(dp_fsm_done)(
                        dp_output_data_valid(0),
                        dp_output_data(0),
                        dp_done(1),
                    ),
                )
            )
        )

        initialize_regs(dp)
        # END DATA PRODUCER --------------------------------------------------------------------------------------------

        # TEST BENCH MODULE --------------------------------------------------------------------------------------------
        grn_data_width = dp_output_data_width

        tb = Module('test_bench')
        tb_clk = tb.Reg('tb_clk')
        tb_rst = tb.Reg('tb_rst')

        tb_dp_output_data_valid = tb.Wire('tb_dp_output_data_valid')
        tb_dp_output_data = tb.Wire('tb_dp_output_data', dp_output_data_width)
        tb_dp_done = tb.Wire('tb_dp_done')

        grn_output_data_valid = tb.Wire('grn_output_data_valid')
        grn_output_data = tb.Wire('grn_output_data', grn_data_width)

        tb_done = tb.Wire('tb_done')

        params = []
        con = [('dp_clk', tb_clk),
               ('dp_rst', tb_rst),
               ('dp_output_data_valid', tb_dp_output_data_valid),
               ('dp_output_data', tb_dp_output_data),
               ('dp_done', tb_dp_done)
               ]
        tb.Instance(dp, dp.name, params, con)

        params = []
        con = [('clk', tb_clk),
               ('input_data_valid', tb_dp_output_data_valid),
               ('input_data', tb_dp_output_data),
               ('output_data_valid', grn_output_data_valid),
               ('output_data', grn_output_data)
               ]
        grn = self.components.create_grn_module(nodes, treated_functions)
        tb.Instance(grn, grn.name, params, con)

        tb_done.assign(tb_dp_done & ~grn_output_data_valid)

        initialize_regs(tb, {'tb_clk': 0, 'tb_rst': 1})

        simulation.setup_waveform(tb)

        tb.Initial(
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            tb_rst(0),
            Delay(10000), Finish()
        )
        tb.EmbeddedCode('always #5tb_clk=~tb_clk;')

        tb.Always(Posedge(tb_clk))(
            If(tb_done)(
                # Display('ACC DONE!'),
                Finish()
            )
        )

        tb.to_verilog("../test_benches/grn_test_bench.v")
        sim = simulation.Simulator(tb, sim='iverilog')
        rslt = sim.run()

    def create_histogram_memory_test_bench(self):
        data_width = 8
        memory_depth = 3
        data_quantity = pow(2, 6)

        # TEST BENCH MODULE --------------------------------------------------------------------------------------------

        tb = Module('test_bench')
        tb_clk = tb.Reg('tb_clk')
        tb_rst = tb.Reg('tb_rst')

        tb_wr = tb.Reg('tb_wr')
        tb_add = tb.Reg('tb_add', memory_depth)
        tb_wr_data = tb.Reg('tb_wr_data', data_width)
        counter_wr = tb.Reg('counter_wr', ceil(log2(data_quantity)))
        counter_rd = tb.Reg('counter_rd', memory_depth)
        tb_done = tb.Reg('td_done')

        hm_rd_data = tb.Wire('hm_rd_data', data_width)
        hm_rdy = tb.Wire('hm_rdy')

        tb.Always(Posedge(tb_clk))(
            If(tb_rst)(
                tb_wr(0),
                counter_wr(0),
                counter_rd(0),
                tb_done(0)
            ).Else(
                If(hm_rdy)(
                    If(Uand(counter_wr))(
                        tb_wr(0),
                        If(Uand(counter_rd))(
                            tb_done(1)
                        ).Else(
                            tb_add(counter_rd),
                            counter_rd.inc()
                        )
                    ).Else(
                        tb_wr(1),
                        tb_add(EmbeddedNumeric('$random%' + str(pow(2, memory_depth)))),
                        tb_wr_data(EmbeddedNumeric('$random%2') + hm_rd_data),
                        counter_wr.inc()
                    )
                )
            )
        )

        params = []
        con = [('clk', tb_clk),
               ('rst', tb_rst),
               ('rd_add', tb_add),
               ('wr', tb_wr),
               ('wr_add', tb_add),
               ('wr_data', tb_wr_data),
               ('rd_data', hm_rd_data),
               ('rdy', hm_rdy)
               ]

        hm = self.components.create_histogram_memory(memory_depth, data_width)
        tb.Instance(hm, hm.name, params, con)

        initialize_regs(tb, {'tb_clk': 0, 'tb_rst': 1})

        simulation.setup_waveform(tb)

        tb.Initial(
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            tb_rst(0),
            Delay(10000), Finish()
        )
        tb.EmbeddedCode('always #5tb_clk=~tb_clk;')

        tb.Always(Posedge(tb_clk))(
            If(tb_done)(
                # Display('ACC DONE!'),
                Finish()
            )
        )

        tb.to_verilog("../test_benches/histogram_memory_test_bench.v")
        sim = simulation.Simulator(tb, sim='iverilog')
        rslt = sim.run()
        a = 1


test_benches = TestBenches()
test_benches.create_histogram_memory_test_bench()
test_benches.create_grn_test_bench('../Benchmarks/Benchmark_5.txt')
test_benches.create_xor_bit_counter_3b_test_bench()
