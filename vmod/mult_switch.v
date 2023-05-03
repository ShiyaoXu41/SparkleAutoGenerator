/////////////////////////////////////////////////////////////////////////
// Design: mult_switch.v
// Description: multiply switch with local stationary buffer
/////////////////////////////////////////////////////////////////////////


module mult_switch #(
	parameter IN_DATA_TYPE  ,
	parameter OUT_DATA_TYPE )(
	clk,
	rst,
	i_valid, // input valid signal
	i_data, // input data
	i_stationary, // input control bit whether
	o_valid, // output valid signal
	o_data // output data
);

	input clk;
	input rst;
	input i_valid;
	input [IN_DATA_TYPE-1:0] i_data;
	input i_stationary;

	output reg o_valid;
	output [OUT_DATA_TYPE-1:0] o_data;

	reg [IN_DATA_TYPE-1:0] r_buffer; // buffer to hold stationary value
	reg r_buffer_valid; // valid buffer entry

	wire [IN_DATA_TYPE-1:0] w_A;
	wire [IN_DATA_TYPE-1:0] w_B;

	// logic to store correct value into the stationary buffer
	always @ (posedge clk) begin
		if (rst == 1'b1) begin
			r_buffer <= 'd0; // clear buffer during reset
			r_buffer_valid <= 1'b0; // invalidate buffer
		end else begin
			if (i_stationary == 1'b1 && i_valid == 1'b1) begin
				r_buffer <= i_data; // latch the stationary value into the switch buffer
				r_buffer_valid <= 1'b1; // validate buffer
			end
		end
	end

	assign w_A = (r_buffer_valid == 1'b1 && i_valid == 1'b1) ? i_data : 'd0; // streaming
	assign w_B = (r_buffer_valid == 1'b1 && i_valid == 1'b1) ? r_buffer : 'd0; // stationary

	// logic to generate correct output valid signal
	always @ (posedge clk) begin
		if (r_buffer_valid == 1'b1 && i_valid == 1'b1) begin
				o_valid <= 1'b1;
		end else begin
				o_valid <= 1'b0;
		end
	end

	// instantiate mult
	// IP CORE
	Mult my_Mult (
		.CLK(clk),
		.A(w_A),        // stationary value
		.B(w_B),        // streaming value
		.P(o_data[OUT_DATA_TYPE-1:0])
	);

	// mult_n #(
	//     .IN_DATA_TYPE(IN_DATA_TYPE),
	//     .OUT_DATA_TYPE(OUT_DATA_TYPE))
	//     my_mult_n (
	// 	.clk(clk),
	// 	.A(w_A), // stationary value
	// 	.B(w_B), // streaming value
	// 	.O(o_data)
	// );

endmodule

