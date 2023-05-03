/////////////////////////////////////////////////////////////////////////
// Design: load_MK.v
// Description: load MK into fifos from on-chip memory
/////////////////////////////////////////////////////////////////////////


module load_MK # (
	parameter   DATA_TYPE   ,
	parameter   NUM_PEGS    ,
	parameter   LOG2_PEGS   ,
    // block_size is default as same as NUM_PES
	parameter   NUM_PES     ,
	parameter   LOG2_PES    ,
	parameter   LOG2_MEMD   ,
	parameter   POINTER_WIDTH) (

	input                                           clk,
	input                                           rst,
	input                                           ena,
	input       [20 : 0]                            M_DIM,
	input       [20 : 0]                            K_DIM,

	input                                           i_fifo_MK_rd_en,

	output      [DATA_TYPE * NUM_PES - 1 : 0]       o_fifo_MK_data_out,
	output      [LOG2_PES * NUM_PES - 1 : 0]        o_fifo_dest_out,
	output      [LOG2_PEGS * NUM_PES - 1 : 0]       o_fifo_vn_out,
	output      [1 : 0]                             o_fifo_flag_out,

	output                                          o_fifo_MK_empty
);

	parameter   MK_DATA_READ_WIDTH =   2*NUM_PES;

	wire    w_MK_read_data_stall;
	wire    w_MK_write_data_stall;
	wire    w_fifo_MK_full;


	/////////////////////////////////////////////////////////////////////////
	// zero cycle
	// counters' movments & bitmap addr
	/////////////////////////////////////////////////////////////////////////

	// 3 counters decide index (befor ena counter is zero by default)
	// counter couting block index (for MK bitmap matrix)
	reg     [10 : 0]    r_MK_block_row_counter,    r_MK_block_col_counter;
	// counter recording the number of rows(for MK) in a block
	reg     [10 : 0]    r_MK_read_row_counter;


	// counters' movements
	always @(posedge clk) begin
		if(rst == 1'b1) begin

			r_MK_block_row_counter     <=  'd0;
			r_MK_block_col_counter     <=  'd0;
			r_MK_read_row_counter      <=  'd0;

		end else if(ena & !w_MK_read_data_stall & !w_MK_write_data_stall & !w_fifo_MK_full) begin

			// finish reading NUM_PEGS rows in a block
			if(r_MK_read_row_counter == NUM_PEGS - 1) begin
				// finish reading NUM_PES matrix rows
				if(r_MK_block_col_counter == K_DIM / NUM_PES - 1) begin
					// finish reading the whole matrix
					if(r_MK_block_row_counter == M_DIM / NUM_PEGS - 1) begin
						r_MK_block_row_counter     <=  'd0;
						r_MK_block_col_counter     <=  'd0;
						r_MK_read_row_counter      <=  'd0;
					end else begin
						r_MK_block_row_counter     <=  r_MK_block_row_counter + 1'b1;
						r_MK_block_col_counter     <=  'd0;
						r_MK_read_row_counter      <=  'd0;
					end
				end else begin
					r_MK_block_row_counter     <=  r_MK_block_row_counter;
					r_MK_block_col_counter     <=  r_MK_block_col_counter + 1'b1;
					r_MK_read_row_counter      <=  'd0;
				end
			end else begin
				r_MK_block_row_counter     <=  r_MK_block_row_counter;
				r_MK_block_col_counter     <=  r_MK_block_col_counter;
				r_MK_read_row_counter      <=  r_MK_read_row_counter + 1'b1;
			end

		end else begin

			r_MK_block_row_counter     <=  r_MK_block_row_counter;
			r_MK_block_col_counter     <=  r_MK_block_col_counter;
			r_MK_read_row_counter      <=  r_MK_read_row_counter;

		end
	end


	// bitmap & pointer address
	wire    [LOG2_MEMD-1 : 0]    w_MK_bitmap_addr;
	assign  w_MK_bitmap_addr = (NUM_PEGS * r_MK_block_row_counter + r_MK_read_row_counter) * (K_DIM / NUM_PES) + r_MK_block_col_counter;


	/////////////////////////////////////////////////////////////////////////
	// 1st cycle
	// get bitmap, pointer and prefix
	/////////////////////////////////////////////////////////////////////////

	wire    [NUM_PES - 1 : 0]           w_MK_bitmap;
	wire    [POINTER_WIDTH - 1 : 0]     w_MK_pointer;

	bram_MK_bitmap my_bram_MK_bitmap (
		.clka(clk),
		.ena(ena & !w_MK_read_data_stall & !w_MK_write_data_stall & !w_fifo_MK_full),
		.wea(1'b0),
		.addra(w_MK_bitmap_addr),
		.dina('d0),
		.douta(w_MK_bitmap)
	);

	bram_MK_pointer my_bram_MK_pointer (
		.clka(clk),
		.ena(ena & !w_MK_read_data_stall & !w_MK_write_data_stall & !w_fifo_MK_full),
		.wea(1'b0),
		.addra(w_MK_bitmap_addr),
		.dina('d0),
		.douta(w_MK_pointer)
	);

	// get index by prefix-sum
	wire    [NUM_PES*(LOG2_PES+1)-1 : 0]   w_MK_pfx_dout;

	presum my_presum (
        .din(w_MK_bitmap), 
        .dout(w_MK_pfx_dout)
	);

	// shift pfx into a dense format
	wire    [NUM_PES*LOG2_PES-1 : 0]   w_MK_pfx_dout_dense;

	pfxdense my_pfxdense(
        .pfx(w_MK_pfx_dout),
        .pfx_dense(w_MK_pfx_dout_dense)
	);


	// ff
	reg             r_ena_ff1;
	reg [10 : 0]    r_MK_block_col_counter_ff1;
	reg [10 : 0]    r_MK_read_row_counter_ff1;

	always @(posedge clk) begin
		if(rst) begin
			r_ena_ff1                   <=  1'b0;
			r_MK_block_col_counter_ff1  <=  'd0;
			r_MK_read_row_counter_ff1   <=  'd0;
		end else if(ena & !w_MK_read_data_stall & !w_MK_write_data_stall & !w_fifo_MK_full) begin
			r_ena_ff1                   <=  ena;
			r_MK_block_col_counter_ff1  <=  r_MK_block_col_counter;
			r_MK_read_row_counter_ff1   <=  r_MK_read_row_counter;
		end else begin
			r_ena_ff1                   <=  r_ena_ff1;
			r_MK_block_col_counter_ff1  <=  r_MK_block_col_counter_ff1;
			r_MK_read_row_counter_ff1   <=  r_MK_read_row_counter_ff1;
		end
	end



	/////////////////////////////////////////////////////////////////////////
	// 2nd cycle
	// MK data address, idx, read stall
	/////////////////////////////////////////////////////////////////////////

	wire    [20 : 0]    w_MK_data_addr;
	wire    [10 : 0]    w_MK_data_idx_begin;
	wire    [10 : 0]    w_MK_data_idx_end;

	wire    [10 : 0]    w_MK_data_len;
	assign  w_MK_data_len = w_MK_pfx_dout[NUM_PES*(LOG2_PES+1)-1 -: (LOG2_PES+1)];

	load_data_addr # (
		.DATA_READ_WIDTH(MK_DATA_READ_WIDTH),
		.POINTER_WIDTH(POINTER_WIDTH))
		my_load_MK_data_addr (
			.clk(clk),
			.rst(rst),
			.ena(r_ena_ff1 & !w_MK_write_data_stall & !w_fifo_MK_full),
			.pointer(w_MK_pointer),
			.read_data_stall(w_MK_read_data_stall),

			.data_addr(w_MK_data_addr)
	);


	load_data_idx # (
		.DATA_READ_WIDTH(MK_DATA_READ_WIDTH),
		.POINTER_WIDTH(POINTER_WIDTH) )
		my_load_MK_data_idx(
			.clk(clk),
			.rst(rst),
			.ena(r_ena_ff1 & !w_MK_read_data_stall & !w_MK_write_data_stall & !w_fifo_MK_full),
			.pointer(w_MK_pointer),
			.data_len(w_MK_data_len),

			.data_idx_begin(w_MK_data_idx_begin),
			.data_idx_end(w_MK_data_idx_end)
	);


	load_read_data_stall # (
		.DATA_READ_WIDTH(MK_DATA_READ_WIDTH),
		.POINTER_WIDTH(POINTER_WIDTH) )
		my_load_MK_read_data_stall(
			.clk(clk),
			.rst(rst),
			.ena(r_ena_ff1 & !w_MK_write_data_stall & !w_fifo_MK_full),
			.pointer(w_MK_pointer),
			.data_len(w_MK_data_len),
			.read_data_stall_in(w_MK_read_data_stall),

			.read_data_stall_out(w_MK_read_data_stall)
	);

	// ff & pfx
	reg             r_ena_ff2;
	reg [10 : 0]    r_MK_block_col_counter_ff2;
	reg [10 : 0]    r_MK_read_row_counter_ff2;

	reg [NUM_PES*LOG2_PES-1 : 0]    r_MK_pfx_dout_dense;

	always @(posedge clk) begin
		if(rst) begin
			r_ena_ff2                   <=  1'b0;
			r_MK_block_col_counter_ff2  <=  'd0;
			r_MK_read_row_counter_ff2   <=  'd0;

			r_MK_pfx_dout_dense         <=  'd0;
		end else if(r_ena_ff1 & !w_MK_read_data_stall & !w_MK_write_data_stall & !w_fifo_MK_full) begin
			r_ena_ff2                   <=  r_ena_ff1;
			r_MK_block_col_counter_ff2  <=  r_MK_block_col_counter_ff1;
			r_MK_read_row_counter_ff2   <=  r_MK_read_row_counter_ff1;

			r_MK_pfx_dout_dense         <=  w_MK_pfx_dout_dense;
		end else begin
			r_ena_ff2                   <=  r_ena_ff2;
			r_MK_block_col_counter_ff2  <=  r_MK_block_col_counter_ff2;
			r_MK_read_row_counter_ff2   <=  r_MK_read_row_counter_ff2;

			r_MK_pfx_dout_dense         <=  r_MK_pfx_dout_dense;
		end
	end


	/////////////////////////////////////////////////////////////////////////
	// 3rd cycle
	// get data and data begin\end index
	/////////////////////////////////////////////////////////////////////////

	// if data cross 2 rows get corresponding begin & end
	wire    [10 : 0]    w_MK_data_read_begin;
	wire    [10 : 0]    w_MK_data_read_len;

	load_read_data_idx # (
		.DATA_READ_WIDTH(MK_DATA_READ_WIDTH) ) 
		my_load_MK_read_data_idx(
			.clk(clk),
			.rst(rst),
			.ena(r_ena_ff2 & !w_MK_write_data_stall & !w_fifo_MK_full),
			.read_data_stall(w_MK_read_data_stall),
			.data_idx_begin(w_MK_data_idx_begin),
			.data_idx_end(w_MK_data_idx_end),

			.data_read_begin(w_MK_data_read_begin),
			.data_read_len(w_MK_data_read_len)
	);


	// read data from RAM
	wire [MK_DATA_READ_WIDTH*DATA_TYPE-1 : 0] w_MK_data;
	bram_MK_data my_bram_MK_data (
		.clka(clk),
		.ena(r_ena_ff2 & !w_MK_write_data_stall & !w_fifo_MK_full),
		.wea(1'b0),
		.addra(w_MK_data_addr),
		.dina('d0),
		.douta(w_MK_data)
	);


	// ff
	reg             r_ena_ff3;
	reg [10 : 0]    r_MK_block_col_counter_ff3;
	reg [10 : 0]    r_MK_read_row_counter_ff3;
	reg [NUM_PES*LOG2_PES-1 : 0]    r_MK_pfx_dout_dense_ff1;
	reg             r_MK_read_data_stall;

	always @(posedge clk) begin
		if(rst) begin
			r_ena_ff3                       <=  1'b0;
			r_MK_block_col_counter_ff3      <=  'd0;
			r_MK_read_row_counter_ff3       <=  'd0;
			r_MK_pfx_dout_dense_ff1         <=  'd0;
			r_MK_read_data_stall            <=  1'b0;
		end else if(r_ena_ff2 & !w_MK_write_data_stall & !w_fifo_MK_full) begin
			r_ena_ff3                       <=  r_ena_ff2;
			r_MK_block_col_counter_ff3      <=  r_MK_block_col_counter_ff2;
			r_MK_read_row_counter_ff3       <=  r_MK_read_row_counter_ff2;
			r_MK_pfx_dout_dense_ff1         <=  r_MK_pfx_dout_dense;
			r_MK_read_data_stall            <=  w_MK_read_data_stall;
		end else begin
			r_ena_ff3                       <=  r_ena_ff3;
			r_MK_block_col_counter_ff3      <=  r_MK_block_col_counter_ff3;
			r_MK_read_row_counter_ff3       <=  r_MK_read_row_counter_ff3;
			r_MK_pfx_dout_dense_ff1         <=  r_MK_pfx_dout_dense_ff1;
			r_MK_read_data_stall            <=  r_MK_read_data_stall;
		end
	end


	/////////////////////////////////////////////////////////////////////////
	// 4th cycle
	// ping-pong bufffer used to read data into fifo
	/////////////////////////////////////////////////////////////////////////

	wire    [10 : 0]                            w_fifo_MK_write_counter;

	wire    [DATA_TYPE * NUM_PES - 1 : 0]    w_fifo_MK_write_data;
	wire    [DATA_TYPE * NUM_PES - 1 : 0]    w_fifo_MK_write_data_1;

	wire    [LOG2_PES * NUM_PES - 1 : 0]        w_fifo_write_dest;
	wire    [LOG2_PES * NUM_PES - 1 : 0]        w_fifo_write_dest_1;

	wire    [LOG2_PEGS * NUM_PES - 1 : 0]       w_fifo_write_vn;
	wire    [LOG2_PEGS * NUM_PES - 1 : 0]       w_fifo_write_vn_1;


	// special ff
	reg             r_MK_read_data_stall_ff1;
	reg [10 : 0]    r_MK_data_read_len;

	always @(posedge clk) begin
		if(rst) begin
			r_MK_read_data_stall_ff1    <=  1'b0;
			r_MK_data_read_len          <=  'd0;
		end else if(r_ena_ff3 & !w_MK_write_data_stall & !w_fifo_MK_full) begin
			r_MK_read_data_stall_ff1    <=  r_MK_read_data_stall;
			r_MK_data_read_len          <=  w_MK_data_read_len;
		end else begin
			r_MK_read_data_stall_ff1    <=  r_MK_read_data_stall_ff1;
			r_MK_data_read_len          <=  r_MK_data_read_len;
		end
	end

	load_MK_data_readfifo # (
		.NUM_PEGS(NUM_PEGS),
		.LOG2_PEGS(LOG2_PEGS),
		.NUM_PES(NUM_PES),
		.LOG2_PES(LOG2_PES), 
		.DATA_TYPE(DATA_TYPE))
		my_load_MK_data_readfifo (
			.clk(clk),
			.rst(rst),
			.ena(r_ena_ff3 & !w_MK_write_data_stall & !w_fifo_MK_full),
			.M_DIM(M_DIM),

			.MK_read_data_stall(r_MK_read_data_stall),
			.MK_read_data_stall_ff(r_MK_read_data_stall_ff1),
			.MK_read_row_counter(r_MK_read_row_counter_ff3),
			.MK_data_read_begin(w_MK_data_read_begin),
			.MK_data_read_len(w_MK_data_read_len),
			.MK_data_read_len_ff(r_MK_data_read_len),
			.MK_data(w_MK_data),
			.MK_pfx_dense(r_MK_pfx_dout_dense_ff1),

			.fifo_MK_write_counter(w_fifo_MK_write_counter),
			.fifo_MK_write_data(w_fifo_MK_write_data),
			.fifo_MK_write_data_1(w_fifo_MK_write_data_1),
			.fifo_write_dest(w_fifo_write_dest),
			.fifo_write_dest_1(w_fifo_write_dest_1),
			.fifo_write_vn(w_fifo_write_vn),
			.fifo_write_vn_1(w_fifo_write_vn_1)
	);

	// used to detect write if need to cross 2
	reg [10 : 0] r_fifo_MK_write_counter;
	always @(posedge clk) begin
		if(rst) begin
			r_fifo_MK_write_counter <= 6'd0;
		end else if(r_ena_ff3 & !w_MK_write_data_stall & !w_fifo_MK_full) begin
			r_fifo_MK_write_counter <= w_fifo_MK_write_counter;
		end else begin
			r_fifo_MK_write_counter <= r_fifo_MK_write_counter;
		end
	end

	// ff
	reg             r_ena_ff4;
	reg [10 : 0]    r_MK_read_row_counter_ff4;
	reg [10 : 0]    r_MK_block_col_counter_ff4;
	reg [10 : 0]    r_MK_read_row_counter_ff5;
	reg [10 : 0]    r_MK_block_col_counter_ff5;

	always @(posedge clk) begin
		if(rst) begin
			r_ena_ff4                   <=  1'b0;
			r_MK_block_col_counter_ff4  <=  'd0;
			r_MK_read_row_counter_ff4   <=  'd0;
			r_MK_read_row_counter_ff5   <=  'd0;
			r_MK_block_col_counter_ff5  <=  'd0;
		end else if(r_ena_ff3 & !w_MK_write_data_stall & !w_fifo_MK_full) begin
			r_ena_ff4                   <=  r_ena_ff3;
			r_MK_block_col_counter_ff4  <=  r_MK_block_col_counter_ff3;
			r_MK_read_row_counter_ff4   <=  r_MK_read_row_counter_ff3;
			r_MK_read_row_counter_ff5   <=  r_MK_read_row_counter_ff4;
			r_MK_block_col_counter_ff5  <=  r_MK_block_col_counter_ff4;
		end else begin
			r_ena_ff4                   <=  r_ena_ff4;
			r_MK_block_col_counter_ff4  <=  r_MK_block_col_counter_ff4;
			r_MK_read_row_counter_ff4   <=  r_MK_read_row_counter_ff4;
			r_MK_read_row_counter_ff5   <=  r_MK_read_row_counter_ff5;
			r_MK_block_col_counter_ff5  <=  r_MK_block_col_counter_ff5;
		end
	end



	/////////////////////////////////////////////////////////////////////////
	// 5th cycle
	// write into fifo
	/////////////////////////////////////////////////////////////////////////

	wire     [DATA_TYPE * NUM_PES - 1 : 0]      w_fifo_MK_data;
	wire     [LOG2_PES * NUM_PES - 1 : 0]       w_fifo_dest;
	wire     [LOG2_PEGS * NUM_PES - 1 : 0]      w_fifo_vn;
	wire     [1 : 0]                            w_fifo_flag;
	wire                                        w_fifo_MK_wr_en;

	load_MK_data_writefifo # (
		.NUM_PEGS(NUM_PEGS),
		.LOG2_PEGS(LOG2_PEGS),
		.NUM_PES(NUM_PES),
		.LOG2_PES(LOG2_PES), 
		.DATA_TYPE(DATA_TYPE))
		my_load_MK_data_writefifo(
			.clk(clk),
			.rst(rst),
			.ena(r_ena_ff4 & !w_fifo_MK_full),
			.MK_read_data_stall(r_MK_read_data_stall_ff1),
			.MK_write_data_stall_in(w_MK_write_data_stall),
			.M_DIM(M_DIM),
			.K_DIM(K_DIM),

			.MK_block_col_counter(r_MK_block_col_counter_ff4),
			.MK_block_col_counter_ff(r_MK_block_col_counter_ff5),
			.MK_read_row_counter(r_MK_read_row_counter_ff4),
			.MK_read_row_counter_ff(r_MK_read_row_counter_ff5),
			.fifo_MK_write_counter(w_fifo_MK_write_counter),
			.fifo_MK_write_counter_ff(r_fifo_MK_write_counter),
			.fifo_MK_write_data(w_fifo_MK_write_data),
			.fifo_MK_write_data_1(w_fifo_MK_write_data_1),
			.fifo_write_dest(w_fifo_write_dest),
			.fifo_write_dest_1(w_fifo_write_dest_1),
			.fifo_write_vn(w_fifo_write_vn),
			.fifo_write_vn_1(w_fifo_write_vn_1),

			.fifo_MK_data(w_fifo_MK_data),
			.fifo_dest(w_fifo_dest),
			.fifo_vn(w_fifo_vn),
			.fifo_flag(w_fifo_flag),
			.fifo_MK_wr_en(w_fifo_MK_wr_en),
			.MK_write_data_stall_out(w_MK_write_data_stall)
	);

	// wire                                        w_fifo_MK_rd_en;

	// wire     [DATA_TYPE * NUM_PES - 1 : 0]   w_fifo_MK_data_out;
	// wire                                        w_fifo_MK_data_full;
	// wire                                        w_fifo_MK_data_empty;

	// wire     [LOG2_PES * NUM_PES - 1 : 0]       w_fifo_dest_out;
	wire                                        w_fifo_dest_full;
	wire                                        w_fifo_dest_empty;

	// wire     [LOG2_PES * NUM_PES - 1 : 0]       w_fifo_vn_out;
	wire                                        w_fifo_vn_full;
	wire                                        w_fifo_vn_empty;

	fifo_MK_data my_fifo_MK_data (
		.clk(clk),
		.rst(rst),
		.din(w_fifo_MK_data),
		.wr_en(r_ena_ff4 & !w_fifo_MK_full & w_fifo_MK_wr_en),
		.rd_en(i_fifo_MK_rd_en & r_ena_ff4),
		.dout(o_fifo_MK_data_out),
		.full(w_fifo_MK_full),
		.empty(o_fifo_MK_empty)
	);


	fifo_dest my_fifo_dest (
		.clk(clk),
		.rst(rst),
		.din(w_fifo_dest),
		.wr_en(r_ena_ff4 & !w_fifo_MK_full & w_fifo_MK_wr_en),
		.rd_en(i_fifo_MK_rd_en & r_ena_ff4),
		.dout(o_fifo_dest_out),
		.full(w_fifo_dest_full),
		.empty(w_fifo_dest_empty)
	);


	fifo_vn my_fifo_vn (
		.clk(clk),
		.rst(rst),
		.din(w_fifo_vn),
		.wr_en(r_ena_ff4 & !w_fifo_MK_full & w_fifo_MK_wr_en),
		.rd_en(i_fifo_MK_rd_en & r_ena_ff4),
		.dout(o_fifo_vn_out),
		.full(w_fifo_vn_full),
		.empty(w_fifo_vn_empty)
	);


	// record the num_dpe for the next col block
	fifo_flag my_fifo_flag (
		.clk(clk),
		.rst(rst),
		.din(w_fifo_flag),
		.wr_en(r_ena_ff4 & !w_fifo_MK_full & w_fifo_MK_wr_en),
		.rd_en(i_fifo_MK_rd_en & r_ena_ff4),
		.dout(o_fifo_flag_out),
		.full(w_fifo_flag_full),
		.empty(w_fifo_flag_empty)
	);

endmodule

