module buff_MK # (
    parameter                                                           NUM_PEGS        = 8,
    parameter                                                           LOG2_PEGS       = 3,
    parameter                                                           NUM_PES         = 8,
    parameter                                                           LOG2_PES        = 3,
    parameter                                                           DATA_TYPE       = 8,
    parameter                                                           PARA_BLOCKS     = 5,
    parameter                                                           LOG2_PARA_BLOCKS= 3)(
             
    input                                                               clk,
    input                                                               rst,
    input               [20 : 0]                                        M_DIM,   

    input               [DATA_TYPE * NUM_PES - 1 : 0]                   i_fifo_MK_data_out,
    input               [LOG2_PES * NUM_PES - 1 : 0]                    i_fifo_dest_out,
    input               [LOG2_PEGS * NUM_PES - 1 : 0]                   i_fifo_vn_out,
    input               [1 : 0]                                         i_fifo_flag_out,
    input                                                               i_fifo_MK_empty,

    input                                                               data_source,


    output      reg                                                     MK_data_valid,              // if MK data is ready
    output                                                              fifo_MK_rd_en,


    output      reg     [LOG2_PARA_BLOCKS : 0]                          o_block_counter,
    output      reg     [LOG2_PEGS * (PARA_BLOCKS + 1) - 1: 0]          o_peg_num_counter,
    output      reg     [1 : 0]                                         o_backup_fifo_ena,

    // regs store MK data
    output      reg     [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]         o_MK_data_bus,              
	output      reg     [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]          o_MK_dest_bus,              
	output      reg     [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]         o_MK_vn_bus,                
    output      reg     [NUM_PEGS -1 : 0]                               o_MK_add_bus,
    output      reg     [NUM_PEGS * LOG2_PEGS - 1 : 0]                  o_MK_block_vn,              // MK block vn seperators
    output      reg     [1 : 0]                                         o_MK_accum_ena
    );



    // ====================== output some control signals ======================

    reg                                                 block_overflow;

    // when MK_data_valid == 0 && block_overflow == 0 then the rd_en = 1
    assign fifo_MK_rd_en = !(MK_data_valid | block_overflow);

    // need to ff and output of the module
    reg     [LOG2_PARA_BLOCKS : 0]                      block_counter;
    reg     [LOG2_PEGS * (PARA_BLOCKS + 1) - 1: 0]      peg_num_counter;
    reg     [1 : 0]                                     backup_fifo_ena;


    // count the num of peg
    reg     [LOG2_PEGS-1 : 0]                           MK_counter;
    // MK read finished
    reg     [10 : 0]                                    MK_block_row_counter;

    wire    [LOG2_PEGS-1 : 0]                           w_block_vn;
    assign  w_block_vn  =   MK_block_row_counter % NUM_PEGS;


    // some analyzing conditions
    wire    read_MK,    get_MK,     fill_MK;
    assign  read_MK =   data_source     &&  MK_data_valid;
    assign  get_MK  =   fifo_MK_rd_en   &&  !i_fifo_MK_empty;
    assign  fill_MK =   !MK_data_valid  &&  block_overflow;

    wire    block_counter_ena,      MK_block_row_counter_ena,   MK_counter_ena;
    assign  block_counter_ena           =   (block_counter < PARA_BLOCKS + backup_fifo_ena[1] - 1) ? 1'b1 : 1'b0;
    assign  MK_block_row_counter_ena    =   (MK_block_row_counter == M_DIM / NUM_PEGS - 1) ? 1'b1 : 1'b0;
    assign  MK_counter_ena              =   (MK_counter == NUM_PEGS - 1) ? 1'b1 : 1'b0;



    // MK_data_valid
    always @(posedge clk) begin
        if(rst) begin
            MK_data_valid   <=  1'b0;
        end else begin
            if((get_MK | fill_MK) & MK_counter_ena) begin
                MK_data_valid   <=  1'b1;
            end else if(read_MK | ((get_MK | fill_MK) & !MK_counter_ena)) begin
                MK_data_valid   <=  1'b0;
            end else begin    
                MK_data_valid   <=  MK_data_valid;
            end
        end
    end


    // block_overflow
    always @(posedge clk) begin
        if(rst) begin
            block_overflow          <=  1'b0;
        end else begin
            if( read_MK | (get_MK & i_fifo_flag_out[1] & block_counter_ena & (!i_fifo_flag_out[0] | (i_fifo_flag_out[0] & !MK_block_row_counter_ena))) ) begin
                block_overflow          <=  1'b0;
            // end else if(get_MK && i_fifo_flag_out[1] && (!i_fifo_flag_out[0] && !block_counter_ena) || (i_fifo_flag_out[0] && MK_block_row_counter_ena) || (i_fifo_flag_out[0] && !MK_block_row_counter_ena && !block_counter_ena)) begin
            end else if( get_MK & i_fifo_flag_out[1] & (!block_counter_ena | (i_fifo_flag_out[0] & MK_block_row_counter_ena)) ) begin
                block_overflow          <=  1'b1;
            end else begin
                block_overflow          <=  block_overflow;
            end
        end
    end


    // peg_num_counter
    genvar i;
    generate
        for(i = 0; i < PARA_BLOCKS+1; i = i + 1) begin: peg_num_counter_gen
        
            always @(posedge clk) begin
                if(rst) begin
                    peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  NUM_PEGS - 1;
                end else begin
                    // read MK to output
                    if(read_MK) begin
                        peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  NUM_PEGS - 1;
                    end else if(get_MK & i_fifo_flag_out[1] & (!i_fifo_flag_out[0] | (i_fifo_flag_out[0] & !MK_block_row_counter_ena)) & (block_counter == i)) begin
                        peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  MK_counter;
                        // case(block_counter)
                        //     'd0: peg_num_counter[4 : 0]      <=  MK_counter;
                        //     'd1: peg_num_counter[9 : 5]      <=  MK_counter;
                        //     'd2: peg_num_counter[14 : 10]    <=  MK_counter;
                        //     'd3: peg_num_counter[19 : 15]    <=  MK_counter;
                        //     'd4: peg_num_counter[24 : 20]    <=  MK_counter;
                        // endcase
                    end else begin
                        peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS];
                    end
                end
                end
        end
    endgenerate



    // block_counter
    always @(posedge clk) begin
        if(rst) begin
            block_counter   <=  'd0;
        end else begin
            if(read_MK) begin
                block_counter   <=  'd0;
            end else if( get_MK & i_fifo_flag_out[1] & block_counter_ena & !MK_counter_ena & (!i_fifo_flag_out[0] | (i_fifo_flag_out[0] & !MK_block_row_counter_ena)) )begin
                block_counter   <=  block_counter + 1'b1;
            end else begin
                block_counter   <=  block_counter;
            end
        end
    end


    // backup_fifo_ena
    always @(posedge clk) begin
        if(rst) begin
            backup_fifo_ena     <=  2'b00;
        end else begin

            if(read_MK) begin
                backup_fifo_ena     <=  {backup_fifo_ena[0], 1'b0};
            end else if(MK_counter_ena & ((get_MK & i_fifo_flag_out[1]) | fill_MK)) begin
                backup_fifo_ena     <=  {backup_fifo_ena[1], 1'b0};
            end else if(MK_counter_ena & get_MK & !i_fifo_flag_out[1]) begin
                backup_fifo_ena     <=  {backup_fifo_ena[1], 1'b1};
            end else begin     
                backup_fifo_ena     <=  backup_fifo_ena;
            end
        end
    end


    // MK_counter
    always @(posedge clk) begin
        if(rst) begin
            MK_counter      <=  'd0;
        end else begin
            if(read_MK) begin
                MK_counter      <=  'd0;
            end else if(get_MK | fill_MK) begin
                MK_counter      <=  MK_counter + 1'b1;
            end else begin
                MK_counter      <=  MK_counter;
            end
        end
    end


    // MK_block_row_counter
    always @(posedge clk) begin
        if(rst) begin
            MK_block_row_counter    <=  'd0;
        end else begin
            if(get_MK & i_fifo_flag_out == 2'b11) begin
                if(MK_block_row_counter_ena) begin
                    MK_block_row_counter <= 'd0;
                end else begin
                    MK_block_row_counter <= MK_block_row_counter + 1'b1;
                end
            end else begin
                MK_block_row_counter    <=  MK_block_row_counter;
            end

        end
    end




    // output ff
    generate
        for(i = 0; i < PARA_BLOCKS+1; i = i + 1) begin: o_peg_num_counter_gen
            always @(posedge clk) begin
                if(rst) begin
                    o_peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  NUM_PEGS - 1;
                end else begin
                    // read MK to output
                    if(read_MK) begin
                        o_peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS];
                    end else begin
                        o_peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS]   <=  o_peg_num_counter[i*LOG2_PEGS +: LOG2_PEGS];
                    end
                end
            end
        end
    endgenerate
    always @(posedge clk) begin
        if(rst) begin
            o_block_counter     <=  'd0;
            o_backup_fifo_ena   <=  'd0;
        end else begin
            // read MK to output
            if(read_MK) begin
                o_block_counter     <=  block_counter;
                o_backup_fifo_ena   <=  backup_fifo_ena;
            end else begin
                o_block_counter     <=  o_block_counter;
                o_backup_fifo_ena   <=  o_backup_fifo_ena;
            end
        end
    end
    

    
    // ===================== output data =====================
    wire    w_add_bit;
    assign  w_add_bit = (i_fifo_flag_out == 2'b01) ? 1'b1 : 1'b0;

    always @(posedge clk) begin
        if(rst) begin
            o_MK_data_bus   <= 'd0;
            o_MK_dest_bus   <= 'd0;
            o_MK_vn_bus     <= 'd0;
            o_MK_add_bus    <= 'd0;

        end else begin

            // read MK data from FIFO
            if(get_MK) begin
                o_MK_data_bus[MK_counter*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)]    <=  i_fifo_MK_data_out;
                o_MK_dest_bus[MK_counter*(NUM_PES*LOG2_PES) +: (NUM_PES*LOG2_PES)]      <=  i_fifo_dest_out;
                o_MK_vn_bus[MK_counter*(NUM_PES*LOG2_PEGS) +: (NUM_PES*LOG2_PEGS)]      <=  i_fifo_vn_out;
                // o_MK_add_bus[MK_counter]    <=  (MK_counter == NUM_PEGS-1) ? 1'b0 : w_add_bit;
                o_MK_add_bus[MK_counter]    <=  (MK_counter_ena) ? 1'b0 : w_add_bit;

            // fill zero: block_overflow
            end else if(fill_MK) begin

                o_MK_data_bus[MK_counter*(NUM_PES*DATA_TYPE) +: (NUM_PES*DATA_TYPE)]    <=  'd0;
                o_MK_dest_bus[MK_counter*(NUM_PES*LOG2_PES) +: (NUM_PES*LOG2_PES)]      <=  'd0;
                o_MK_vn_bus[MK_counter*(NUM_PES*LOG2_PEGS) +: (NUM_PES*LOG2_PEGS)]      <=  'd0;
                o_MK_add_bus[MK_counter]                                                <=  1'b0;

            // ready to read MK to output
            end else begin
                o_MK_data_bus   <=  o_MK_data_bus;
                o_MK_dest_bus   <=  o_MK_dest_bus;
                o_MK_vn_bus     <=  o_MK_vn_bus;
                o_MK_add_bus    <=  o_MK_add_bus;
            end
        end
    end


    // o_MK_block_vn
    always @(posedge clk) begin
        if(rst) begin
            o_MK_block_vn             <=  'd0;
        end else begin
            if(get_MK) begin
                o_MK_block_vn[MK_counter*LOG2_PEGS +: LOG2_PEGS] <=  w_block_vn;
            end else if(fill_MK) begin
                o_MK_block_vn[MK_counter*LOG2_PEGS +: LOG2_PEGS] <=  o_MK_block_vn[(MK_counter-1)*LOG2_PEGS +: LOG2_PEGS];
            // if(get_MK | fill_MK) begin
            //     o_MK_block_vn[MK_counter*LOG2_PEGS +: LOG2_PEGS] <=  w_block_vn;
            end else begin
                o_MK_block_vn             <=  o_MK_block_vn;
            end
        end
    end

    // ff
    reg                 fill_MK_ff;
    reg     [1 : 0]     r_fifo_flag_out_ff;
    always @(posedge clk) begin
        if(rst) begin
            fill_MK_ff  <= 1'b0;
            r_fifo_flag_out_ff <= 'd0;
        end else begin
            fill_MK_ff  <=  fill_MK;
            r_fifo_flag_out_ff  <=  i_fifo_flag_out;
        end
    end

    // o_MK_accum_ena
    always @(posedge clk) begin
        if(rst) begin
            o_MK_accum_ena          <=  'd0;
        end else begin
            // if((get_MK | fill_MK) & MK_counter_ena) begin
            //     // means the end of a block 
            //     if(i_fifo_flag_out == 2'b11) begin
            //         o_MK_accum_ena <= {1'b0, o_MK_accum_ena[1]};
            //     end else begin
            //         o_MK_accum_ena <= {1'b1, o_MK_accum_ena[1]};
            //     end
                
            if(get_MK & MK_counter_ena) begin
                if(i_fifo_flag_out == 2'b11) begin
                    o_MK_accum_ena <= {1'b0, o_MK_accum_ena[1]};
                end else begin
                    o_MK_accum_ena <= {1'b1, o_MK_accum_ena[1]};
                end
            end else if(!fill_MK_ff & fill_MK) begin
                if(r_fifo_flag_out_ff == 2'b11) begin
                    o_MK_accum_ena <= {1'b0, o_MK_accum_ena[1]};
                end else begin
                    o_MK_accum_ena <= {1'b1, o_MK_accum_ena[1]};
                end
            end else begin
                o_MK_accum_ena      <=  o_MK_accum_ena;
            end
        end
    end

endmodule
