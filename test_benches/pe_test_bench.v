

module test_bench
(

);


  //Standar I/O signals - Begin
  reg tb_clk;
  reg tb_rst;
  //Standar I/O signals - End

  //Configuration Signals - Begin
  reg tb_config_input_done;
  reg pe_config_input_valid;
  reg [32-1:0] pe_config_input;
  wire [32-1:0] pe_config_output;
  //Configuration Signals - End

  //Data Transfer Signals - Begin
  reg pe_output_data_read;
  wire pe_output_data_valid;
  wire [32-1:0] pe_output_data_sum;
  wire [32-1:0] pe_output_data_qty;
  //Data Transfer Signals - End
  wire pe_done;


  reg [2-1:0] config_counter;
  wire [32-1:0] config_rom [0:2-1];

  //Configuraton Memory section - Begin
  assign config_rom[0] = 0;
  assign config_rom[1] = 31;

  //Configuraton Memory section - End

  //PE test Control - Begin

  always @(posedge tb_clk) begin
    if(tb_rst) begin
      config_counter <= 0;
      tb_config_input_done <= 0;
    end else begin
      if(config_counter == 2) begin
        tb_config_input_done <= 1;
        pe_config_input_valid <= 0;
      end else begin
        config_counter <= config_counter + 1;
        pe_config_input_valid <= 1;
        pe_config_input <= config_rom[config_counter];
      end
    end
  end

  reg rd_flag;
  reg [1-1:0] fsm_rd_data;
  localparam fsm_rd_data_idle = 0;
  localparam fsm_rd_data_read = 1;

  always @(posedge tb_clk) begin
    if(tb_rst) begin
      pe_output_data_read <= 0;
      fsm_rd_data <= fsm_rd_data_idle;
      rd_flag <= 0;
    end else begin
      pe_output_data_read <= 1;
      if(pe_output_data_valid) begin
        $display("Pos -: sum %d qty %d", pe_output_data_sum, pe_output_data_qty);
      end 
    end
  end


  //PE test Control - End

  pe
  pe
  (
    .clk(tb_clk),
    .rst(tb_rst),
    .config_input_done(tb_config_input_done),
    .config_input_valid(pe_config_input_valid),
    .config_input(pe_config_input),
    .config_output(pe_config_output),
    .output_data_read(pe_output_data_read),
    .output_data_valid(pe_output_data_valid),
    .output_data_sum(pe_output_data_sum),
    .output_data_qty(pe_output_data_qty),
    .done(pe_done)
  );


  //Simulation sector - Begin

  initial begin
    tb_clk = 0;
    tb_rst = 1;
    tb_config_input_done = 0;
    pe_config_input_valid = 0;
    pe_config_input = 0;
    pe_output_data_read = 0;
    config_counter = 0;
    rd_flag = 0;
    fsm_rd_data = 0;
  end


  initial begin
    $dumpfile("uut.vcd");
    $dumpvars(0);
  end


  initial begin
    @(posedge tb_clk);
    @(posedge tb_clk);
    @(posedge tb_clk);
    tb_rst = 0;
  end

  always #5tb_clk=~tb_clk;

  always @(posedge tb_clk) begin
    if(pe_done) begin
      $finish;
    end 
  end


  //Simulation sector - End

endmodule



module pe
(
  input clk,
  input rst,
  input config_input_done,
  input config_input_valid,
  input [32-1:0] config_input,
  output reg [32-1:0] config_output,
  input output_data_read,
  output reg output_data_valid,
  output reg [32-1:0] output_data_sum,
  output reg [32-1:0] output_data_qty,
  output reg done
);


  //configuration wires and regs - begin
  reg [32-1:0] pe_init_conf;
  reg [32-1:0] pe_end_conf;
  wire [32-1:0] config_forward;
  wire [32-1:0] config_output_forward;
  //configuration wires and regs - end

  //grn instantiation module wires and regs - begin
  reg [2-1:0] grn_input_data_valid;
  reg [5-1:0] grn_input_data;
  wire [2-1:0] grn_output_data_valid;
  wire [5-1:0] grn_output_data;
  //grn instantiation module wires and regs - end

  //Internal loop control wires and regs - begin
  reg last_loop;
  reg [5-1:0] ctrl_hm_rd_add;
  reg [5-1:0] b_r;
  reg [5-1:0] b_r_next;
  reg [5-1:0] al_r;
  reg [5-1:0] bl_r;
  reg bl_r_v;
  reg flag_first_iteration;
  reg [5-1:0] fsm_process;
  localparam fsm_process_init = 0;
  localparam fsm_process_loop = 1;
  localparam fsm_process_wait_pipeline = 2;
  localparam fsm_process_discharge = 3;
  localparam fsm_process_verify = 4;
  localparam fsm_process_done = 5;
  //Internal loop control wires and regs - end

  //xor bit counters instantiation wires and regs - begin
  wire [2-1:0] xbc3_add_output_data_valid;
  wire [2-1:0] xbc3_add_output_data [0:2-1];
  wire [2-1:0] xbc3_data_output_data_valid;
  wire [2-1:0] xbc3_data_output_data [0:2-1];
  //xor bit counters instantiation wires and regs - end

  //Histogram memory instantiation wires and regs - begin
  wire [32-1:0] hm_rd_data;
  wire [32-1:0] hm_rd_qty;
  wire hm_rdy;
  wire [5-1:0] hm_rd_add;
  reg hm_rd_add_selector;
  //Histogram memory instantiation wires and regs - end

  //sum loops for address and data lines wires and regs - begin
  reg [5-1:0] sum_add [0:1-1];
  reg [5-1:0] reg_add [0:1-1];
  reg [2-1:0] reg_add_valid_pipe;
  wire [5-1:0] wr_address;
  wire wr;
  reg [5-1:0] sum_data [0:1-1];
  reg [5-1:0] reg_data [0:0-1];
  reg [1-1:0] reg_data_valid_pipe;
  wire [32-1:0] wr_data;
  wire wr_data_valid;
  //sum loops for address and data lines wires and regs - end

  //configuration sector - begin
  assign config_forward = pe_end_conf;
  assign config_output_forward = pe_init_conf;

  always @(posedge clk) begin
    if(config_input_valid) begin
      pe_end_conf <= config_input;
      pe_init_conf <= config_forward;
      config_output <= config_output_forward;
    end 
  end

  //configuration sector - end

  //Internal loop control - begin

  always @(posedge clk) begin
    if(grn_output_data_valid[1]) begin
      al_r <= grn_output_data;
    end 
    if(grn_output_data_valid[0]) begin
      bl_r <= grn_output_data;
      bl_r_v <= 1;
    end else begin
      bl_r_v <= 0;
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      fsm_process <= fsm_process_init;
      grn_input_data_valid <= 0;
      last_loop <= 0;
      done <= 0;
    end else begin
      if(config_input_done && hm_rdy) begin
        case(fsm_process)
          fsm_process_init: begin
            b_r <= pe_init_conf[4:0];
            grn_input_data_valid <= 2;
            b_r_next <= pe_init_conf[4:0] + 1;
            flag_first_iteration <= 1;
            fsm_process <= fsm_process_loop;
            hm_rd_add_selector <= 0;
          end
          fsm_process_loop: begin
            grn_input_data <= b_r;
            b_r <= b_r + 1;
            b_r_next <= b_r_next + 1;
            grn_input_data_valid <= 1;
            if(b_r_next == pe_init_conf[4:0]) begin
              grn_input_data_valid <= 0;
              pe_init_conf <= pe_init_conf[4:0] + 1;
              fsm_process <= fsm_process_verify;
            end 
          end
          fsm_process_verify: begin
            fsm_process <= fsm_process_init;
            if(pe_init_conf[4:0] == pe_end_conf[4:0]) begin
              last_loop <= 1;
            end else if(last_loop) begin
              fsm_process <= fsm_process_wait_pipeline;
            end 
          end
          fsm_process_wait_pipeline: begin
            if(~wr) begin
              fsm_process <= fsm_process_discharge;
              hm_rd_add_selector <= 1;
              ctrl_hm_rd_add <= 0;
            end 
          end
          fsm_process_discharge: begin
            output_data_valid <= 0;
            if(&ctrl_hm_rd_add) begin
              output_data_valid <= 0;
              fsm_process <= fsm_process_done;
            end else if(output_data_read) begin
              ctrl_hm_rd_add <= ctrl_hm_rd_add + 1;
              output_data_valid <= 1;
              output_data_sum <= hm_rd_data;
              output_data_qty <= hm_rd_qty;
            end 
          end
          fsm_process_done: begin
            done <= 1;
          end
        endcase
      end 
    end
  end

  //Internal loop control - end

  //sum loop for address line sector - begin
  assign wr_address = reg_add[0];
  assign wr = reg_add_valid_pipe[1];

  always @(posedge clk) begin
    sum_add[0] <= xbc3_add_output_data[0] + xbc3_add_output_data[1];
    reg_add[0] <= sum_add[0];
  end


  always @(posedge clk) begin
    reg_add_valid_pipe[0] <= xbc3_add_output_data_valid[0];
    reg_add_valid_pipe[1] <= reg_add_valid_pipe[0];

  end

  //sum loop for address line sector - end

  //sum loop for data line sector - begin
  assign wr_data = sum_data[0];
  assign wr_data_valid = reg_data_valid_pipe[0];

  always @(posedge clk) begin
    sum_data[0] <= xbc3_data_output_data[0] + xbc3_data_output_data[1];

  end


  always @(posedge clk) begin
    reg_data_valid_pipe[0] <= xbc3_data_output_data_valid[0];

  end

  //sum loop for data line sector - end

  //grn module instantiation sector - begin

  grn
  grn
  (
    .clk(clk),
    .input_data_valid(grn_input_data_valid),
    .input_data(b_r),
    .output_data_valid(grn_output_data_valid),
    .output_data(grn_output_data)
  );

  //grn module instantiation sector - end

  //xor bit counters instantiation sector - begin

  xor_bit_counter_3b
  xor_bit_counter_3b_add_0
  (
    .clk(clk),
    .input_data_valid(grn_input_data_valid[0]),
    .input_data({ pe_init_conf[2:0], b_r[2:0] }),
    .output_data_valid(xbc3_add_output_data_valid[0]),
    .output_data(xbc3_add_output_data[0])
  );


  xor_bit_counter_3b
  xor_bit_counter_3b_add_1
  (
    .clk(clk),
    .input_data_valid(grn_input_data_valid[0]),
    .input_data({ { 1'd0, pe_init_conf[4:3] }, { 1'd0, b_r[4:3] } }),
    .output_data_valid(xbc3_add_output_data_valid[1]),
    .output_data(xbc3_add_output_data[1])
  );


  xor_bit_counter_3b
  xor_bit_counter_3b_data_0
  (
    .clk(clk),
    .input_data_valid(grn_output_data_valid[0]),
    .input_data({ al_r[2:0], grn_output_data[2:0] }),
    .output_data_valid(xbc3_data_output_data_valid[0]),
    .output_data(xbc3_data_output_data[0])
  );


  xor_bit_counter_3b
  xor_bit_counter_3b_data_1
  (
    .clk(clk),
    .input_data_valid(grn_output_data_valid[0]),
    .input_data({ { 1'd0, al_r[4:3] }, { 1'd0, grn_output_data[4:3] } }),
    .output_data_valid(xbc3_data_output_data_valid[1]),
    .output_data(xbc3_data_output_data[1])
  );

  //xor bit counters instantiation sector - end

  //histogram memory sector - Begin
  assign hm_rd_add = (hm_rd_add_selector)? ctrl_hm_rd_add : wr_address;

  histogram_memory
  histogram_memory
  (
    .clk(clk),
    .rst(rst),
    .rd_add(hm_rd_add),
    .wr(wr),
    .wr_add(wr_address),
    .wr_data(wr_data),
    .rd_data(hm_rd_data),
    .rd_qty(hm_rd_qty),
    .rdy(hm_rdy)
  );

  //histogram memory sector - Begin

  //simulation sector - begin
  integer i_initial;

  initial begin
    config_output = 0;
    output_data_valid = 0;
    output_data_sum = 0;
    output_data_qty = 0;
    done = 0;
    pe_init_conf = 0;
    pe_end_conf = 0;
    grn_input_data_valid = 0;
    grn_input_data = 0;
    last_loop = 0;
    ctrl_hm_rd_add = 0;
    b_r = 0;
    b_r_next = 0;
    al_r = 0;
    bl_r = 0;
    bl_r_v = 0;
    flag_first_iteration = 0;
    fsm_process = 0;
    hm_rd_add_selector = 0;
    for(i_initial=0; i_initial<1; i_initial=i_initial+1) begin
      sum_add[i_initial] = 0;
    end
    for(i_initial=0; i_initial<1; i_initial=i_initial+1) begin
      reg_add[i_initial] = 0;
    end
    reg_add_valid_pipe = 0;
    for(i_initial=0; i_initial<1; i_initial=i_initial+1) begin
      sum_data[i_initial] = 0;
    end
    for(i_initial=0; i_initial<0; i_initial=i_initial+1) begin
      reg_data[i_initial] = 0;
    end
    reg_data_valid_pipe = 0;
  end

  //simulation sector - begin

endmodule



module grn
(
  input clk,
  input [2-1:0] input_data_valid,
  input [5-1:0] input_data,
  output reg [2-1:0] output_data_valid,
  output [5-1:0] output_data
);

  reg ccrm_r;
  reg ctra_r;
  reg dnaa_r;
  reg gcra_r;
  reg scip_r;
  wire ccrm;
  wire ctra;
  wire dnaa;
  wire gcra;
  wire scip;

  always @(posedge clk) begin
    output_data_valid <= input_data_valid;
    ccrm_r <=  ctra & (~ccrm ) & (~scip ) ;
    ctra_r <=  ( ctra | gcra ) & (~ccrm ) & (~scip ) ;
    dnaa_r <=  ctra & ccrm & (~gcra ) & (~dnaa ) ;
    gcra_r <=  dnaa &~ctra ;
    scip_r <=  ctra &~dnaa ;
  end

  assign ccrm = input_data[0];
  assign ctra = input_data[1];
  assign dnaa = input_data[2];
  assign gcra = input_data[3];
  assign scip = input_data[4];
  assign output_data[0] = ccrm_r;
  assign output_data[1] = ctra_r;
  assign output_data[2] = dnaa_r;
  assign output_data[3] = gcra_r;
  assign output_data[4] = scip_r;

  initial begin
    output_data_valid = 0;
    ccrm_r = 0;
    ctra_r = 0;
    dnaa_r = 0;
    gcra_r = 0;
    scip_r = 0;
  end


endmodule



module xor_bit_counter_3b
(
  input clk,
  input input_data_valid,
  input [6-1:0] input_data,
  output reg output_data_valid,
  output reg [2-1:0] output_data
);

  wire [2-1:0] xor_bit_counter_rom [0:64-1];

  always @(posedge clk) begin
    output_data_valid <= input_data_valid;
    output_data <= xor_bit_counter_rom[input_data];
  end

  assign xor_bit_counter_rom[0] = 2'b0;
  assign xor_bit_counter_rom[1] = 2'b1;
  assign xor_bit_counter_rom[2] = 2'b1;
  assign xor_bit_counter_rom[3] = 2'b10;
  assign xor_bit_counter_rom[4] = 2'b1;
  assign xor_bit_counter_rom[5] = 2'b10;
  assign xor_bit_counter_rom[6] = 2'b10;
  assign xor_bit_counter_rom[7] = 2'b11;
  assign xor_bit_counter_rom[8] = 2'b1;
  assign xor_bit_counter_rom[9] = 2'b0;
  assign xor_bit_counter_rom[10] = 2'b10;
  assign xor_bit_counter_rom[11] = 2'b1;
  assign xor_bit_counter_rom[12] = 2'b10;
  assign xor_bit_counter_rom[13] = 2'b1;
  assign xor_bit_counter_rom[14] = 2'b11;
  assign xor_bit_counter_rom[15] = 2'b10;
  assign xor_bit_counter_rom[16] = 2'b1;
  assign xor_bit_counter_rom[17] = 2'b10;
  assign xor_bit_counter_rom[18] = 2'b0;
  assign xor_bit_counter_rom[19] = 2'b1;
  assign xor_bit_counter_rom[20] = 2'b10;
  assign xor_bit_counter_rom[21] = 2'b11;
  assign xor_bit_counter_rom[22] = 2'b1;
  assign xor_bit_counter_rom[23] = 2'b10;
  assign xor_bit_counter_rom[24] = 2'b10;
  assign xor_bit_counter_rom[25] = 2'b1;
  assign xor_bit_counter_rom[26] = 2'b1;
  assign xor_bit_counter_rom[27] = 2'b0;
  assign xor_bit_counter_rom[28] = 2'b11;
  assign xor_bit_counter_rom[29] = 2'b10;
  assign xor_bit_counter_rom[30] = 2'b10;
  assign xor_bit_counter_rom[31] = 2'b1;
  assign xor_bit_counter_rom[32] = 2'b1;
  assign xor_bit_counter_rom[33] = 2'b10;
  assign xor_bit_counter_rom[34] = 2'b10;
  assign xor_bit_counter_rom[35] = 2'b11;
  assign xor_bit_counter_rom[36] = 2'b0;
  assign xor_bit_counter_rom[37] = 2'b1;
  assign xor_bit_counter_rom[38] = 2'b1;
  assign xor_bit_counter_rom[39] = 2'b10;
  assign xor_bit_counter_rom[40] = 2'b10;
  assign xor_bit_counter_rom[41] = 2'b1;
  assign xor_bit_counter_rom[42] = 2'b11;
  assign xor_bit_counter_rom[43] = 2'b10;
  assign xor_bit_counter_rom[44] = 2'b1;
  assign xor_bit_counter_rom[45] = 2'b0;
  assign xor_bit_counter_rom[46] = 2'b10;
  assign xor_bit_counter_rom[47] = 2'b1;
  assign xor_bit_counter_rom[48] = 2'b10;
  assign xor_bit_counter_rom[49] = 2'b11;
  assign xor_bit_counter_rom[50] = 2'b1;
  assign xor_bit_counter_rom[51] = 2'b10;
  assign xor_bit_counter_rom[52] = 2'b1;
  assign xor_bit_counter_rom[53] = 2'b10;
  assign xor_bit_counter_rom[54] = 2'b0;
  assign xor_bit_counter_rom[55] = 2'b1;
  assign xor_bit_counter_rom[56] = 2'b11;
  assign xor_bit_counter_rom[57] = 2'b10;
  assign xor_bit_counter_rom[58] = 2'b10;
  assign xor_bit_counter_rom[59] = 2'b1;
  assign xor_bit_counter_rom[60] = 2'b10;
  assign xor_bit_counter_rom[61] = 2'b1;
  assign xor_bit_counter_rom[62] = 2'b1;
  assign xor_bit_counter_rom[63] = 2'b0;

  initial begin
    output_data_valid = 0;
    output_data = 0;
  end


endmodule



module histogram_memory
(
  input clk,
  input rst,
  input [5-1:0] rd_add,
  input wr,
  input [5-1:0] wr_add,
  input [32-1:0] wr_data,
  output [32-1:0] rd_data,
  output [32-1:0] rd_qty,
  output reg rdy
);

  reg [5-1:0] rst_counter;
  reg flag_rst;
  reg [32-1:0] valid;
  reg [32-1:0] sum_m [0:32-1];
  reg [32-1:0] qty_m [0:32-1];
  wire [32-1:0] wr_sum;
  wire [32-1:0] wr_qty;
  assign rd_data = (valid[rd_add])? sum_m[rd_add] : 0;
  assign rd_qty = (valid[rd_add])? qty_m[rd_add] : 0;
  assign wr_sum = wr_data + rd_data;
  assign wr_qty = rd_qty + 1;

  always @(posedge clk) begin
    if(rst) begin
      rdy <= 0;
      flag_rst <= 1;
      rst_counter <= 0;
    end else begin
      if(flag_rst) begin
        if(&rst_counter) begin
          rdy <= 1;
          flag_rst <= 0;
        end else begin
          valid[rst_counter] <= 0;
          qty_m[rst_counter] <= 0;
          rst_counter <= rst_counter + 1;
        end
      end else begin
        if(wr) begin
          sum_m[wr_add] <= wr_sum;
          qty_m[wr_add] <= wr_qty;
          valid[wr_add] <= 1;
        end 
      end
    end
  end

  integer i_initial;

  initial begin
    rdy = 0;
    rst_counter = 0;
    flag_rst = 0;
    valid = 0;
    for(i_initial=0; i_initial<32; i_initial=i_initial+1) begin
      sum_m[i_initial] = 0;
    end
    for(i_initial=0; i_initial<32; i_initial=i_initial+1) begin
      qty_m[i_initial] = 0;
    end
  end


endmodule

