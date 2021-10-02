

module test_bench
(

);

  reg tb_clk;
  reg tb_rst;
  wire tb_dp_output_data_valid;
  wire [5-1:0] tb_dp_output_data;
  wire tb_dp_done;
  wire grn_output_data_valid;
  wire [5-1:0] grn_output_data;
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


  grn
  grn
  (
    .clk(tb_clk),
    .input_data_valid(tb_dp_output_data_valid),
    .input_data(tb_dp_output_data),
    .output_data_valid(grn_output_data_valid),
    .output_data(grn_output_data)
  );

  assign tb_done = tb_dp_done & ~grn_output_data_valid;

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
  output reg [5-1:0] dp_output_data,
  output reg dp_done
);

  reg [5-1:0] dp_data_counter;
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
          if(dp_data_counter == 31.0) begin
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



module grn
(
  input clk,
  input input_data_valid,
  input [5-1:0] input_data,
  output reg output_data_valid,
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

