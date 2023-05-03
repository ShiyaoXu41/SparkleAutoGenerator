/////////////////////////////////////////////////////////////////////////
// Design: output_(NUM_PEGS).v
// Description: the output module for the serialization of output
/////////////////////////////////////////////////////////////////////////


module res_output # (
	parameter   NUM_PEGS    ,
	parameter   DATA_TYPE   ,
	parameter   PARA_BLOCKS ) (

	input                                                   clk,
	input                                                   rst,
	input                                                   ena,

	input       [PARA_BLOCKS:0]                             i_data_valid,
	input       [(PARA_BLOCKS + 1)*NUM_PEGS*DATA_TYPE-1:0]  i_data_bus,

	output  reg                                             o_data_valid,
	output  reg [NUM_PEGS*DATA_TYPE-1:0]                    o_data_bus
);


	// output port
	wire    [PARA_BLOCKS:0]                                 w_fifo_output_full;
	wire    [PARA_BLOCKS:0]                                 w_fifo_output_empty;
	wire    [(PARA_BLOCKS + 1)*NUM_PEGS*DATA_TYPE-1:0]      w_fifo_output_out;
	// input port
	reg     [PARA_BLOCKS:0]                                 w_fifo_output_rd_en;

	genvar i;
	generate
		for(i = 0; i < PARA_BLOCKS + 1; i = i + 1) begin
			always@(*) begin
				if(i == 0) begin
					w_fifo_output_rd_en[i] = !w_fifo_output_empty[i];
				end else begin
					w_fifo_output_rd_en[i] = (!w_fifo_output_empty[i]) & (&w_fifo_output_empty[i-1:0]);
				end
			end
		end
	endgenerate


	generate
		for(i = 0; i < PARA_BLOCKS + 1; i = i + 1) begin: fifo_output_gen
			fifo_output my_fifo_output (
				.clk(clk),                                                      // input wire clk
				.rst(rst),                                                          // input wire rst
				.din(i_data_bus[i*NUM_PEGS*DATA_TYPE +: NUM_PEGS*DATA_TYPE]),
				.wr_en(i_data_valid[i]),
				.rd_en(w_fifo_output_rd_en[i]),                                     // input wire rd_en

				.dout(w_fifo_output_out[i*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)]),
				.full(w_fifo_output_full[i]),                                       // output wire full
				.empty(w_fifo_output_empty[i])                                      // output wire empty
			);
		end
	endgenerate


	always @(posedge clk) begin
		if(rst) begin
			o_data_valid    <= 1'b0;
		end else begin
			o_data_valid    <= |w_fifo_output_rd_en;
		end
	end

	integer j;
	always @(posedge clk) begin
		if(rst) begin
			o_data_bus      <=  'd0;
		end else begin
			for(j = PARA_BLOCKS; j >= 0; j = j - 1) begin
				if(w_fifo_output_rd_en[j]) begin
					o_data_bus      <=  w_fifo_output_out[j*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)];
				end
			end
		end
		// if(w_fifo_output_rd_en[0]) begin
		//     o_data_bus      <=  w_fifo_output_out[0*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)];
		// end else if (w_fifo_output_rd_en[1]) begin
		//     o_data_bus      <=  w_fifo_output_out[1*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)];
		// end else if (w_fifo_output_rd_en[2]) begin
		//     o_data_bus      <=  w_fifo_output_out[2*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)];
		// end else if (w_fifo_output_rd_en[3]) begin
		//     o_data_bus      <=  w_fifo_output_out[3*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)];
		// end else if (w_fifo_output_rd_en[4]) begin
		//     o_data_bus      <=  w_fifo_output_out[4*(DATA_TYPE*NUM_PEGS) +: (DATA_TYPE*NUM_PEGS)];
		// end else begin
		//     o_data_bus      <=  o_data_bus;
		// end

	end

endmodule