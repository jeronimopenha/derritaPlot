from veriloggen import *

from src.hw.grn_derrida_plot_components import GrnDerridaPlotComponents
from src.hw.utils import initialize_regs


class GrnDerridaPlotAws:

    def get(self, nodes, functions, treated_functions, copies_qty=1, std_comm_width=32):
        self.nodes = nodes
        self.functions = functions
        self.treated_functions = treated_functions
        self.copies_qty = copies_qty
        self.std_comm_width = std_comm_width
        self.grdpComponents = GrnDerridaPlotComponents()
        return self.__create_derrita_aws()

    def __create_derrita_aws(self):
        if self.copies_qty < 1: raise ValueError("The copies value can't be lower than 1")
        name = 'derrita_aws_%d_PE' % self.copies_qty
        drdp_components = GrnDerridaPlotComponents()

        m = Module(name)

        # interface I/O interface - Begin ------------------------------------------------------------------------------
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        drdp_done_rd_data = m.Input('drdp_done_rd_data')
        drdp_done_wr_data = m.Input('drdp_done_wr_data')

        drdp_request_read = m.OutputReg('drdp_request_read')
        drdp_read_data_valid = m.Input('drdp_read_data_valid')
        drdp_read_data = m.Input('drdp_read_data', self.std_comm_width)

        drdp_available_write = m.Input('drdp_available_write')
        drdp_request_write = m.Output('drdp_request_write')
        drdp_write_data = m.Output('drdp_write_data', self.std_comm_width)

        drdp_done = m.Output('drdp_done')
        # interface I/O interface - End --------------------------------------------------------------------------------

        # Config wires and regs - Begin --------------------------------------------------------------------------------
        m.EmbeddedCode('\n//Config wires and regs - Begin')
        fsm_sd_idle = m.Localparam('fsm_sd_idle', 0, 2)
        fsm_sd_send_data = m.Localparam('fsm_sd_send_data', 1, 2)
        fsm_sd_done = m.Localparam('fsm_sd_done', 2, 2)
        fsm_sd = m.Reg('fms_cs', 2)
        config_valid = m.Reg('config_valid')
        config_data = m.Reg('config_data', self.std_comm_width)
        config_done = m.Reg('config_done')
        flag = m.Reg('flag')
        m.EmbeddedCode('//Config wires and regs - End')
        # Config wires and regs - End ----------------------------------------------------------------------------------

        # PEs instantiations wires and Regs - Begin --------------------------------------------------------------------
        m.EmbeddedCode('\n//PEs instantiations wires and Regs - Begin')
        pe_done = m.Wire('pe_done', self.copies_qty)
        pe_request_read = m.Wire('pe_request_read', self.copies_qty)
        pe_read_data_valid = m.Wire('pe_read_data_valid', self.copies_qty)
        pe_read_data = m.Wire('pe_read_data', self.std_comm_width, self.copies_qty)
        pe_config_output_done = m.Wire('pe_config_output_done', self.copies_qty)
        pe_config_output_valid = m.Wire('pe_config_output_valid', self.copies_qty)
        pe_config_output = m.Wire('pe_config_output', self.std_comm_width, self.copies_qty)
        m.EmbeddedCode('//PEs instantiations wires and Regs - End')
        # PEs instantiations wires and Regs - End ----------------------------------------------------------------------

        # Data Reading - Begin -----------------------------------------------------------------------------------------
        m.EmbeddedCode('\n//Data Reading - Begin')
        m.Always(Posedge(clk))(
            If(rst)(
                drdp_request_read(0),
                config_valid(0),
                fsm_sd(fsm_sd_idle),
                config_done(0),
                flag(0)
            ).Elif(start)(
                config_valid(0),
                drdp_request_read(0),
                flag(0),
                Case(fsm_sd)(
                    When(fsm_sd_idle)(
                        If(drdp_read_data_valid)(
                            drdp_request_read(1),
                            flag(1),
                            fsm_sd(fsm_sd_send_data)
                        ).Elif(drdp_done_rd_data)(
                            fsm_sd(fsm_sd_done)
                        )
                    ),
                    When(fsm_sd_send_data)(
                        If(drdp_read_data_valid | flag)(
                            config_data(drdp_read_data),
                            config_valid(1),
                            drdp_request_read(1),
                        ).Elif(drdp_done_rd_data)(
                            fsm_sd(fsm_sd_done)
                        ).Else(
                            fsm_sd(fsm_sd_idle)
                        )
                    ),
                    When(fsm_sd_done)(
                        config_done(1)
                    )
                )
            )
        )
        m.EmbeddedCode('//Data Reading - End')
        # Data Reading - End -------------------------------------------------------------------------------------------

        # PE modules instantiation - Begin -----------------------------------------------------------------------------
        m.EmbeddedCode('\n//PE modules instantiation - Begin')
        pe_read_data_valid[self.copies_qty - 1].assign(1)
        pe_read_data[self.copies_qty - 1].assign(0)
        drdp_done.assign(pe_done[0])
        for i in range(self.copies_qty):
            par = []
            con = [('clk', clk),
                   ('rst', rst),
                   ('done', pe_done[i]),
                   ('request_read', pe_request_read[i]),
                   ('read_data_valid', pe_read_data_valid[i]),
                   ('read_data', pe_read_data[i]),
                   ('config_output_valid', pe_config_output_valid[i]),
                   ('config_output', pe_config_output[i]),
                   ('config_output_done', pe_config_output_done[i]),
                   ]
            if i == 0:
                con.append(('request_write', drdp_request_write))
                con.append(('available_write', drdp_available_write))
                con.append(('write_data', drdp_write_data))
                con.append(('config_input_valid', config_valid))
                con.append(('config_input', config_data))
                con.append(('config_input_done', config_done))
            else:
                con.append(('request_write', pe_read_data_valid[i - 1]))
                con.append(('available_write', pe_request_read[i - 1]))
                con.append(('write_data', pe_read_data[i - 1]))
                con.append(('config_input_valid', pe_config_output_valid[i - 1]))
                con.append(('config_input', pe_config_output[i - 1]))
                con.append(('config_input_done', pe_config_output_done[i - 1]))
            pe = self.grdpComponents.create_pe(self.nodes, self.treated_functions, self.std_comm_width)
            m.Instance(pe, pe.name + '_' + str(i), par, con)
        m.EmbeddedCode('//PE modules instantiation - End')
        # PE modules instantiation - End -------------------------------------------------------------------------------

        # Simulation - Begin -------------------------------------------------------------------------------------------
        initialize_regs(m)
        # Simulation - End ---------------------------------------------------------------------------------------------
        return m
