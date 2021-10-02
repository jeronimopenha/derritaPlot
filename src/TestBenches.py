import os
import sys
from veriloggen import *
from src.Components import Components
from src.utils import initialize_regs

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
        dp_mem_dimension = pow(2, 6)
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

        dp_data_out_rom = dp.Wire('dp_data_out_rom', dp_output_data_width, dp_mem_dimension)

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
                        dp_output_data(dp_data_out_rom[dp_data_counter]),
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

        for i in range(0, 64):
            dp_data_out_rom[i].assign(Int(i, dp_output_data_width, 2))

        initialize_regs(dp)
        # END DATA PRODUCER --------------------------------------------------------------------------------------------

        # TEST BENCH MODULE --------------------------------------------------------------------------------------------
        xbc3_output_data_width = 2

        tb = Module('tb')
        tb_clk = tb.Reg('tb_clk')
        tb_rst = tb.Reg('tb_rst')

        tb_dp_output_data_valid = tb.Wire('tb_dp_output_data_valid')
        tb_dp_output_data = tb.Wire('tb_dp_output_data', dp_output_data_width)
        tb_dp_done = tb.Wire('tb_dp_done')

        xbc3_output_valid = tb.Wire('xbc3_output_valid')
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
               ('input_valid', tb_dp_output_data_valid),
               ('input_data', tb_dp_output_data),
               ('output_valid', xbc3_output_valid),
               ('output_data', xbc3_output_data)
               ]
        components = Components()
        xbc3 = components.create_xor_bit_counter_3b()
        tb.Instance(xbc3, xbc3.name, params, con)

        tb_done.assign(tb_dp_done & ~xbc3_output_valid)

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

        tb.to_verilog("../test_benches/xor_bit_counter_3b_text_bench.v")
        sim = simulation.Simulator(tb, sim='iverilog')
        rslt = sim.run()


        
test_benches = TestBenches()
test_benches.create_xor_bit_counter_3b_test_bench()
