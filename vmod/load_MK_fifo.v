`timescale 1ns / 1ps

// module load_MK_fifo(

//     );
// endmodule

module load_MK_data_readfifo # (
    parameter                                               NUM_PEGS    =       32,
    parameter                                               LOG2_PEGS   =       5,
    parameter                                               NUM_PES     =       32,
    parameter                                               LOG2_PES    =       5,
    parameter                                               DATA_TYPE   =       8) (

    input                                                   clk,
    input                                                   rst,
    input                                                   ena,
    input               [20 : 0]                            M_DIM,

    input                                                   MK_read_data_stall,
    input                                                   MK_read_data_stall_ff,
    input               [10 : 0]                            MK_read_row_counter,
    input               [10 : 0]                            MK_data_read_begin,
    input               [10 : 0]                            MK_data_read_len,
    input               [10 : 0]                            MK_data_read_len_ff,
    input               [2 * NUM_PES * DATA_TYPE - 1 : 0]   MK_data,
    input               [NUM_PES*LOG2_PES-1 : 0]            MK_pfx_dense,

    output      reg     [10 : 0]                            fifo_MK_write_counter,

    output      reg     [DATA_TYPE * NUM_PES - 1 : 0]       fifo_MK_write_data,
    output      reg     [DATA_TYPE * NUM_PES - 1 : 0]       fifo_MK_write_data_1,

    output      reg     [LOG2_PES * NUM_PES - 1 : 0]        fifo_write_dest,
    output      reg     [LOG2_PES * NUM_PES - 1 : 0]        fifo_write_dest_1,

    output      reg     [LOG2_PEGS * NUM_PES - 1 : 0]       fifo_write_vn,
    output      reg     [LOG2_PEGS * NUM_PES - 1 : 0]       fifo_write_vn_1
    );


    wire                MK_read_blk_end_ena;
    assign  MK_read_blk_end_ena = (MK_read_row_counter == NUM_PEGS - 1 && !MK_read_data_stall) ? 1'b1 : 1'b0;
    
    wire    [10 : 0]    fifo_MK_write_len;
    assign  fifo_MK_write_len   =   fifo_MK_write_counter + MK_data_read_len;

    wire    [10 : 0]    fifo_MK_write_end;
    assign  fifo_MK_write_end   =   fifo_MK_write_len % (2*NUM_PES);

    reg     [NUM_PES -1 : 0]    cond1,  cond2,  cond3,  cond4,  cond5,  cond6;
    genvar i;
    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin: cond_gen
            always @(*) begin
                cond1[i]    =   (fifo_MK_write_counter <= i)            ?   1'b1 : 1'b0;
                cond2[i]    =   (i < fifo_MK_write_len)                 ?   1'b1 : 1'b0;   
                cond3[i]    =   (2*NUM_PES < fifo_MK_write_len)         ?   1'b1 : 1'b0;
                cond4[i]    =   (i < fifo_MK_write_end)                 ?   1'b1 : 1'b0;
                cond5[i]    =   (fifo_MK_write_counter <= i + NUM_PES)  ?   1'b1 : 1'b0;
                cond6[i]    =   (i + NUM_PES < fifo_MK_write_len)       ?   1'b1 : 1'b0;
            end
        end
    endgenerate
    // assign  cond1     =   (fifo_MK_write_counter <= i)            ?   1'b1 : 1'b0;
    // assign  cond2     =   (i < fifo_MK_write_len)                 ?   1'b1 : 1'b0;   
    // assign  cond3     =   (2*NUM_PES < fifo_MK_write_len)         ?   1'b1 : 1'b0;
    // assign  cond4     =   (i < fifo_MK_write_end)                 ?   1'b1 : 1'b0;
    // assign  cond5     =   (fifo_MK_write_counter <= i + NUM_PES)  ?   1'b1 : 1'b0;
    // assign  cond6     =   (i + NUM_PES < fifo_MK_write_len)       ?   1'b1 : 1'b0;



    // counter
    always @(posedge clk) begin
        if(rst == 1'b1) begin
            fifo_MK_write_counter <= 'd0;
        end else if(ena) begin
            // if(MK_read_row_counter == M_DIM - 1 && MK_read_data_stall != 1'b1) begin
            if(MK_read_blk_end_ena) begin
                if((fifo_MK_write_len - 1) % (2*NUM_PES) < NUM_PES) begin
                    fifo_MK_write_counter <= NUM_PES;
                end else begin
                    fifo_MK_write_counter <= 'd0;
                end

            end else begin
                fifo_MK_write_counter <= fifo_MK_write_end;
            end
        end else begin
            fifo_MK_write_counter <= fifo_MK_write_counter;
        end
    end



    // x_case
    reg     [10*NUM_PES-1 : 0]    fifo_data_case;
    reg     [10*NUM_PES-1 : 0]    fifo_dest_case;
    
    // genvar i;
    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin
            always @(*) begin

                fifo_data_case[i*10 +: 10]  =   'd0;
                fifo_dest_case[i*10 +: 10]  =   'd0;

                if(cond1[i] && cond2[i]) begin
                    fifo_data_case[i*10 +: 10]  =   i - fifo_MK_write_counter + MK_data_read_begin;

                    if(MK_read_data_stall_ff) begin
                        fifo_dest_case[i*10 +: 10]  =   i - fifo_MK_write_counter + MK_data_read_len_ff;
                    end else begin
                        fifo_dest_case[i*10 +: 10]  =   i - fifo_MK_write_counter;
                    end
                end else if(cond3[i] && cond4[i]) begin
                    fifo_data_case[i*10 +: 10]  =   i - fifo_MK_write_counter + MK_data_read_begin + 2*NUM_PES;

                    if(MK_read_data_stall_ff) begin
                        fifo_dest_case[i*10 +: 10]  =   i - fifo_MK_write_counter  + MK_data_read_len_ff + 2*NUM_PES;
                    end else begin
                        fifo_dest_case[i*10 +: 10]  =   i - fifo_MK_write_counter + 2*NUM_PES;
                    end

                end
            end
        end
    endgenerate


    // x / filling / keep: fifo_data, fifo_dest
    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin
            always @(posedge clk) begin
                if(rst) begin
                    fifo_MK_write_data[i*DATA_TYPE +: DATA_TYPE] <= 'd0;
                    fifo_write_dest[i*LOG2_PES +: LOG2_PES] <= 'd0;
                end else if(ena && ((cond1[i] && cond2[i]) || (cond3[i] && cond4[i]))) begin
                    // x
                    // write to fifo_data     
                    fifo_MK_write_data[i*DATA_TYPE +: DATA_TYPE] <= MK_data[fifo_data_case[i*10 +: 10]*(DATA_TYPE) +: DATA_TYPE];

                    // write to fifo_dest
                    fifo_write_dest[i*LOG2_PES +: LOG2_PES] <= MK_pfx_dense[fifo_dest_case[i*10 +: 10]*LOG2_PES +: LOG2_PES];
                    
                end else if(ena && MK_read_blk_end_ena && (cond1[i] || cond3[i])) begin
                    // filling
                    fifo_MK_write_data[i*DATA_TYPE +: DATA_TYPE] <= 'd0;
                    fifo_write_dest[i*LOG2_PES +: LOG2_PES] <= NUM_PES-1;
                end else begin
                    // keep
                    fifo_MK_write_data[i*DATA_TYPE +: DATA_TYPE] <= fifo_MK_write_data[i*DATA_TYPE +: DATA_TYPE];
                    fifo_write_dest[i*LOG2_PES +: LOG2_PES] <= fifo_write_dest[i*LOG2_PES +: LOG2_PES];
                end
            end
        end
    endgenerate


    // x / filling / keep: fifo_vn
    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin
            always @(posedge clk) begin
                if(rst) begin
                    fifo_write_vn[i*LOG2_PEGS +: LOG2_PEGS] <= 'd0;
                end else if( ena && ( (cond1[i] && (cond2[i] || MK_read_blk_end_ena)) || (cond3[i] && (cond4[i] || MK_read_blk_end_ena)) ) ) begin
                    // x & filling
                    fifo_write_vn[i*LOG2_PEGS +: LOG2_PEGS] <= MK_read_row_counter;
                end else begin
                    // keep
                    fifo_write_vn[i*LOG2_PEGS +: LOG2_PEGS] <= fifo_write_vn[i*LOG2_PEGS +: LOG2_PEGS];
                end
            end
        end
    endgenerate






    // x_case
    reg     [10*NUM_PES-1 : 0]    fifo_data1_case;
    reg     [10*NUM_PES-1 : 0]    fifo_dest1_case;
    
    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin
            always @(*) begin

                fifo_data1_case[i*10 +: 10]  =   'd0;
                fifo_dest1_case[i*10 +: 10]  =   'd0;

                if(cond5[i] && cond6[i]) begin
                    fifo_data1_case[i*10 +: 10]  =   i + NUM_PES + MK_data_read_begin - fifo_MK_write_counter;

                    if(MK_read_data_stall_ff) begin
                        fifo_dest1_case[i*10 +: 10]  =   i + NUM_PES + MK_data_read_len_ff - fifo_MK_write_counter;
                    end else begin
                        fifo_dest1_case[i*10 +: 10]  =   i + NUM_PES - fifo_MK_write_counter;
                    end
                end
            end
        end
    endgenerate


    // fifo_1
    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin
            always @(posedge clk) begin
                if(rst == 1'b1) begin
                    fifo_MK_write_data_1[i*DATA_TYPE +: DATA_TYPE] <= 'd0;
                    fifo_write_dest_1[i*LOG2_PES +: LOG2_PES] <= 'd0;
                end else if(ena && cond5[i] && cond6[i]) begin
                    // x
                    // write to fifo_data        
                    fifo_MK_write_data_1[i*DATA_TYPE +: DATA_TYPE] <= MK_data[fifo_data1_case[i*10 +: 10]*DATA_TYPE +: DATA_TYPE];     

                    // write to fifo_dest
                    fifo_write_dest_1[i*LOG2_PES +: LOG2_PES] <= MK_pfx_dense[fifo_dest1_case[i*10 +: 10]*LOG2_PES +: LOG2_PES];
                    
                end else if(ena && MK_read_blk_end_ena && cond5[i]) begin
                    // filling
                    fifo_MK_write_data_1[i*DATA_TYPE +: DATA_TYPE] <= 8'd0;
                    fifo_write_dest_1[i*LOG2_PES +: LOG2_PES] <= NUM_PES-1;
                end else begin
                    // keep
                    fifo_MK_write_data_1[i*DATA_TYPE +: DATA_TYPE] <= fifo_MK_write_data_1[i*DATA_TYPE +: DATA_TYPE];
                    fifo_write_dest_1[i*LOG2_PES +: LOG2_PES] <= fifo_write_dest_1[i*LOG2_PES +: LOG2_PES];
                end
            end
        end
    endgenerate

    generate
        for(i = 0; i < NUM_PES; i = i + 1) begin
            always @(posedge clk) begin
                if(rst) begin
                    fifo_write_vn_1[i*LOG2_PEGS +: LOG2_PEGS] <= 'd0;
                end else if(ena && cond5[i] && (cond6[i] || MK_read_blk_end_ena)) begin
                    fifo_write_vn_1[i*LOG2_PEGS +: LOG2_PEGS] <= MK_read_row_counter;
                end else begin
                    fifo_write_vn_1[i*LOG2_PEGS +: LOG2_PEGS] <= fifo_write_vn_1[i*LOG2_PEGS +: LOG2_PEGS];
                end
            end
        end
    endgenerate


endmodule






module load_MK_data_writefifo # (
    parameter                                               NUM_PEGS    =       32,
    parameter                                               LOG2_PEGS   =       5,
    parameter                                               NUM_PES     =       32,
    parameter                                               LOG2_PES    =       5,
    parameter                                               DATA_TYPE   =       8) (

    input                                                   clk,
    input                                                   rst,
    input                                                   ena,
    input               [20 : 0]                            M_DIM,
    input               [20 : 0]                            K_DIM,

    input                                                   MK_read_data_stall,
    input                                                   MK_write_data_stall_in,

    input               [10 : 0]                            MK_block_col_counter,
    input               [10 : 0]                            MK_block_col_counter_ff,
    input               [10 : 0]                            MK_read_row_counter,
    input               [10 : 0]                            MK_read_row_counter_ff,
    input               [10 : 0]                            fifo_MK_write_counter,
    input               [10 : 0]                            fifo_MK_write_counter_ff,
    input               [DATA_TYPE * NUM_PES - 1 : 0]       fifo_MK_write_data,
    input               [DATA_TYPE * NUM_PES - 1 : 0]       fifo_MK_write_data_1,
    input               [LOG2_PES * NUM_PES - 1 : 0]        fifo_write_dest,
    input               [LOG2_PES * NUM_PES - 1 : 0]        fifo_write_dest_1,
    input               [LOG2_PEGS * NUM_PES - 1 : 0]       fifo_write_vn,
    input               [LOG2_PEGS * NUM_PES - 1 : 0]       fifo_write_vn_1,

    output      reg     [DATA_TYPE * NUM_PES - 1 : 0]       fifo_MK_data,
    output      reg     [LOG2_PES * NUM_PES - 1 : 0]        fifo_dest,
    output      reg     [LOG2_PEGS * NUM_PES - 1 : 0]       fifo_vn,
    output      reg     [1 : 0]                             fifo_flag,
    output      reg                                         fifo_MK_wr_en,
    output      reg                                         MK_write_data_stall_out
    );


    // from fifo_reg to real FIFO
    always @(posedge clk) begin
        if(rst == 1'b1) begin
            fifo_MK_data <= 'd0;
            fifo_dest <= 'd0;
            fifo_vn <= 'd0;
            fifo_flag <= 2'b00;
            fifo_MK_wr_en <= 1'b0;
            MK_write_data_stall_out <= 1'b0;
        end
        else if(ena) begin

            // write twice
            if(MK_write_data_stall_in) begin

                if(fifo_MK_write_counter_ff == 'd0) begin
                    fifo_MK_data <= fifo_MK_write_data_1;
                    fifo_dest <= fifo_write_dest_1;
                    fifo_vn <= fifo_write_vn_1;
                    fifo_MK_wr_en <= 1'b1;
                end else if(fifo_MK_write_counter_ff == NUM_PES) begin
                    fifo_MK_data <= fifo_MK_write_data;
                    fifo_dest <= fifo_write_dest;
                    fifo_vn <= fifo_write_vn;
                    fifo_MK_wr_en <= 1'b1;
                end

                if(MK_read_row_counter_ff == NUM_PEGS - 1) begin
                    if(MK_block_col_counter_ff == K_DIM / NUM_PES - 1) begin
                        fifo_flag <= 2'b11;
                    end else begin
                        fifo_flag <= 2'b10;
                    end
                end else begin
                    fifo_flag <= 2'b00;
                end

                MK_write_data_stall_out <= 1'b0;
 
            end else begin

                // fill the fifo_reg with 0 cause a block is finished
                if(MK_read_row_counter == NUM_PEGS - 1 && MK_read_data_stall != 1'b1) begin
                    // fill all by 0
                    if(fifo_MK_write_counter == fifo_MK_write_counter_ff) begin
                        fifo_MK_data <= 'd0;
                        fifo_dest <= {(LOG2_PES*NUM_PES){1'b1}};
                        fifo_vn <= {(LOG2_PEGS*NUM_PES){1'b1}};
                        // fifo_flag <= 2'b00;
                        fifo_MK_wr_en <= 1'b1;
                        MK_write_data_stall_out <= 1'b0;
                        if(MK_block_col_counter == K_DIM / NUM_PES - 1) begin
                            fifo_flag <= 2'b11;
                        end else begin
                            fifo_flag <= 2'b10;
                        end
                    end
                    // cross 2 regs need stall to load in FIFO
                    else if(fifo_MK_write_counter == 'd0 && fifo_MK_write_counter_ff < NUM_PES) begin
                        fifo_MK_data <= fifo_MK_write_data;
                        fifo_dest <= fifo_write_dest;
                        fifo_vn <= fifo_write_vn;
                        fifo_flag <= 2'b01;
                        fifo_MK_wr_en <= 1'b1;
                        MK_write_data_stall_out <= 1'b1;
                    end else if(fifo_MK_write_counter == NUM_PES && NUM_PES <= fifo_MK_write_counter_ff) begin
                        fifo_MK_data <= fifo_MK_write_data_1;
                        fifo_dest <= fifo_write_dest_1;
                        fifo_vn <= fifo_write_vn_1;
                        fifo_flag <= 2'b01;
                        fifo_MK_wr_en <= 1'b1;
                        MK_write_data_stall_out <= 1'b1;
                    end
                    // load in FIFO directly
                    else begin
                        if(fifo_MK_write_counter_ff < NUM_PES) begin
                            fifo_MK_data <= fifo_MK_write_data;
                            fifo_dest <= fifo_write_dest;
                            fifo_vn <= fifo_write_vn;
                            fifo_MK_wr_en <= 1'b1;
                            MK_write_data_stall_out <= 1'b0;
                        end else begin
                            fifo_MK_data <= fifo_MK_write_data_1;
                            fifo_dest <= fifo_write_dest_1;
                            fifo_vn <= fifo_write_vn_1;
                            fifo_MK_wr_en <= 1'b1;
                            MK_write_data_stall_out <= 1'b0;
                        end

                        if(MK_block_col_counter == K_DIM / NUM_PES - 1) begin
                            fifo_flag <= 2'b11;
                        end else begin
                            fifo_flag <= 2'b10;
                        end
                    end

                // normally
                end else begin 
                    if(fifo_MK_write_counter_ff < NUM_PES && NUM_PES <= fifo_MK_write_counter) begin
                        fifo_MK_data <= fifo_MK_write_data;
                        fifo_dest <= fifo_write_dest;
                        fifo_vn <= fifo_write_vn;
                        fifo_MK_wr_en <= 1'b1;
                        if(fifo_MK_write_counter == NUM_PES && MK_read_data_stall != 1'b1) begin
                            fifo_flag <= 2'b00;
                        end else begin
                            fifo_flag <= 2'b01;
                        end
                    end
                    else if(NUM_PES <= fifo_MK_write_counter_ff && fifo_MK_write_counter < NUM_PES) begin
                        fifo_MK_data <= fifo_MK_write_data_1;
                        fifo_dest <= fifo_write_dest_1;
                        fifo_vn <= fifo_write_vn_1;
                        fifo_MK_wr_en <= 1'b1;
                        if(fifo_MK_write_counter == 'd0 && MK_read_data_stall != 1'b1) begin
                            fifo_flag <= 2'b00;
                        end else begin
                            fifo_flag <= 2'b01;
                        end
                    end
                    else begin
                        fifo_MK_data <= fifo_MK_data;
                        fifo_dest <= fifo_dest;
                        fifo_vn <= fifo_vn;
                        fifo_flag <= 2'b00;
                        fifo_MK_wr_en <= 1'b0;
                    end
                    MK_write_data_stall_out <= 1'b0;
                end

            end

        end else begin
            fifo_MK_data <= fifo_MK_data;
            fifo_dest <= fifo_dest;
            fifo_vn <= fifo_vn;
            fifo_flag <= fifo_flag;
            fifo_MK_wr_en <= fifo_MK_wr_en;
            MK_write_data_stall_out <= MK_write_data_stall_out;
        end
    end


endmodule