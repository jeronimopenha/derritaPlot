import math
from veriloggen import *
from src.grn_derrida_plot_aws import GrnDerridaPlotAws
from src.utils import treat_functions, readGRN, initialize_regs


class GrnDerridaPlotAccelerator:
    def __init__(self, grn_arch_file, copies_qty=1, std_comm_width=32):
        # constants
        self.acc_num_in = 1
        self.acc_num_out = 1

        # needed variables
        self.grn_arch_file = grn_arch_file
        self.copies_qty = copies_qty
        self.std_comm_width = std_comm_width

        self.functions = sorted(readGRN(self.grn_arch_file))
        self.nodes_qty = len(self.functions)
        self.nodes, self.treated_functions = treat_functions(self.functions)

        self.acc_data_in_width = std_comm_width
        self.acc_data_out_width = std_comm_width
        self.axi_bus_data_width = int(math.pow(2, math.ceil(math.log2(self.acc_data_in_width))))

    def get_num_in(self):
        return self.acc_num_in

    def get_num_out(self):
        return self.acc_num_out

    def get(self):
        return self.__create_drdp_accelerator()

    def __create_drdp_accelerator(self):
        grn_drdp_aws = GrnDerridaPlotAws()

        m = Module('grn_derrida_plot_acc')
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        acc_user_done_rd_data = m.Input('acc_user_done_rd_data', self.acc_num_in)
        acc_user_done_wr_data = m.Input('acc_user_done_wr_data', self.acc_num_out)

        acc_user_request_read = m.Output('acc_user_request_read', self.acc_num_in)
        acc_user_read_data_valid = m.Input('acc_user_read_data_valid', self.acc_num_in)
        acc_user_read_data = m.Input('acc_user_read_data', self.axi_bus_data_width * self.acc_num_in)

        acc_user_available_write = m.Input('acc_user_available_write', self.acc_num_out)
        acc_user_request_write = m.Output('acc_user_request_write', self.acc_num_out)
        acc_user_write_data = m.Output('acc_user_write_data', self.axi_bus_data_width * self.acc_num_out)

        acc_user_done = m.Output('acc_user_done')

        start_reg = m.Reg('start_reg')
        drdp_done = m.Wire('drdp_done', self.get_num_in())

        acc_user_done.assign(drdp_done)

        m.Always(Posedge(clk))(
            If(rst)(
                start_reg(0)
            ).Else(
                start_reg(Or(start_reg, start))
            )
        )

        drdp = grn_drdp_aws.get(self.nodes, self.functions, self.treated_functions, self.copies_qty,
                                self.std_comm_width)
        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start_reg),
            ('drdp_done_rd_data', acc_user_done_rd_data),
            ('drdp_done_wr_data', acc_user_done_wr_data),
            ('drdp_request_read', acc_user_request_read),
            ('drdp_read_data_valid', acc_user_read_data_valid),
            ('drdp_read_data', acc_user_read_data),
            ('drdp_available_write', acc_user_available_write),
            ('drdp_request_write', acc_user_request_write),
            ('drdp_write_data', acc_user_write_data),
            ('drdp_done', drdp_done)]
        m.Instance(drdp, drdp.name, par, con)

        initialize_regs(m)

        return m
