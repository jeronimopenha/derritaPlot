from PIL.ImageQt import qt_module
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

    def create_pe_test_bench(self, benchmark):
        functions = sorted(readGRN(benchmark))
        nodes, treated_functions = treat_functions(functions)
        id_width = 32
        std_comm_width = 32

        # TEST BENCH MODULE --------------------------------------------------------------------------------------------
        tb = Module('test_bench')

        tb.EmbeddedCode('\n//Standar I/O signals - Begin')
        tb_clk = tb.Reg('tb_clk')
        tb_rst = tb.Reg('tb_rst')
        tb.EmbeddedCode('//Standar I/O signals - End')

        tb.EmbeddedCode('\n//Configuration Signals - Begin')
        tb_config_input_done = tb.Reg('tb_config_input_done')
        pe_config_input_valid = tb.Reg('pe_config_input_valid')
        pe_config_input = tb.Reg('pe_config_input', std_comm_width)
        pe_config_output = tb.Wire('pe_config_output', std_comm_width)
        tb.EmbeddedCode('//Configuration Signals - End')

        tb.EmbeddedCode('\n//Data Transfer Signals - Begin')
        tb_data_valid = tb.Reg('tb_data_valid')
        tb_input_data = tb.Reg('tb_input_data', std_comm_width)
        pe_output_data_valid = tb.Wire('pe_output_data_valid')
        pe_output_data = tb.Wire('pe_output_data', std_comm_width)
        tb.EmbeddedCode('//Data Transfer Signals - End')

        pe_done = tb.Wire('pe_done')

        params = []
        con = [('clk', tb_clk),
               ('rst', tb_rst),
               ('config_input_done', tb_config_input_done),
               ('config_input_valid', pe_config_input_valid),
               ('config_input', pe_config_input),
               ('config_output', pe_config_output),
               ('input_data_valid', tb_data_valid),
               ('input_data', tb_input_data),
               ('output_data_valid', pe_output_data_valid),
               ('output_data', pe_output_data),
               ('done', pe_done)
               ]

        pe = self.components.create_PE(nodes, treated_functions, std_comm_width)
        tb.Instance(pe, pe.name, params, con)

        tb.EmbeddedCode('\n//Configuraton Memory section - Begin')

        init_state = 1
        end_state = 5
        bits_grn = len(nodes)
        qtde_conf = ceil(bits_grn / std_comm_width) * 2

        config_rom = tb.Wire('config_rom', std_comm_width, qtde_conf)
        for i in range(qtde_conf):
            if i < qtde_conf / 2:
                config_rom[i].assign(init_state & 0xffff)
                init_state = init_state >> std_comm_width
            else:
                config_rom[i].assign(end_state & 0xffff)
                end_state = end_state >> std_comm_width
        tb.EmbeddedCode('\n//Configuraton Memory section - End')

        tb.EmbeddedCode('\n//PE test Control - Begin')

        config_counter = tb.Reg('config_counter', ceil(log2(qtde_conf))+1)

        tb.Always(Posedge(tb_clk))(
            If(tb_rst)(
                config_counter(0),
                tb_config_input_done(0),
            ).Else(
                    If(config_counter == qtde_conf)(
                        tb_config_input_done(1),
                        pe_config_input_valid(0),
                    ).Else(
                        config_counter.inc(),
                        pe_config_input_valid(1),
                        pe_config_input(config_rom[config_counter])
                    )
            )
        )
        tb.EmbeddedCode('\n//PE test Control - End')

        tb.EmbeddedCode('\n//Simulation sector - Begin')
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
            If(pe_done)(
                # Display('ACC DONE!'),
                Finish()
            )
        )

        tb.EmbeddedCode('\n//Simulation sector - End')
        tb.to_verilog("../test_benches/pe_test_bench.v")
        sim = simulation.Simulator(tb, sim='iverilog')
        rslt = sim.run()


test_benches = TestBenches()
#test_benches.create_pe_test_bench('../Benchmarks/B_bronchiseptica.txt')
test_benches.create_pe_test_bench('../Benchmarks/Benchmark_5.txt')
# test_benches.create_histogram_memory_test_bench()
# test_benches.create_grn_test_bench('../Benchmarks/Benchmark_5.txt')
# test_benches.create_xor_bit_counter_3b_test_bench()
