

module test_bench
(

);


  //Standar I/O signals - Begin
  reg tb_clk;
  reg tb_rst;
  reg tb_start_reg;
  //Standar I/O signals - End

  //derrida plot accelerator instantiation regs and wires - end
  reg [1-1:0] drdp_acc_user_done_rd_data;
  reg [1-1:0] drdp_acc_user_done_wr_data;
  wire [1-1:0] drdp_acc_user_request_read;
  reg [1-1:0] drdp_acc_user_read_data_valid;
  reg [32-1:0] drdp_acc_user_read_data;
  reg [1-1:0] drdp_acc_user_available_write;
  wire [1-1:0] drdp_acc_user_request_write;
  wire [32-1:0] drdp_acc_user_write_data;
  wire drdp_acc_user_done;
  //derrida plot accelerator instantiation regs and wires - end

  //Config Rom configuration regs and wires - Begin
  reg [6-1:0] config_counter;
  wire [32-1:0] config_rom [0:18-1];
  //Config Rom configuration regs and wires - End

  //Data Producer regs and wires - Begin
  reg [2-1:0] fsm_produce_data;
  localparam fsm_init = 0;
  localparam fsm_produce = 1;
  localparam fsm_done = 2;

  //Data Producer regs and wires - End

  //Data Producer - Begin

  always @(posedge tb_clk) begin
    if(tb_rst) begin
      config_counter <= 0;
      drdp_acc_user_read_data_valid <= 0;
      drdp_acc_user_done_rd_data <= 0;
      fsm_produce_data <= fsm_init;
    end else begin
      case(fsm_produce_data)
        fsm_init: begin
          fsm_produce_data <= fsm_produce;
        end
        fsm_produce: begin
          drdp_acc_user_read_data_valid <= 1'd1;
          drdp_acc_user_read_data <= config_rom[config_counter];
          if(drdp_acc_user_request_read && drdp_acc_user_read_data_valid) begin
            config_counter <= config_counter + 1;
            drdp_acc_user_read_data_valid <= 1'd0;
          end 
          if(config_counter == 18) begin
            drdp_acc_user_read_data_valid <= 1'd0;
            fsm_produce_data <= fsm_done;
          end 
        end
        fsm_done: begin
          drdp_acc_user_done_rd_data <= 1'd1;
        end
      endcase
    end
  end

  //Data Producer - End

  //Data Consumer - Begin

  always @(posedge tb_clk) begin
    if(tb_rst) begin
      drdp_acc_user_available_write <= 0;
    end else begin
      drdp_acc_user_available_write <= 1;
      if(drdp_acc_user_request_write) begin
        $display("%d", drdp_acc_user_write_data);
        drdp_acc_user_available_write <= 0;
      end 
    end
  end

  //Data Consumer - Begin

  //Config Rom configuration - Begin
  assign config_rom[0] = 32'd0;
  assign config_rom[1] = 32'd2;
  assign config_rom[2] = 32'd3;
  assign config_rom[3] = 32'd5;
  assign config_rom[4] = 32'd6;
  assign config_rom[5] = 32'd8;
  assign config_rom[6] = 32'd9;
  assign config_rom[7] = 32'd11;
  assign config_rom[8] = 32'd12;
  assign config_rom[9] = 32'd14;
  assign config_rom[10] = 32'd15;
  assign config_rom[11] = 32'd17;
  assign config_rom[12] = 32'd18;
  assign config_rom[13] = 32'd20;
  assign config_rom[14] = 32'd21;
  assign config_rom[15] = 32'd23;
  assign config_rom[16] = 32'd24;
  assign config_rom[17] = 32'd31;
  //Config Rom configuration - End

  grn_derrida_plot_acc
  grn_derrida_plot_acc
  (
    .clk(tb_clk),
    .rst(tb_rst),
    .start(tb_start_reg),
    .acc_user_done_rd_data(drdp_acc_user_done_rd_data),
    .acc_user_done_wr_data(drdp_acc_user_done_wr_data),
    .acc_user_request_read(drdp_acc_user_request_read),
    .acc_user_read_data_valid(drdp_acc_user_read_data_valid),
    .acc_user_read_data(drdp_acc_user_read_data),
    .acc_user_available_write(drdp_acc_user_available_write),
    .acc_user_request_write(drdp_acc_user_request_write),
    .acc_user_write_data(drdp_acc_user_write_data),
    .acc_user_done(drdp_acc_user_done)
  );


  initial begin
    tb_clk = 0;
    tb_rst = 1;
    tb_start_reg = 0;
    drdp_acc_user_done_rd_data = 0;
    drdp_acc_user_done_wr_data = 0;
    drdp_acc_user_read_data_valid = 0;
    drdp_acc_user_read_data = 0;
    drdp_acc_user_available_write = 0;
    config_counter = 0;
    fsm_produce_data = 0;
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
    tb_start_reg = 1;
    #1000000;
    $finish;
  end

  always #5tb_clk=~tb_clk;

  always @(posedge tb_clk) begin
    if(drdp_acc_user_done) begin
      $finish;
    end 
  end


  //Simulation sector - End

endmodule



module grn_derrida_plot_acc
(
  input clk,
  input rst,
  input start,
  input [1-1:0] acc_user_done_rd_data,
  input [1-1:0] acc_user_done_wr_data,
  output [1-1:0] acc_user_request_read,
  input [1-1:0] acc_user_read_data_valid,
  input [32-1:0] acc_user_read_data,
  input [1-1:0] acc_user_available_write,
  output [1-1:0] acc_user_request_write,
  output [32-1:0] acc_user_write_data,
  output acc_user_done
);

  reg start_reg;
  wire [1-1:0] drdp_done;
  assign acc_user_done = drdp_done;

  always @(posedge clk) begin
    if(rst) begin
      start_reg <= 0;
    end else begin
      start_reg <= start_reg | start;
    end
  end


  derrita_aws_9_PE
  derrita_aws_9_PE
  (
    .clk(clk),
    .rst(rst),
    .start(start_reg),
    .drdp_done_rd_data(acc_user_done_rd_data),
    .drdp_done_wr_data(acc_user_done_wr_data),
    .drdp_request_read(acc_user_request_read),
    .drdp_read_data_valid(acc_user_read_data_valid),
    .drdp_read_data(acc_user_read_data),
    .drdp_available_write(acc_user_available_write),
    .drdp_request_write(acc_user_request_write),
    .drdp_write_data(acc_user_write_data),
    .drdp_done(drdp_done)
  );


  initial begin
    start_reg = 0;
  end


endmodule



module derrita_aws_9_PE
(
  input clk,
  input rst,
  input start,
  input drdp_done_rd_data,
  input drdp_done_wr_data,
  output reg drdp_request_read,
  input drdp_read_data_valid,
  input [32-1:0] drdp_read_data,
  input drdp_available_write,
  output drdp_request_write,
  output [32-1:0] drdp_write_data,
  output drdp_done
);


  //Config wires and regs - Begin
  localparam [2-1:0] fsm_sd_idle = 0;
  localparam [2-1:0] fsm_sd_send_data = 1;
  localparam [2-1:0] fsm_sd_done = 2;
  reg [2-1:0] fms_cs;
  reg config_valid;
  reg [32-1:0] config_data;
  reg config_done;
  reg flag;
  //Config wires and regs - End

  //PEs instantiations wires and Regs - Begin
  wire [9-1:0] pe_done;
  wire [9-1:0] pe_request_read;
  wire [9-1:0] pe_read_data_valid;
  wire [32-1:0] pe_read_data [0:9-1];
  wire [9-1:0] pe_config_output_done;
  wire [9-1:0] pe_config_output_valid;
  wire [32-1:0] pe_config_output [0:9-1];
  //PEs instantiations wires and Regs - End

  //Data Reading - Begin

  always @(posedge clk) begin
    if(rst) begin
      drdp_request_read <= 0;
      config_valid <= 0;
      fms_cs <= fsm_sd_idle;
      config_done <= 0;
      flag <= 0;
    end else begin
      if(start) begin
        config_valid <= 0;
        drdp_request_read <= 0;
        flag <= 0;
        case(fms_cs)
          fsm_sd_idle: begin
            if(drdp_read_data_valid) begin
              drdp_request_read <= 1;
              flag <= 1;
              fms_cs <= fsm_sd_send_data;
            end else if(drdp_done_rd_data) begin
              fms_cs <= fsm_sd_done;
            end 
          end
          fsm_sd_send_data: begin
            if(drdp_read_data_valid | flag) begin
              config_data <= drdp_read_data;
              config_valid <= 1;
              drdp_request_read <= 1;
            end else if(drdp_done_rd_data) begin
              fms_cs <= fsm_sd_done;
            end else begin
              fms_cs <= fsm_sd_idle;
            end
          end
          fsm_sd_done: begin
            config_done <= 1;
          end
        endcase
      end 
    end
  end

  //Data Reading - End

  //PE modules instantiation - Begin
  assign pe_read_data_valid[8] = 1;
  assign pe_read_data[8] = 0;
  assign drdp_done = pe_done[0];

  pe
  pe_0
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[0]),
    .request_read(pe_request_read[0]),
    .read_data_valid(pe_read_data_valid[0]),
    .read_data(pe_read_data[0]),
    .config_output_valid(pe_config_output_valid[0]),
    .config_output(pe_config_output[0]),
    .config_output_done(pe_config_output_done[0]),
    .request_write(drdp_request_write),
    .available_write(drdp_available_write),
    .write_data(drdp_write_data),
    .config_input_valid(config_valid),
    .config_input(config_data),
    .config_input_done(config_done)
  );


  pe
  pe_1
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[1]),
    .request_read(pe_request_read[1]),
    .read_data_valid(pe_read_data_valid[1]),
    .read_data(pe_read_data[1]),
    .config_output_valid(pe_config_output_valid[1]),
    .config_output(pe_config_output[1]),
    .config_output_done(pe_config_output_done[1]),
    .request_write(pe_read_data_valid[0]),
    .available_write(pe_request_read[0]),
    .write_data(pe_read_data[0]),
    .config_input_valid(pe_config_output_valid[0]),
    .config_input(pe_config_output[0]),
    .config_input_done(pe_config_output_done[0])
  );


  pe
  pe_2
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[2]),
    .request_read(pe_request_read[2]),
    .read_data_valid(pe_read_data_valid[2]),
    .read_data(pe_read_data[2]),
    .config_output_valid(pe_config_output_valid[2]),
    .config_output(pe_config_output[2]),
    .config_output_done(pe_config_output_done[2]),
    .request_write(pe_read_data_valid[1]),
    .available_write(pe_request_read[1]),
    .write_data(pe_read_data[1]),
    .config_input_valid(pe_config_output_valid[1]),
    .config_input(pe_config_output[1]),
    .config_input_done(pe_config_output_done[1])
  );


  pe
  pe_3
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[3]),
    .request_read(pe_request_read[3]),
    .read_data_valid(pe_read_data_valid[3]),
    .read_data(pe_read_data[3]),
    .config_output_valid(pe_config_output_valid[3]),
    .config_output(pe_config_output[3]),
    .config_output_done(pe_config_output_done[3]),
    .request_write(pe_read_data_valid[2]),
    .available_write(pe_request_read[2]),
    .write_data(pe_read_data[2]),
    .config_input_valid(pe_config_output_valid[2]),
    .config_input(pe_config_output[2]),
    .config_input_done(pe_config_output_done[2])
  );


  pe
  pe_4
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[4]),
    .request_read(pe_request_read[4]),
    .read_data_valid(pe_read_data_valid[4]),
    .read_data(pe_read_data[4]),
    .config_output_valid(pe_config_output_valid[4]),
    .config_output(pe_config_output[4]),
    .config_output_done(pe_config_output_done[4]),
    .request_write(pe_read_data_valid[3]),
    .available_write(pe_request_read[3]),
    .write_data(pe_read_data[3]),
    .config_input_valid(pe_config_output_valid[3]),
    .config_input(pe_config_output[3]),
    .config_input_done(pe_config_output_done[3])
  );


  pe
  pe_5
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[5]),
    .request_read(pe_request_read[5]),
    .read_data_valid(pe_read_data_valid[5]),
    .read_data(pe_read_data[5]),
    .config_output_valid(pe_config_output_valid[5]),
    .config_output(pe_config_output[5]),
    .config_output_done(pe_config_output_done[5]),
    .request_write(pe_read_data_valid[4]),
    .available_write(pe_request_read[4]),
    .write_data(pe_read_data[4]),
    .config_input_valid(pe_config_output_valid[4]),
    .config_input(pe_config_output[4]),
    .config_input_done(pe_config_output_done[4])
  );


  pe
  pe_6
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[6]),
    .request_read(pe_request_read[6]),
    .read_data_valid(pe_read_data_valid[6]),
    .read_data(pe_read_data[6]),
    .config_output_valid(pe_config_output_valid[6]),
    .config_output(pe_config_output[6]),
    .config_output_done(pe_config_output_done[6]),
    .request_write(pe_read_data_valid[5]),
    .available_write(pe_request_read[5]),
    .write_data(pe_read_data[5]),
    .config_input_valid(pe_config_output_valid[5]),
    .config_input(pe_config_output[5]),
    .config_input_done(pe_config_output_done[5])
  );


  pe
  pe_7
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[7]),
    .request_read(pe_request_read[7]),
    .read_data_valid(pe_read_data_valid[7]),
    .read_data(pe_read_data[7]),
    .config_output_valid(pe_config_output_valid[7]),
    .config_output(pe_config_output[7]),
    .config_output_done(pe_config_output_done[7]),
    .request_write(pe_read_data_valid[6]),
    .available_write(pe_request_read[6]),
    .write_data(pe_read_data[6]),
    .config_input_valid(pe_config_output_valid[6]),
    .config_input(pe_config_output[6]),
    .config_input_done(pe_config_output_done[6])
  );


  pe
  pe_8
  (
    .clk(clk),
    .rst(rst),
    .done(pe_done[8]),
    .request_read(pe_request_read[8]),
    .read_data_valid(pe_read_data_valid[8]),
    .read_data(pe_read_data[8]),
    .config_output_valid(pe_config_output_valid[8]),
    .config_output(pe_config_output[8]),
    .config_output_done(pe_config_output_done[8]),
    .request_write(pe_read_data_valid[7]),
    .available_write(pe_request_read[7]),
    .write_data(pe_read_data[7]),
    .config_input_valid(pe_config_output_valid[7]),
    .config_input(pe_config_output[7]),
    .config_input_done(pe_config_output_done[7])
  );

  //PE modules instantiation - End

  initial begin
    drdp_request_read = 0;
    fms_cs = 0;
    config_valid = 0;
    config_data = 0;
    config_done = 0;
    flag = 0;
  end


endmodule



module pe
(
  input clk,
  input rst,
  input config_input_done,
  input config_input_valid,
  input [32-1:0] config_input,
  output reg config_output_done,
  output reg config_output_valid,
  output reg [32-1:0] config_output,
  output reg request_read,
  input read_data_valid,
  input [32-1:0] read_data,
  input available_write,
  output reg request_write,
  output reg [32-1:0] write_data,
  output reg done
);


  //configuration wires and regs - begin
  reg is_configured;
  reg [32-1:0] pe_init_conf;
  reg [32-1:0] pe_end_conf;
  reg [0-1:0] config_counter;
  wire [32-1:0] config_forward;
  //configuration wires and regs - end

  //grn instantiation module wires and regs - begin
  reg [2-1:0] grn_input_data_valid;
  reg [5-1:0] grn_input_data;
  wire [2-1:0] grn_output_data_valid;
  wire [5-1:0] grn_output_data;
  //grn instantiation module wires and regs - end

  //Internal loop control wires and regs - begin
  reg last_loop;
  reg [3-1:0] ctrl_hm_rd_add;
  reg [5-1:0] b_r;
  reg [5-1:0] b_r_next;
  reg [5-1:0] al_r;
  reg bl_r_v;
  reg flag_send;
  reg [3-1:0] fsm_process;
  localparam fsm_process_init = 0;
  localparam fsm_process_loop = 1;
  localparam fsm_process_verify = 2;
  localparam fsm_process_wait_pipeline = 3;
  localparam fsm_process_receive = 4;
  localparam fsm_process_send = 5;
  localparam fsm_process_done = 6;
  //Internal loop control wires and regs - end

  //hamming distances instantiation wires and regs - begin
  wire [2-1:0] hm3b_add_output_data_valid;
  wire [2-1:0] hm3b_add_output_data [0:2-1];
  wire [2-1:0] hm3b_data_output_data_valid;
  wire [2-1:0] hm3b_data_output_data [0:2-1];
  //hamming distances instantiation wires and regs - end

  //Histogram memory instantiation wires and regs - begin
  wire [32-1:0] hm_rd_data;
  wire [32-1:0] hm_rd_qty;
  wire hm_rdy;
  wire [3-1:0] hm_rd_add;
  reg hm_rd_add_selector;
  //Histogram memory instantiation wires and regs - end

  //sum loops for address and data lines wires and regs - begin
  reg [3-1:0] sum_add [0:1-1];
  reg [3-1:0] reg_add [0:1-1];
  reg [2-1:0] reg_add_valid_pipe;
  wire [3-1:0] wr_address;
  wire wr;
  reg [3-1:0] sum_data [0:1-1];
  reg [3-1:0] reg_data [0:0-1];
  reg [1-1:0] reg_data_valid_pipe;
  wire [32-1:0] wr_data;
  wire wr_data_valid;
  //sum loops for address and data lines wires and regs - end

  //configuration sector - begin
  assign config_forward = pe_end_conf;

  always @(posedge clk) begin
    config_output_valid <= 0;
    config_output_done <= config_input_done;
    if(rst) begin
      is_configured <= 0;
      config_counter <= 0;
    end else begin
      if(config_input_valid) begin
        config_counter <= config_counter + 1;
        if(config_counter == 1) begin
          is_configured <= 1;
        end 
      end 
    end
    if(config_input_valid) begin
      if(~is_configured) begin
        pe_end_conf <= config_input;
        pe_init_conf <= config_forward;
      end else begin
        config_output_valid <= config_input_valid;
        config_output <= config_input;
      end
    end 
  end

  //configuration sector - end

  //Internal loop control - begin

  always @(posedge clk) begin
    if(grn_output_data_valid[1]) begin
      al_r <= grn_output_data;
    end 
    if(grn_output_data_valid[0]) begin
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
      request_read <= 0;
      request_write <= 0;
      done <= 0;
    end else begin
      if(&{ config_input_done, hm_rdy }) begin
        case(fsm_process)
          fsm_process_init: begin
            b_r <= pe_init_conf[4:0];
            grn_input_data_valid <= 2;
            b_r_next <= pe_init_conf[4:0] + 1;
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
              fsm_process <= fsm_process_receive;
              hm_rd_add_selector <= 1;
              flag_send <= 0;
              ctrl_hm_rd_add <= 0;
            end 
          end
          fsm_process_receive: begin
            request_read <= 1;
            request_write <= 0;
            if(ctrl_hm_rd_add == 6) begin
              request_read <= 0;
              fsm_process <= fsm_process_done;
            end else if(read_data_valid) begin
              request_read <= 0;
              fsm_process <= fsm_process_send;
              if(flag_send) begin
                write_data <= read_data + hm_rd_data;
              end else begin
                write_data <= read_data + hm_rd_qty;
              end
            end 
          end
          fsm_process_send: begin
            if(available_write) begin
              request_write <= 1;
              flag_send <= ~flag_send;
              fsm_process <= fsm_process_receive;
              if(flag_send) begin
                ctrl_hm_rd_add <= ctrl_hm_rd_add + 1;
              end 
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
    sum_add[0] <= hm3b_add_output_data[0] + hm3b_add_output_data[1];
    reg_add[0] <= sum_add[0];
  end


  always @(posedge clk) begin
    reg_add_valid_pipe[0] <= hm3b_add_output_data_valid[0];
    reg_add_valid_pipe[1] <= reg_add_valid_pipe[0];

  end

  //sum loop for address line sector - end

  //sum loop for data line sector - begin
  assign wr_data = sum_data[0];
  assign wr_data_valid = reg_data_valid_pipe[0];

  always @(posedge clk) begin
    sum_data[0] <= hm3b_data_output_data[0] + hm3b_data_output_data[1];

  end


  always @(posedge clk) begin
    reg_data_valid_pipe[0] <= hm3b_data_output_data_valid[0];

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

  //hamming distances instantiation sector - begin

  hamming_distance_3b
  hamming_distance_3b_add_0
  (
    .clk(clk),
    .input_data_valid(grn_input_data_valid[0]),
    .input_data({ pe_init_conf[2:0], b_r[2:0] }),
    .output_data_valid(hm3b_add_output_data_valid[0]),
    .output_data(hm3b_add_output_data[0])
  );


  hamming_distance_3b
  hamming_distance_3b_add_1
  (
    .clk(clk),
    .input_data_valid(grn_input_data_valid[0]),
    .input_data({ { 1'd0, pe_init_conf[4:3] }, { 1'd0, b_r[4:3] } }),
    .output_data_valid(hm3b_add_output_data_valid[1]),
    .output_data(hm3b_add_output_data[1])
  );


  hamming_distance_3b
  hamming_distance_3b_data_0
  (
    .clk(clk),
    .input_data_valid(grn_output_data_valid[0]),
    .input_data({ al_r[2:0], grn_output_data[2:0] }),
    .output_data_valid(hm3b_data_output_data_valid[0]),
    .output_data(hm3b_data_output_data[0])
  );


  hamming_distance_3b
  hamming_distance_3b_data_1
  (
    .clk(clk),
    .input_data_valid(grn_output_data_valid[0]),
    .input_data({ { 1'd0, al_r[4:3] }, { 1'd0, grn_output_data[4:3] } }),
    .output_data_valid(hm3b_data_output_data_valid[1]),
    .output_data(hm3b_data_output_data[1])
  );

  //hamming distances instantiation sector - end

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
    config_output_done = 0;
    config_output_valid = 0;
    config_output = 0;
    request_read = 0;
    request_write = 0;
    write_data = 0;
    done = 0;
    is_configured = 0;
    pe_init_conf = 0;
    pe_end_conf = 0;
    config_counter = 0;
    grn_input_data_valid = 0;
    grn_input_data = 0;
    last_loop = 0;
    ctrl_hm_rd_add = 0;
    b_r = 0;
    b_r_next = 0;
    al_r = 0;
    bl_r_v = 0;
    flag_send = 0;
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



module hamming_distance_3b
(
  input clk,
  input input_data_valid,
  input [6-1:0] input_data,
  output reg output_data_valid,
  output reg [2-1:0] output_data
);

  wire [2-1:0] hamming_distance_rom [0:64-1];

  always @(posedge clk) begin
    output_data_valid <= input_data_valid;
    output_data <= hamming_distance_rom[input_data];
  end

  assign hamming_distance_rom[0] = 2'b0;
  assign hamming_distance_rom[1] = 2'b1;
  assign hamming_distance_rom[2] = 2'b1;
  assign hamming_distance_rom[3] = 2'b10;
  assign hamming_distance_rom[4] = 2'b1;
  assign hamming_distance_rom[5] = 2'b10;
  assign hamming_distance_rom[6] = 2'b10;
  assign hamming_distance_rom[7] = 2'b11;
  assign hamming_distance_rom[8] = 2'b1;
  assign hamming_distance_rom[9] = 2'b0;
  assign hamming_distance_rom[10] = 2'b10;
  assign hamming_distance_rom[11] = 2'b1;
  assign hamming_distance_rom[12] = 2'b10;
  assign hamming_distance_rom[13] = 2'b1;
  assign hamming_distance_rom[14] = 2'b11;
  assign hamming_distance_rom[15] = 2'b10;
  assign hamming_distance_rom[16] = 2'b1;
  assign hamming_distance_rom[17] = 2'b10;
  assign hamming_distance_rom[18] = 2'b0;
  assign hamming_distance_rom[19] = 2'b1;
  assign hamming_distance_rom[20] = 2'b10;
  assign hamming_distance_rom[21] = 2'b11;
  assign hamming_distance_rom[22] = 2'b1;
  assign hamming_distance_rom[23] = 2'b10;
  assign hamming_distance_rom[24] = 2'b10;
  assign hamming_distance_rom[25] = 2'b1;
  assign hamming_distance_rom[26] = 2'b1;
  assign hamming_distance_rom[27] = 2'b0;
  assign hamming_distance_rom[28] = 2'b11;
  assign hamming_distance_rom[29] = 2'b10;
  assign hamming_distance_rom[30] = 2'b10;
  assign hamming_distance_rom[31] = 2'b1;
  assign hamming_distance_rom[32] = 2'b1;
  assign hamming_distance_rom[33] = 2'b10;
  assign hamming_distance_rom[34] = 2'b10;
  assign hamming_distance_rom[35] = 2'b11;
  assign hamming_distance_rom[36] = 2'b0;
  assign hamming_distance_rom[37] = 2'b1;
  assign hamming_distance_rom[38] = 2'b1;
  assign hamming_distance_rom[39] = 2'b10;
  assign hamming_distance_rom[40] = 2'b10;
  assign hamming_distance_rom[41] = 2'b1;
  assign hamming_distance_rom[42] = 2'b11;
  assign hamming_distance_rom[43] = 2'b10;
  assign hamming_distance_rom[44] = 2'b1;
  assign hamming_distance_rom[45] = 2'b0;
  assign hamming_distance_rom[46] = 2'b10;
  assign hamming_distance_rom[47] = 2'b1;
  assign hamming_distance_rom[48] = 2'b10;
  assign hamming_distance_rom[49] = 2'b11;
  assign hamming_distance_rom[50] = 2'b1;
  assign hamming_distance_rom[51] = 2'b10;
  assign hamming_distance_rom[52] = 2'b1;
  assign hamming_distance_rom[53] = 2'b10;
  assign hamming_distance_rom[54] = 2'b0;
  assign hamming_distance_rom[55] = 2'b1;
  assign hamming_distance_rom[56] = 2'b11;
  assign hamming_distance_rom[57] = 2'b10;
  assign hamming_distance_rom[58] = 2'b10;
  assign hamming_distance_rom[59] = 2'b1;
  assign hamming_distance_rom[60] = 2'b10;
  assign hamming_distance_rom[61] = 2'b1;
  assign hamming_distance_rom[62] = 2'b1;
  assign hamming_distance_rom[63] = 2'b0;

  initial begin
    output_data_valid = 0;
    output_data = 0;
  end


endmodule



module histogram_memory
(
  input clk,
  input rst,
  input [3-1:0] rd_add,
  input wr,
  input [3-1:0] wr_add,
  input [32-1:0] wr_data,
  output [32-1:0] rd_data,
  output [32-1:0] rd_qty,
  output reg rdy
);

  reg [3-1:0] rst_counter;
  reg flag_rst;
  reg [8-1:0] valid;
  reg [32-1:0] sum_m [0:8-1];
  reg [32-1:0] qty_m [0:8-1];
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
    for(i_initial=0; i_initial<8; i_initial=i_initial+1) begin
      sum_m[i_initial] = 0;
    end
    for(i_initial=0; i_initial<8; i_initial=i_initial+1) begin
      qty_m[i_initial] = 0;
    end
  end


endmodule

