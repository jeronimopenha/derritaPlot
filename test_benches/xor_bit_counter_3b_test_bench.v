

module test_bench
(

);

  reg tb_clk;
  reg tb_rst;
  wire tb_dp_output_data_valid;
  wire [6-1:0] tb_dp_output_data;
  wire tb_dp_done;
  wire xbc3_output_data_valid;
  wire [2-1:0] xbc3_output_data;
  wire tb_done;

  data_producer
  data_producer
  (
    .dp_clk(tb_clk),
    .dp_rst(tb_rst),
    .dp_output_data_valid(tb_dp_output_data_valid),
    .dp_output_data(tb_dp_output_data),
    .dp_done(tb_dp_done)
  );


  xor_bit_counter_3b
  xor_bit_counter_3b
  (
    .clk(tb_clk),
    .input_data_valid(tb_dp_output_data_valid),
    .input_data(tb_dp_output_data),
    .output_data_valid(xbc3_output_data_valid),
    .output_data(xbc3_output_data)
  );

  assign tb_done = tb_dp_done & ~xbc3_output_data_valid;

  initial begin
    tb_clk = 0;
    tb_rst = 1;
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
    #10000;
    $finish;
  end

  always #5tb_clk=~tb_clk;

  always @(posedge tb_clk) begin
    if(tb_done) begin
      $finish;
    end 
  end


endmodule



module data_producer
(
  input dp_clk,
  input dp_rst,
  output reg dp_output_data_valid,
  output reg [6-1:0] dp_output_data,
  output reg dp_done
);

  reg [6-1:0] dp_data_counter;
  reg dp_fsm;
  localparam dp_fsm_to_produce = 0;
  localparam dp_fsm_done = 1;

  always @(posedge dp_clk) begin
    if(dp_rst) begin
      dp_data_counter <= 0;
      dp_output_data_valid <= 0;
      dp_done <= 0;
      dp_output_data <= 0;
      dp_fsm <= dp_fsm_to_produce;
    end else begin
      case(dp_fsm)
        dp_fsm_to_produce: begin
          dp_output_data_valid <= 1;
          dp_output_data <= dp_data_counter;
          dp_data_counter <= dp_data_counter + 1;
          if(dp_data_counter == 63.0) begin
            dp_fsm <= dp_fsm_done;
          end 
        end
        dp_fsm_done: begin
          dp_output_data_valid <= 0;
          dp_output_data <= 0;
          dp_done <= 1;
        end
      endcase
    end
  end


  initial begin
    dp_output_data_valid = 0;
    dp_output_data = 0;
    dp_done = 0;
    dp_data_counter = 0;
    dp_fsm = 0;
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

