from builtins import len

from apt_pkg import init
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

    def create_pe_test_bench_hw(self, benchmark, hist_mem_bit_depth, init_state=0, end_state=31):
        functions = sorted(readGRN(benchmark))
        nodes, treated_functions = treat_functions(functions)
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
        pe_output_data_read = tb.Reg('pe_output_data_read')
        pe_output_data_valid = tb.Wire('pe_output_data_valid')
        pe_output_data_sum = tb.Wire('pe_output_data_sum', std_comm_width)
        pe_output_data_qty = tb.Wire('pe_output_data_qty', std_comm_width)
        tb.EmbeddedCode('//Data Transfer Signals - End')

        pe_done = tb.Wire('pe_done')

        tb.EmbeddedCode('\n')
        bits_grn = len(nodes)
        qty_conf = ceil(bits_grn / std_comm_width) * 2
        config_counter = tb.Reg('config_counter', ceil(log2(qty_conf)) + 1)
        config_rom = tb.Wire('config_rom', std_comm_width, qty_conf)

        tb.EmbeddedCode('\n//Configuraton Memory section - Begin')

        for i in range(qty_conf):
            if i < qty_conf / 2:
                config_rom[i].assign(init_state & 0xffff)
                init_state = init_state >> std_comm_width
            else:
                config_rom[i].assign(end_state & 0xffff)
                end_state = end_state >> std_comm_width
        tb.EmbeddedCode('\n//Configuraton Memory section - End')

        tb.EmbeddedCode('\n//PE test Control - Begin')
        tb.Always(Posedge(tb_clk))(
            If(tb_rst)(
                config_counter(0),
                tb_config_input_done(0),
            ).Else(
                If(config_counter == qty_conf)(
                    tb_config_input_done(1),
                    pe_config_input_valid(0),
                ).Else(
                    config_counter.inc(),
                    pe_config_input_valid(1),
                    pe_config_input(config_rom[config_counter])
                )
            )
        )

        rd_flag = tb.Reg('rd_flag')
        fsm_rd_data = tb.Reg('fsm_rd_data', 1)
        fsm_rd_data_idle = tb.Localparam('fsm_rd_data_idle', 0)
        fsm_rd_data_read = tb.Localparam('fsm_rd_data_read', 1)

        tb.Always(Posedge(tb_clk))(
            If(tb_rst)(
                pe_output_data_read(0),
                fsm_rd_data(fsm_rd_data_idle),
                rd_flag(0)
            ).Else(
                pe_output_data_read(1),
                If(pe_output_data_valid)(
                    Display('Pos -: sum %d qty %d', pe_output_data_sum, pe_output_data_qty)
                ),
            )
        )
        tb.EmbeddedCode('\n//PE test Control - End')

        params = []
        con = [('clk', tb_clk),
               ('rst', tb_rst),
               ('config_input_done', tb_config_input_done),
               ('config_input_valid', pe_config_input_valid),
               ('config_input', pe_config_input),
               ('config_output', pe_config_output),
               ('output_data_read', pe_output_data_read),
               ('output_data_valid', pe_output_data_valid),
               ('output_data_sum', pe_output_data_sum),
               ('output_data_qty', pe_output_data_qty),
               ('done', pe_done)
               ]
        hist_mem_bit_depth = len(nodes) if hist_mem_bit_depth > len(nodes) else hist_mem_bit_depth
        pe = self.components.create_pe(nodes, treated_functions, hist_mem_bit_depth, std_comm_width)
        tb.Instance(pe, pe.name, params, con)

        tb.EmbeddedCode('\n//Simulation sector - Begin')
        initialize_regs(tb, {'tb_clk': 0, 'tb_rst': 1})

        simulation.setup_waveform(tb)

        tb.Initial(
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            tb_rst(0),
            # Delay(100000), Finish()
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
        print(rslt)

    def create_pe_test_bench_cpu(self, benchmark, init_state=0, end_state=31):

        functions = sorted(readGRN(benchmark))
        nodes, treated_functions = treat_functions(functions)

        sum = [0 for i in range(int(pow(2, len(nodes))))]
        qty = [0 for i in range(int(pow(2, len(nodes))))]

        nodes_a = {node: False for node in nodes}
        nodes_b = {node: False for node in nodes}
        nodes_al = {node: False for node in nodes}
        nodes_bl = {node: False for node in nodes}

        functions_a = [function for function in functions]
        for i in range(len(functions_a)):
            for node in nodes:
                functions_a[i] = functions_a[i].strip().replace(node, 'nodes_a["' + node + '"]')
            aux = functions_a[i].split('=')
            functions_a[i] = aux[0].replace('nodes_a', 'nodes_al') + ' = ' + aux[1]

        functions_b = [function for function in functions]
        for i in range(len(functions_b)):
            for node in nodes:
                functions_b[i] = functions_b[i].strip().replace(node, 'nodes_b["' + node + '"]')
            aux = functions_b[i].split('=')
            functions_b[i] = aux[0].replace('nodes_b', 'nodes_bl') + ' = ' + aux[1]

        while init_state <= end_state:
            counter = init_state + 1 if init_state + 1 <= end_state else 0
            init_state_a = init_state

            for node in nodes_a:
                nodes_a[node] = True if (init_state_a & 0x1 == 1) else False
                init_state_a = init_state_a >> 1

            for f in functions_a:
                exec(f, globals(), locals())

            while counter != init_state:
                init_state_b = counter
                for node in nodes_b:
                    nodes_b[node] = True if (init_state_b & 0x1 == 1) else False
                    init_state_b = init_state_b >> 1

                for f in functions_b:
                    exec(f)

                diff_a_b = 0
                diff_al_bl = 0

                for node in nodes_a:
                    diff_a_b = diff_a_b + 1 if nodes_a[node] != nodes_b[node] else diff_a_b
                    diff_al_bl = diff_al_bl + 1 if nodes_al[node] != nodes_bl[node] else diff_al_bl
                sum[diff_a_b] = sum[diff_a_b] + diff_al_bl
                qty[diff_a_b] = qty[diff_a_b] + 1
                counter = counter + 1 if counter + 1 <= end_state else 0
            init_state = init_state + 1

        print('PE_ test_bench_results_CPU')
        for i in range(len(sum)):
            print('Pos ' + str(i) + ': sum ' + str(sum[i]) + ' qty ' + str(qty[i]))


test_benches = TestBenches()
test_benches.create_pe_test_bench_hw('../Benchmarks/Benchmark_5.txt', 5)
test_benches.create_pe_test_bench_cpu('../Benchmarks/Benchmark_5.txt')
# test_benches.create_pe_test_bench('../Benchmarks/B_bronchiseptica.txt',10)
# test_benches.create_histogram_memory_test_bench()
# test_benches.create_grn_test_bench('../Benchmarks/Benchmark_5.txt')
# test_benches.create_xor_bit_counter_3b_test_bench()
