
module buff_schedule # (
    parameter                                                       NUM_PEGS    = 8,
    parameter                                                       LOG2_PEGS   = 3,
    parameter                                                       NUM_PES     = 8,
    parameter                                                       LOG2_PES    = 3,
    parameter                                                       DATA_TYPE   = 8)(

    input                                                           clk,
    input                                                           rst,
    input               [20 : 0]                                    N_DIM,

    input                                                           i_MK_data_valid,
    input               [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]     i_MK_data_bus,      // 256-bit each
	input               [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]      i_MK_dest_bus,      // 160-bit
	input               [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     i_MK_vn_bus,        // 160-bit
    input               [NUM_PEGS -1 : 0]                           i_MK_add_bus,
    input               [NUM_PEGS * LOG2_PEGS - 1 : 0]              i_MK_block_vn,
    input               [1 : 0]                                     i_MK_accum_ena,

    input                                                           i_fifo_KN_data_empty,
    input               [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]     i_KN_data_bus,

    output      reg                                                 data_source,
    output                                                          KN_counter_ena,

    // output for pegs
    output      reg     [NUM_PEGS - 1 : 0]                          o_data_valid,       // each unit is 1-bit
    output      reg     [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]     o_data_bus,         // 256-bit each
	output      reg     [NUM_PEGS -1 : 0]                           o_stationary,       // 1-bit
	output      reg     [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]      o_dest_bus,         // 160-bit
	output      reg     [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     o_vn_seperator,     // 160-bit
    output      reg     [NUM_PEGS - 1 : 0]                          o_data_add,
    output      reg     [NUM_PEGS * LOG2_PEGS -1:0]                 o_block_vn,         // others: MK block vn
    output      reg     [1 : 0]                                     o_accum_ena,
    output      reg                                                 o_ctrl_en

    );


    wire    MK_is_read,     KN_is_read;
    assign  MK_is_read  =   data_source & i_MK_data_valid;
    assign  KN_is_read  =   !(data_source | data_source_ff | i_fifo_KN_data_empty);
    // assign  KN_is_read  =   !(data_source | i_fifo_KN_data_empty);


    reg     data_source_ff;
    always @(posedge clk) begin
        if(rst) begin
            data_source_ff <=  1'b0;
        end else begin
            data_source_ff <=  data_source;
        end
    end


    // KN_counter
    reg     [20 : 0]    KN_counter;         // count the colum of KN    
    
    always @(posedge clk) begin
        if(rst) begin
            KN_counter  <=  'd0;
        end else begin
            if(KN_is_read) begin
                if(KN_counter_ena) begin
                    KN_counter  <=  'd0;
                end else begin
                    KN_counter  <=  KN_counter + 1'b1;
                end
            end else begin
                KN_counter  <=  KN_counter;
            end
        end
    end

    // assign  KN_counter_ena = (KN_counter == N_DIM) ? 1'b1 : 1'b0;
    // assign  KN_counter_ena = (KN_counter == N_DIM - 1) ? 1'b1 : 1'b0;
    assign  KN_counter_ena = ((N_DIM != 1 && KN_counter == N_DIM - 1) || (N_DIM == 1 && KN_is_read)) ? 1'b1 : 1'b0;

    // data_source
    always @(posedge clk) begin
        if(rst) begin
            data_source     <=  1'b1;
        end else begin
            if( MK_is_read || (KN_is_read && !KN_counter_ena) ) begin
                data_source     <=  1'b0;
            end else if( KN_is_read && KN_counter_ena )  begin
                data_source     <=  1'b1;
            end else begin
                data_source     <=  data_source;
            end
        end
    end


    
    // outputs

    always @(posedge clk) begin
        if(rst) begin
            o_data_valid            <=      'd0;
            o_ctrl_en               <=      1'b0;
        end else begin
            if( MK_is_read || KN_is_read )begin
                // o_data_valid            <=      { 32{1'b1} };
                o_data_valid            <=      {(NUM_PEGS){1'b1}};
                o_ctrl_en               <=      1'b1;
            end else begin
                o_data_valid            <=      'd0;
                o_ctrl_en               <=      1'b0;
            end
        end
    end



    always @(posedge clk) begin
        if(rst) begin
            o_data_bus              <=      'd0;
            o_stationary            <=      'd0;
        end else begin
            if(MK_is_read) begin
                o_data_bus              <=      i_MK_data_bus;
                // o_stationary            <=      { 32{1'b1} };
                o_stationary            <=      {(NUM_PEGS){1'b1}};
            end else if(KN_is_read) begin
                o_data_bus              <=      i_KN_data_bus;
                // o_stationary            <=      { 32{1'b0} };
                o_stationary            <=      'd0;
            end else begin
                o_data_bus              <=      o_data_bus;
                o_stationary            <=      o_stationary;
            end
        end
    end



    always @(posedge clk) begin
        if(rst) begin
            o_dest_bus              <=      'd0;
            o_vn_seperator          <=      'd0;
            o_data_add              <=      'd0;
            o_block_vn              <=      'd0;
            o_accum_ena             <=      'd0;
        end else begin
            if(MK_is_read) begin
                o_dest_bus              <=      i_MK_dest_bus;
                o_vn_seperator          <=      i_MK_vn_bus;
                o_data_add              <=      i_MK_add_bus;
                o_block_vn              <=      i_MK_block_vn;
                o_accum_ena             <=      i_MK_accum_ena;
            end else begin
                o_dest_bus              <=      o_dest_bus;
                o_vn_seperator          <=      o_vn_seperator;
                o_data_add              <=      o_data_add;
                o_block_vn              <=      o_block_vn;
                o_accum_ena             <=      o_accum_ena;
            end
        end
    end

         

endmodule
