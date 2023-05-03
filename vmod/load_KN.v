module load_KN # (
	parameter   DATA_TYPE       ,
	parameter   NUM_PES         ,
	parameter   LOG2_PES        ,
	parameter   PARA_BLOCKS     ,
	parameter   LOG2_PARA_BLOCKS) (

	input                                                       clk,
	input                                                       rst,
	input                                                       ena,
	input       [20 : 0]                                        M_DIM,
	input       [20 : 0]                                        K_DIM,
	input       [20 : 0]                                        K_PAD,
	input       [20 : 0]                                        N_DIM,

	input       [PARA_BLOCKS-1 : 0]                             i_fifo_KN_rd_en,

	output      [PARA_BLOCKS * DATA_TYPE * NUM_PES - 1 : 0]     o_fifo_KN_data_out,
	output                                                      o_fifo_KN_data_empty
);

	parameter   KN_DATA_READ_WIDTH  =   PARA_BLOCKS * NUM_PES;

	wire    [PARA_BLOCKS-1 : 0]     w_fifo_KN_data_empty;

	wire    [PARA_BLOCKS-1 : 0]     w_fifo_KN_full;

	wire    full;
	assign  full                    =   |w_fifo_KN_full;

	wire    unstall;
	assign  unstall                 =   ena & !full;


	/////////////////////////////////////////////////////////////////////////
	// zero cycle 
	// counters' movments & bitmap addr
	/////////////////////////////////////////////////////////////////////////

	reg     [10 : 0]    KN_bitmap_iter_counter;         // matrix iter times
	reg     [10 : 0]    KN_bitmap_block_row_counter;
	reg     [10 : 0]    KN_bitmap_read_col_counter;     // every col get paralisim(4) block data

	// counters' movements

	wire    KN_bitmap_iter_counter_ena,     KN_bitmap_block_row_counter_ena,    KN_bitmap_read_col_counter_ena;

	assign  KN_bitmap_iter_counter_ena      =   (KN_bitmap_iter_counter == M_DIM / NUM_PES - 1) ? 1'b1 : 1'b0;
	assign  KN_bitmap_block_row_counter_ena =   (KN_bitmap_block_row_counter == K_PAD / KN_DATA_READ_WIDTH - 1) ? 1'b1 : 1'b0;
	assign  KN_bitmap_read_col_counter_ena  =   (KN_bitmap_read_col_counter == N_DIM - 1) ? 1'b1 : 1'b0;

	always @(posedge clk) begin
		if(rst) begin
			KN_bitmap_iter_counter          <=  'd0;
		end else if(unstall && KN_bitmap_read_col_counter_ena && KN_bitmap_block_row_counter_ena) begin
			if(KN_bitmap_iter_counter_ena) begin
				KN_bitmap_iter_counter          <=  'd0;
			end else begin
				KN_bitmap_iter_counter          <=  KN_bitmap_iter_counter + 1'b1;
			end
		end else begin
			KN_bitmap_iter_counter          <=  KN_bitmap_iter_counter;
		end
	end

	always @(posedge clk) begin
		if(rst) begin
			KN_bitmap_block_row_counter     <=  'd0;
		end else if(unstall && KN_bitmap_read_col_counter_ena) begin
			if(!KN_bitmap_block_row_counter_ena) begin
				KN_bitmap_block_row_counter     <=  KN_bitmap_block_row_counter + 1'b1;
			end else begin
				KN_bitmap_block_row_counter     <=  'd0;
			end
		end else begin
			KN_bitmap_block_row_counter     <=  KN_bitmap_block_row_counter;
		end
	end

	always @(posedge clk) begin
		if(rst) begin
			KN_bitmap_read_col_counter      <=  'd0;
		end else if(unstall) begin
			if(!KN_bitmap_read_col_counter_ena) begin
				KN_bitmap_read_col_counter      <=  KN_bitmap_read_col_counter + 1'b1;
			end else begin
				KN_bitmap_read_col_counter      <=  'd0;
			end
		end else begin
			KN_bitmap_read_col_counter      <=  KN_bitmap_read_col_counter;
		end
	end


	// bitmap address
	wire [20:0] w_KN_addr;
	assign w_KN_addr = (K_PAD / KN_DATA_READ_WIDTH * KN_bitmap_read_col_counter + KN_bitmap_block_row_counter);


	/////////////////////////////////////////////////////////////////////////
	// 1st cycle
	// get data
	/////////////////////////////////////////////////////////////////////////

	// read data from RAM
	wire [KN_DATA_READ_WIDTH*DATA_TYPE-1 : 0] w_KN_data;
	bram_KN_data my_bram_KN_data (
		.clka(clk),
		.ena(unstall),
		.wea(1'b0),
		.addra(w_KN_addr),
		.dina('d0),
		.douta(w_KN_data)
	);


	// pad_cnt, start_pt, end_pt, help to write data in fifos
	wire    [LOG2_PARA_BLOCKS-1 : 0]    pad_cnt;
	assign  pad_cnt = (K_PAD-K_DIM)/NUM_PES;

	reg     KN_bitmap_block_row_counter_ena_ff;
	always @(posedge clk) begin
		if(rst) begin
			KN_bitmap_block_row_counter_ena_ff  <=  'd0;
		end else begin
			KN_bitmap_block_row_counter_ena_ff  <=  KN_bitmap_block_row_counter_ena;
		end
	end

	reg     [LOG2_PARA_BLOCKS : 0]    start_pt;
	always @(posedge clk) begin
		if(rst) begin
			start_pt <= 'd0;
		end else begin
			if(!KN_bitmap_block_row_counter_ena && KN_bitmap_block_row_counter_ena_ff && K_DIM != K_PAD) begin
				start_pt    <=  (start_pt + (PARA_BLOCKS-pad_cnt)) % PARA_BLOCKS;
			end else begin
				start_pt    <=  start_pt;
			end
		end
	end

	wire    [LOG2_PARA_BLOCKS : 0] end_pt;
	assign  end_pt = start_pt + (PARA_BLOCKS-pad_cnt);


	integer j;
	// wr_en & din
	reg     [PARA_BLOCKS-1 : 0]     r_wr_en;
	always @(posedge clk) begin
		for(j = 0; j < PARA_BLOCKS; j = j + 1) begin
			if(rst) begin
				r_wr_en[j]  <=  'd0;
			end else begin
				if(KN_bitmap_block_row_counter_ena && K_DIM != K_PAD) begin
					if((start_pt <= j && j < end_pt) || (start_pt <= j + PARA_BLOCKS && j + PARA_BLOCKS < end_pt)) begin
						r_wr_en[j] <= unstall;
					end else begin
						r_wr_en[j] <= 1'b0;
					end
				end else begin
					r_wr_en[j] <= unstall;
				end
			end
		end
	end

	genvar i;
	reg [KN_DATA_READ_WIDTH*DATA_TYPE-1 : 0] w_din;
	generate
		for(i = 0; i < PARA_BLOCKS; i = i + 1) begin
			always @(*) begin
				// if(i+start_pt < PARA_BLOCKS) begin
				// 	w_din[(i+start_pt)*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE] = w_KN_data[i*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE];
				// end else begin
				// 	w_din[(i+start_pt-PARA_BLOCKS)*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE] = w_KN_data[i*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE];
				// end
                if(i < start_pt) begin
					w_din[i*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE] = w_KN_data[(i+PARA_BLOCKS-start_pt)*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE];
				end else begin
					w_din[i*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE] = w_KN_data[(i-start_pt)*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE];
				end
			end
		end
	endgenerate



	generate
		for(i = 0; i < PARA_BLOCKS; i = i + 1) begin: fifo_KN_data_gen
			fifo_KN_data my_fifo_KN_data (
				.clk(clk),                                                      // input wire clk
				.rst(rst),                                                      // input wire rst
				.din(w_din[i*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE]),
				.wr_en(r_wr_en[i]),
				.rd_en(i_fifo_KN_rd_en[i]),                                     // input wire rd_en
				.dout(o_fifo_KN_data_out[i*(DATA_TYPE*NUM_PES) +: (DATA_TYPE*NUM_PES)]),
				.almost_full(w_fifo_KN_full[i]),                                // output wire full
				.empty(w_fifo_KN_data_empty[i])                                 // output wire empty
			);
		end
	endgenerate

	assign o_fifo_KN_data_empty = |w_fifo_KN_data_empty;

endmodule
