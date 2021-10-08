from builtins import len
from veriloggen import *

from src.derrida_accelerator import GrnDerridaPlotAccelerator
from math import pow, ceil, log2, floor

from src.utils import initialize_regs

p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if not p in sys.path:
    sys.path.insert(0, p)


class TestBenches:

    def __init__(self, grn_arch_file, copies_qty=1, std_comm_width=32):
        self.grn_arch_file = grn_arch_file
        self.std_comm_width = std_comm_width
        self.drdp = GrnDerridaPlotAccelerator(grn_arch_file, copies_qty, std_comm_width)

    def create_grn_derrida_plot_test_bench_hw(self):
        # TEST BENCH MODULE --------------------------------------------------------------------------------------------
        tb = Module('test_bench')

        tb.EmbeddedCode('\n//Standar I/O signals - Begin')
        tb_clk = tb.Reg('tb_clk')
        tb_rst = tb.Reg('tb_rst')
        tb_start_reg = tb.Reg('tb_start_reg')
        tb.EmbeddedCode('//Standar I/O signals - End')

        # derrida plot accelerator instantiation regs and wires - Begin ------------------------------------------------
        tb.EmbeddedCode('\n//derrida plot accelerator instantiation regs and wires - end')
        drdp_acc_user_done_rd_data = tb.Reg('drdp_acc_user_done_rd_data', self.drdp.get_num_in())
        drdp_acc_user_done_wr_data = tb.Reg('drdp_acc_user_done_wr_data', self.drdp.get_num_out())
        drdp_acc_user_request_read = tb.Wire('drdp_acc_user_request_read', self.drdp.get_num_in())
        drdp_acc_user_read_data_valid = tb.Reg('drdp_acc_user_read_data_valid', self.drdp.get_num_in())
        drdp_acc_user_read_data = tb.Reg('drdp_acc_user_read_data', self.std_comm_width * self.drdp.get_num_in())
        drdp_acc_user_available_write = tb.Reg('drdp_acc_user_available_write', self.drdp.get_num_out())
        drdp_acc_user_request_write = tb.Wire('drdp_acc_user_request_write', self.drdp.get_num_out())
        drdp_acc_user_write_data = tb.Wire('drdp_acc_user_write_data', self.std_comm_width * self.drdp.get_num_out())
        drdp_acc_user_done = tb.Wire('drdp_acc_user_done')
        tb.EmbeddedCode('//derrida plot accelerator instantiation regs and wires - end')
        # derrida plot accelerator instantiation regs and wires - end --------------------------------------------------

        # Config Rom configuration regs and wires - Begin --------------------------------------------------------------
        tb.EmbeddedCode('\n//Config Rom configuration regs and wires - Begin')
        bits_grn = self.drdp.nodes_qty
        qty_conf = ceil(bits_grn / self.drdp.std_comm_width) * 2 * self.drdp.copies_qty
        step = floor(pow(2, bits_grn)) // self.drdp.copies_qty
        configs = []
        for i in range(self.drdp.copies_qty):
            configs.append(i * step)
            configs.append((i * step) + step - 1)
        configs[len(configs) - 1] = ceil(pow(2, bits_grn)) - 1
        config_counter = tb.Reg('config_counter', ceil(log2(qty_conf)) + 1)
        config_rom = tb.Wire('config_rom', self.drdp.std_comm_width, qty_conf)
        tb.EmbeddedCode('//Config Rom configuration regs and wires - End')
        # Config Rom configuration regs and wires - End ----------------------------------------------------------------

        # Data Producer regs and wires - Begin -------------------------------------------------------------------------
        tb.EmbeddedCode('\n//Data Producer regs and wires - Begin')
        fsm_produce_data = tb.Reg('fsm_produce_data', 2)
        fsm_init = tb.Localparam('fsm_init', 0)
        fsm_produce = tb.Localparam('fsm_produce', 1)
        fsm_done = tb.Localparam('fsm_done', 2)
        tb.EmbeddedCode('\n//Data Producer regs and wires - End')
        # Data Producer regs and wires - End ---------------------------------------------------------------------------

        # Data Producer - Begin ----------------------------------------------------------------------------------------
        tb.EmbeddedCode('\n//Data Producer - Begin')
        tb.Always(Posedge(tb_clk))(
            If(tb_rst)(
                config_counter(0),
                drdp_acc_user_read_data_valid(0),
                drdp_acc_user_done_rd_data(0),
                fsm_produce_data(fsm_init),
            ).Else(
                Case(fsm_produce_data)(
                    When(fsm_init)(
                        fsm_produce_data(fsm_produce)
                    ),
                    When(fsm_produce)(
                        drdp_acc_user_read_data_valid(Int(1, 1, 10)),
                        drdp_acc_user_read_data(config_rom[config_counter]),
                        If(AndList(drdp_acc_user_request_read, drdp_acc_user_read_data_valid))(
                            config_counter(config_counter + 1),
                            drdp_acc_user_read_data_valid(Int(0, 1, 10)),
                        ),
                        If(config_counter == qty_conf)(
                            drdp_acc_user_read_data_valid(Int(0, 1, 10)),
                            fsm_produce_data(fsm_done)
                        )
                    ),
                    When(fsm_done)(
                        drdp_acc_user_done_rd_data(Int(1, 1, 10))
                    ),
                )
            )
        )
        tb.EmbeddedCode('//Data Producer - End')
        # Data Producer - End ------------------------------------------------------------------------------------------

        # Data Consumer - Begin ----------------------------------------------------------------------------------------
        tb.EmbeddedCode('\n//Data Consumer - Begin')
        tb.Always(Posedge(tb_clk))(
            If(tb_rst)(
                drdp_acc_user_available_write(0),
            ).Else(
                drdp_acc_user_available_write(1),
                If(drdp_acc_user_request_write)(
                    Display("%d", drdp_acc_user_write_data),
                    drdp_acc_user_available_write(0),
                )
            )
        )
        tb.EmbeddedCode('//Data Consumer - Begin')
        # Data Consumer - End ------------------------------------------------------------------------------------------

        # Config Rom configuration - Begin -----------------------------------------------------------------------------
        tb.EmbeddedCode('\n//Config Rom configuration - Begin')
        config_rom_counter = 0
        for conf in configs:
            for i in range(ceil(bits_grn / self.drdp.std_comm_width)):
                config_rom[config_rom_counter].assign(Int(conf & (self.drdp.std_comm_width - 1), config_rom.width, 10))
                conf = conf >> self.drdp.std_comm_width
                config_rom_counter = config_rom_counter + 1
        tb.EmbeddedCode('//Config Rom configuration - End')
        # Config Rom configuration - End -------------------------------------------------------------------------------

        # derrida plot accelerator instantiation - Begin -----------------------------------------------------------------
        par = []
        con = [
            ('clk', tb_clk),
            ('rst', tb_rst),
            ('start', tb_start_reg),
            ('acc_user_done_rd_data', drdp_acc_user_done_rd_data),
            ('acc_user_done_wr_data', drdp_acc_user_done_wr_data),
            ('acc_user_request_read', drdp_acc_user_request_read),
            ('acc_user_read_data_valid', drdp_acc_user_read_data_valid),
            ('acc_user_read_data', drdp_acc_user_read_data),
            ('acc_user_available_write', drdp_acc_user_available_write),
            ('acc_user_request_write', drdp_acc_user_request_write),
            ('acc_user_write_data', drdp_acc_user_write_data),
            ('acc_user_done', drdp_acc_user_done)
        ]
        drdp_acc = self.drdp.get()
        tb.Instance(drdp_acc, drdp_acc.name, par, con)
        # derrida plot accelerator instantiation - end -----------------------------------------------------------------

        initialize_regs(tb, {'tb_clk': 0, 'tb_rst': 1, 'tb_start_reg': 0})

        simulation.setup_waveform(tb)

        tb.Initial(
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            EmbeddedCode('@(posedge tb_clk);'),
            tb_rst(0),
            tb_start_reg(1),
            Delay(1000000), Finish()
        )
        tb.EmbeddedCode('always #5tb_clk=~tb_clk;')

        tb.Always(Posedge(tb_clk))(
            If(drdp_acc_user_done)(
                # Display('ACC DONE!'),
                Finish()
            )
        )

        tb.EmbeddedCode('\n//Simulation sector - End')
        tb.to_verilog('../test_benches/grn_derrida_plot_acc_test_bench_' + str(self.drdp.nodes_qty) + '_nodes_' + str(
            self.drdp.copies_qty) + '_copies_' + str(int(pow(2, bits_grn))) + '_states.v')
        sim = simulation.Simulator(tb, sim='iverilog')
        rslt = sim.run()
        print(rslt)

    def create_grn_derrida_plot_test_bench_cpu(self, init_state=0, end_state=31):

        functions = self.drdp.functions
        nodes = self.drdp.nodes
        treated_functions = self.drdp.treated_functions

        sum = [0 for i in range(len(nodes) + 1)]
        qty = [0 for i in range(len(nodes) + 1)]

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


test_benches = TestBenches('../Benchmarks/Benchmark_5.txt', 15, 32)
test_benches.create_grn_derrida_plot_test_bench_hw()
test_benches.create_grn_derrida_plot_test_bench_cpu(0, 31)
