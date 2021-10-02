

module test_bench
(

);

  reg tb_clk;
  reg tb_rst;
  reg tb_wr;
  reg [3-1:0] tb_add;
  reg [8-1:0] tb_wr_data;
  reg [6-1:0] counter_wr;
  reg [3-1:0] counter_rd;
  reg td_done;
  wire [8-1:0] hm_rd_data;
  wire hm_rdy;

  always @(posedge tb_clk) begin
    if(tb_rst) begin
      tb_wr <= 0;
      counter_wr <= 0;
      counter_rd <= 0;
      td_done <= 0;
    end else begin
      if(hm_rdy) begin
        if(&counter_wr) begin
          tb_wr <= 0;
          if(&counter_rd) begin
            td_done <= 1;
          end else begin
            tb_add <= counter_rd;
            counter_rd <= counter_rd + 1;
          end
        end else begin
          tb_wr <= 1;
          tb_add <= $random%8.0;
          tb_wr_data <= $random%2 + hm_rd_data;
          counter_wr <= counter_wr + 1;
        end
      end 
    end
  end


  histogram_memory
  histogram_memory
  (
    .clk(tb_clk),
    .rst(tb_rst),
    .rd_add(tb_add),
    .wr(tb_wr),
    .wr_add(tb_add),
    .wr_data(tb_wr_data),
    .rd_data(hm_rd_data),
    .rdy(hm_rdy)
  );


  initial begin
    tb_clk = 0;
    tb_rst = 1;
    tb_wr = 0;
    tb_add = 0;
    tb_wr_data = 0;
    counter_wr = 0;
    counter_rd = 0;
    td_done = 0;
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
    if(td_done) begin
      $finish;
    end 
  end


endmodule



module histogram_memory
(
  input clk,
  input rst,
  input [3-1:0] rd_add,
  input wr,
  input [3-1:0] wr_add,
  input [8-1:0] wr_data,
  output [8-1:0] rd_data,
  output reg rdy
);

  reg [3-1:0] rst_counter;
  reg flag_rst;
  reg [8-1:0] valid;
  reg [8-1:0] mem [0:8-1];
  assign rd_data = (valid[rd_add])? mem[rd_add] : 0;

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
          rst_counter <= rst_counter + 1;
        end
      end else begin
        if(wr) begin
          mem[wr_add] <= wr_data;
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
      mem[i_initial] = 0;
    end
  end


endmodule

