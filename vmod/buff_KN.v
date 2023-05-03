module buff_KN # (
	parameter                                                       NUM_PEGS        ,
	parameter                                                       LOG2_PEGS       ,
	parameter                                                       NUM_PES         ,
	parameter                                                       DATA_TYPE       ,
	parameter                                                       PARA_BLOCKS     ,
	parameter                                                       LOG2_PARA_BLOCKS)(

	input                                                           clk,
	input                                                           rst,

	input               [PARA_BLOCKS * DATA_TYPE * NUM_PES - 1 : 0] i_fifo_KN_data_out,

	input                                                           i_fifo_KN_data_empty,
	input               [1 : 0]                                     i_backup_fifo_ena,
	input               [LOG2_PARA_BLOCKS : 0]                      i_block_counter,
	input               [LOG2_PEGS * (PARA_BLOCKS + 1) - 1: 0]      i_peg_num_counter,

	input                                                           data_source,
	input                                                           KN_counter_ena,


	output      reg     [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]     o_KN_data_bus,

	output      reg     [PARA_BLOCKS - 1 : 0]                       o_fifo_KN_rd_en

);


	reg     [LOG2_PARA_BLOCKS+1 : 0]  KN_fifo_counter;

	wire    [LOG2_PARA_BLOCKS+1 : 0]  KN_fifo_counter_temp;
	assign  KN_fifo_counter_temp    =   KN_fifo_counter + i_block_counter + 1'b1 - i_backup_fifo_ena[1];

	always @(posedge clk) begin
		if(rst) begin
			KN_fifo_counter <= 'd0;
		end else begin
			if(!data_source && !i_fifo_KN_data_empty && KN_counter_ena) begin
				if(KN_fifo_counter_temp < PARA_BLOCKS) begin
					KN_fifo_counter <= KN_fifo_counter_temp;
				end else begin
					KN_fifo_counter <= KN_fifo_counter_temp - PARA_BLOCKS;
				end
			end else begin
				KN_fifo_counter <= KN_fifo_counter;
			end
		end
	end



	// ======================= backup fifo to store KN data =======================
	wire                                        w_fifo_backup_rd_en;

	reg                                         r_fifo_backup_wr_en;
	wire    [DATA_TYPE * NUM_PES - 1 : 0]       w_fifo_backup_data_in;

	wire    [DATA_TYPE * NUM_PES - 1 : 0]       w_fifo_backup_data_out;
	wire                                        w_fifo_backup_full;
	wire                                        w_fifo_backup_empty;


	assign w_fifo_backup_rd_en = !(data_source | KN_counter_ena | i_fifo_KN_data_empty) & i_backup_fifo_ena[1];


	// backup_fifo write in
	always @(posedge clk) begin
		if(rst) begin
			r_fifo_backup_wr_en     <=   1'b0;
			// r_fifo_backup_data_in   <=   'd0;
		end else begin
			if(!(data_source || KN_counter_ena || i_fifo_KN_data_empty) && i_backup_fifo_ena[0]) begin
				r_fifo_backup_wr_en     =   1'b1;
				// r_fifo_backup_data_in   =   i_fifo_KN_data_out[((KN_fifo_counter_temp - 1'b1) % PARA_BLOCKS) * (DATA_TYPE*NUM_PES) +: (DATA_TYPE*NUM_PES)];
			end else begin
				r_fifo_backup_wr_en     <=   1'b0;
				// r_fifo_backup_data_in   <=   'd0;
			end
		end
	end

	assign w_fifo_backup_data_in   =   i_fifo_KN_data_out[((KN_fifo_counter_temp - 1'b1) % PARA_BLOCKS) * (DATA_TYPE*NUM_PES) +: (DATA_TYPE*NUM_PES)];


	fifo_KN_data_backup my_fifo_KN_data_backup (
		.clk(clk),
		.rst(rst),
		.din(w_fifo_backup_data_in),
		.wr_en(r_fifo_backup_wr_en),
		.rd_en(w_fifo_backup_rd_en),
		.dout(w_fifo_backup_data_out),
		.full(w_fifo_backup_full),
		.empty(w_fifo_backup_empty)
	);



	// ======================= KN input: o_fifo_KN_rd_en_x =======================

	integer i;
	always @(*) begin

		o_fifo_KN_rd_en = 'd0;
		for(i = 0; i < PARA_BLOCKS; i = i + 1) begin: fifo_KN_rd_en_gen
			if(!(data_source || KN_counter_ena || i_fifo_KN_data_empty)) begin
				if((KN_fifo_counter <= i && i < KN_fifo_counter_temp) || (KN_fifo_counter <= i+PARA_BLOCKS && i+PARA_BLOCKS < KN_fifo_counter_temp))
					o_fifo_KN_rd_en[i] = 1'b1;
			end
		end

	end



	// ======================= KN output: o_KN_data_bus =======================

	wire    [(PARA_BLOCKS-1)*LOG2_PARA_BLOCKS-1 :0]  KN_fifo_counter_p;
	genvar j;
	generate
		for(j = 1; j < PARA_BLOCKS; j = j + 1) begin: KN_fifo_counter_p_gen
			assign KN_fifo_counter_p[(j-1)*LOG2_PARA_BLOCKS +: LOG2_PARA_BLOCKS] = (KN_fifo_counter + j < PARA_BLOCKS) ? KN_fifo_counter + j : KN_fifo_counter + j - PARA_BLOCKS;
		end
	endgenerate


	generate
		for(j = 0; j < NUM_PEGS; j = j + 1) begin: o_KN_data_bus_gen
			always @(*) begin

				o_KN_data_bus[j*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)]   =  'd0;

				if(!data_source) begin
					if(i_backup_fifo_ena[1]) begin
						o_KN_data_bus[j*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)]   =  w_fifo_backup_data_out;
						for(i = 0; i < PARA_BLOCKS; i = i + 1) begin
							if(i_peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS] < j) begin
								if(i == 0) begin
									o_KN_data_bus[j*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)] = i_fifo_KN_data_out[KN_fifo_counter*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)];
								end else begin
									o_KN_data_bus[j*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)] = i_fifo_KN_data_out[KN_fifo_counter_p[(i-1)*LOG2_PARA_BLOCKS +: LOG2_PARA_BLOCKS]*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)];
								end
							end
						end
					end else begin
						// default
						o_KN_data_bus[j*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)]   =  i_fifo_KN_data_out[KN_fifo_counter*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)];
						// others
						for(i = 0; i < PARA_BLOCKS-1; i = i + 1) begin
							if(i_peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS] < j) begin
								o_KN_data_bus[j*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)] = i_fifo_KN_data_out[KN_fifo_counter_p[i*LOG2_PARA_BLOCKS +: LOG2_PARA_BLOCKS]*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)];
							end
						end
					end
				end

			end
		end
	endgenerate

endmodule

