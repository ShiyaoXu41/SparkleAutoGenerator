`timescale 1ns / 1ps

// module load_data(

//     );
// endmodule

/////////////////////////////////////////////////////////////////////////

//  data address

/////////////////////////////////////////////////////////////////////////

module load_data_addr # (
    parameter   DATA_READ_WIDTH =   32,
    parameter   POINTER_WIDTH   =   30)(

    input                                   clk,
    input                                   rst,
    input                                   ena,
    input       [POINTER_WIDTH - 1 : 0]     pointer,             // 18-bit width
    input                                   read_data_stall,

    output  reg [20 : 0]                    data_addr            // 16-bit width
    );
    
    //  data address
    always @(posedge clk) begin
        if(rst == 1'b1) begin
            data_addr <= 'd0;
        end else if(ena) begin
            // insert bubble, if data read need 2 cycles
            if(read_data_stall) begin
                data_addr <= data_addr + 1'b1;
            end
            else begin
                data_addr <= (pointer / DATA_READ_WIDTH);     // data width is double NUM_PES
            end
        end else begin
            data_addr <= data_addr;
        end
    end

endmodule





/////////////////////////////////////////////////////////////////////////

//  data address

/////////////////////////////////////////////////////////////////////////

module load_data_idx # (
    parameter                               DATA_READ_WIDTH =   32,
    parameter                               POINTER_WIDTH   =   30) (

    input                                   clk,
    input                                   rst,
    input                                   ena,
    input       [POINTER_WIDTH - 1 : 0]     pointer,
    input       [10 : 0]                    data_len,

    output  reg [10 : 0]                    data_idx_begin,
    output  reg [10 : 0]                    data_idx_end
    );


    // reg to keep valid_data_begin/end value
    always @(posedge clk) begin
        if(rst == 1'b1) begin
            data_idx_begin   <=  'd0;
            data_idx_end     <=  'd0;
        end else if(ena) begin
            data_idx_begin   <=  pointer % DATA_READ_WIDTH;
            data_idx_end     <=  pointer % DATA_READ_WIDTH + data_len;
        end else begin
            data_idx_begin   <=  data_idx_begin;
            data_idx_end     <=  data_idx_end;
        end
    end


endmodule



/////////////////////////////////////////////////////////////////////////

//  read data stall

/////////////////////////////////////////////////////////////////////////

module load_read_data_stall # (
    parameter                               DATA_READ_WIDTH =   32,
    parameter                               POINTER_WIDTH   =   30) (

    input                                   clk,
    input                                   rst,
    input                                   ena,
    input       [POINTER_WIDTH - 1 : 0]     pointer,
    input       [10 : 0]                    data_len,
    input                                   read_data_stall_in,

    output  reg                             read_data_stall_out
    );

    always @(posedge clk) begin
        if(rst == 1'b1) begin
            read_data_stall_out <= 1'b0;
        end else if(ena) begin

            if(read_data_stall_in) begin  // stall only to keep one cycle
                read_data_stall_out <= 1'b0;
            end else if(pointer % DATA_READ_WIDTH + data_len > DATA_READ_WIDTH) begin
                read_data_stall_out <= 1'b1;
            end else begin
                read_data_stall_out <= 1'b0;
            end

        end else begin
            read_data_stall_out <= read_data_stall_out;
        end
    end


endmodule


/////////////////////////////////////////////////////////////////////////

//  data index

/////////////////////////////////////////////////////////////////////////

module load_read_data_idx # (
    parameter               DATA_READ_WIDTH =   32) (

    input                   clk,
    input                   rst,
    input                   ena,
    input                   read_data_stall,
    input       [10 : 0]    data_idx_begin,
    input       [10 : 0]    data_idx_end,

    output  reg [10 : 0]    data_read_begin,
    output  reg [10 : 0]    data_read_len
    );

    wire        data_idx_end_ena;
    assign      data_idx_end_ena    =   (data_idx_end > DATA_READ_WIDTH) ? 1'b1 : 1'b0;

    always @(posedge clk) begin
        if(rst) begin
            data_read_begin <= 'd0;
        end else if(ena) begin
            if(!read_data_stall && data_idx_end_ena) begin
                data_read_begin  <= 'd0;
            end else begin
                data_read_begin  <= data_idx_begin;
            end
        end else begin
            data_read_begin     <=  data_read_begin;
        end
    end


    always @(posedge clk) begin
        if(rst) begin
            data_read_len <= 'd0;
        end
        else if(ena) begin
            if(data_idx_end_ena) begin
                if(read_data_stall) begin
                    data_read_len    <= DATA_READ_WIDTH - data_idx_begin;
                end else begin
                    data_read_len    <= data_idx_end - DATA_READ_WIDTH;
                end
            end else begin
                data_read_len    <= data_idx_end - data_idx_begin;
            end

        end else begin
            data_read_len    <= data_read_len;
        end
    end

    // always @(posedge clk) begin
    //     if(rst == 1'b1) begin
    //         data_read_begin <= 'd0;
    //         data_read_len <= 'd0;
    //     end
    //     else if(ena) begin
    //         if(data_idx_end > DATA_READ_WIDTH) begin
    //             if(read_data_stall) begin
    //                 data_read_begin  <= data_idx_begin;
    //                 data_read_len    <= DATA_READ_WIDTH - data_idx_begin;
    //             end else begin
    //                 data_read_begin  <= 'd0;
    //                 data_read_len    <= data_idx_end - DATA_READ_WIDTH;
    //             end
    //         end else begin
    //             data_read_begin  <= data_idx_begin;
    //             data_read_len    <= data_idx_end - data_idx_begin;
    //         end

    //     end else begin
    //         data_read_begin  <= data_read_begin;
    //         data_read_len    <= data_read_len;
    //     end
    // end


endmodule
