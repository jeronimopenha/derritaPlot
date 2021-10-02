

module tb
(

);

  reg tb_clk;
  reg tb_rst;
  wire tb_dp_output_data_valid;
  wire [6-1:0] tb_dp_output_data;
  wire tb_dp_done;
  wire xbc3_output_valid;
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
    .input_valid(tb_dp_output_data_valid),
    .input_data(tb_dp_output_data),
    .output_valid(xbc3_output_valid),
    .output_data(xbc3_output_data)
  );

  assign tb_done = tb_dp_done & ~xbc3_output_valid;

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
  wire [6-1:0] dp_data_out_rom [0:64-1];

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
          dp_output_data <= dp_data_out_rom[dp_data_counter];
          dp_data_counter <= dp_data_counter + 1;
          if(dp_data_counter == 63) begin
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

  assign dp_data_out_rom[0] = 6'b0;
  assign dp_data_out_rom[1] = 6'b1;
  assign dp_data_out_rom[2] = 6'b10;
  assign dp_data_out_rom[3] = 6'b11;
  assign dp_data_out_rom[4] = 6'b100;
  assign dp_data_out_rom[5] = 6'b101;
  assign dp_data_out_rom[6] = 6'b110;
  assign dp_data_out_rom[7] = 6'b111;
  assign dp_data_out_rom[8] = 6'b1000;
  assign dp_data_out_rom[9] = 6'b1001;
  assign dp_data_out_rom[10] = 6'b1010;
  assign dp_data_out_rom[11] = 6'b1011;
  assign dp_data_out_rom[12] = 6'b1100;
  assign dp_data_out_rom[13] = 6'b1101;
  assign dp_data_out_rom[14] = 6'b1110;
  assign dp_data_out_rom[15] = 6'b1111;
  assign dp_data_out_rom[16] = 6'b10000;
  assign dp_data_out_rom[17] = 6'b10001;
  assign dp_data_out_rom[18] = 6'b10010;
  assign dp_data_out_rom[19] = 6'b10011;
  assign dp_data_out_rom[20] = 6'b10100;
  assign dp_data_out_rom[21] = 6'b10101;
  assign dp_data_out_rom[22] = 6'b10110;
  assign dp_data_out_rom[23] = 6'b10111;
  assign dp_data_out_rom[24] = 6'b11000;
  assign dp_data_out_rom[25] = 6'b11001;
  assign dp_data_out_rom[26] = 6'b11010;
  assign dp_data_out_rom[27] = 6'b11011;
  assign dp_data_out_rom[28] = 6'b11100;
  assign dp_data_out_rom[29] = 6'b11101;
  assign dp_data_out_rom[30] = 6'b11110;
  assign dp_data_out_rom[31] = 6'b11111;
  assign dp_data_out_rom[32] = 6'b100000;
  assign dp_data_out_rom[33] = 6'b100001;
  assign dp_data_out_rom[34] = 6'b100010;
  assign dp_data_out_rom[35] = 6'b100011;
  assign dp_data_out_rom[36] = 6'b100100;
  assign dp_data_out_rom[37] = 6'b100101;
  assign dp_data_out_rom[38] = 6'b100110;
  assign dp_data_out_rom[39] = 6'b100111;
  assign dp_data_out_rom[40] = 6'b101000;
  assign dp_data_out_rom[41] = 6'b101001;
  assign dp_data_out_rom[42] = 6'b101010;
  assign dp_data_out_rom[43] = 6'b101011;
  assign dp_data_out_rom[44] = 6'b101100;
  assign dp_data_out_rom[45] = 6'b101101;
  assign dp_data_out_rom[46] = 6'b101110;
  assign dp_data_out_rom[47] = 6'b101111;
  assign dp_data_out_rom[48] = 6'b110000;
  assign dp_data_out_rom[49] = 6'b110001;
  assign dp_data_out_rom[50] = 6'b110010;
  assign dp_data_out_rom[51] = 6'b110011;
  assign dp_data_out_rom[52] = 6'b110100;
  assign dp_data_out_rom[53] = 6'b110101;
  assign dp_data_out_rom[54] = 6'b110110;
  assign dp_data_out_rom[55] = 6'b110111;
  assign dp_data_out_rom[56] = 6'b111000;
  assign dp_data_out_rom[57] = 6'b111001;
  assign dp_data_out_rom[58] = 6'b111010;
  assign dp_data_out_rom[59] = 6'b111011;
  assign dp_data_out_rom[60] = 6'b111100;
  assign dp_data_out_rom[61] = 6'b111101;
  assign dp_data_out_rom[62] = 6'b111110;
  assign dp_data_out_rom[63] = 6'b111111;

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
  input input_valid,
  input [6-1:0] input_data,
  output reg output_valid,
  output reg [2-1:0] output_data
);

  wire [2-1:0] xor_bit_counter_rom [0:64-1];

  always @(posedge clk) begin
    output_valid <= input_valid;
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
    output_valid = 0;
    output_data = 0;
  end


endmodule

