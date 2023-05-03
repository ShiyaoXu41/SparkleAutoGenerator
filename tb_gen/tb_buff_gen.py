# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_buff.sv", mode = 'w')


f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_buff.sv\n")
f.write("// Parameterization: NUM_PES, PARA_BLOCKS, LOG2_MEMD, DATA_TYPE\n")
f.write("// Description: Testbench for buff_MK, buff_KN_32, buff_schedule vmod\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_buff ();\n\n")

f.write("\t// 1. parameters\n")
f.write("\tparameter DATA_TYPE = " + str(IN_DATA_TYPE) + ";\n")
f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ";\n")
f.write("\tparameter LOG2_PEGS = " + str(LOG2_PEGS) + ";\n")
f.write("\tparameter NUM_PES = " + str(NUM_PES) + ";\n")
f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + ";\n")
f.write("\tparameter LOG2_MEMD = " + str(LOG2_MEMD) + ";\n")
f.write("\tparameter PARA_BLOCKS = " + str(PARA_BLOCKS) + ";\n")
f.write("\tparameter LOG2_PARA_BLOCKS = " + str(LOG2_PARA_BLOCKS) + ";\n")
f.write("\tparameter POINTER_WIDTH = " + str(POINTER_WIDTH) + ";\n\n\n\n")



f.write("\t// 2. general inputs\n")
f.write("\treg clk = 0;\n")
f.write("\treg rst = 0;\n")
f.write("\treg ena = 0;\n\n")

f.write("\t// Generate simulation clock\n")
f.write("\talways #1 clk = !clk;\n\n")

f.write("\t// set reset signal\n")
f.write("\tinitial begin\n")
f.write("\t\trst = 1'b1;\n")
f.write("\t\tena = 1'b0;\n")
f.write("\t\t#4\n")
f.write("\t\trst = 1'b0;\n")
f.write("\t\t#196\n")
f.write("\t\tena = 1'b1;\n")
f.write("\tend\n\n")

f.write("\t// dimensions of MK&KN\n")
f.write("\treg     [20 : 0]      M_DIM     =   'd" + str(M_DIM) + ";\n")
f.write("\treg     [20 : 0]      K_DIM     =   'd" + str(K_DIM) + ";\n")
f.write("\treg     [20 : 0]      K_PAD     =   'd" + str(K_PAD) + ";\n")
f.write("\treg     [20 : 0]      N_DIM     =   'd" + str(N_DIM) + ";\n\n\n\n")



f.write("\t// 3. inputs of each\n")
f.write("\t// inputs of buff_MK\n")
f.write("\twire    [DATA_TYPE * NUM_PES - 1 : 0]    			    w_fifo_MK_data_out;\n")
f.write("\twire    [LOG2_PES * NUM_PES - 1 : 0]        			w_fifo_dest_out;\n")
f.write("\twire    [LOG2_PEGS * NUM_PES - 1 : 0]       			w_fifo_vn_out;\n")
f.write("\twire    [1 : 0]                             			w_fifo_flag_out;\n")
f.write("\twire                                        			w_fifo_MK_empty;\n\n")

f.write("\t// inputs of buff_KN \n")
f.write("\twire    [PARA_BLOCKS * DATA_TYPE * NUM_PES - 1 : 0]     w_fifo_KN_data_out;\n")
f.write("\twire                                                    w_fifo_KN_data_empty;	// inputs of buff_schedule\n\n")

f.write("\t// inputs of buff_MK/KN, while outputs of buff_schedule\n")
f.write("\twire                                                	data_source;        // 1 is from MK, 0 is from KN\n")
f.write("\twire    												KN_counter_ena;\n\n\n\n")



f.write("\t// 4. outputs\n")
f.write("\t// outputs of buff_MK\n")
f.write("\twire    [LOG2_PARA_BLOCKS : 0]                          w_block_counter;\n")
f.write("\twire    [LOG2_PEGS * (PARA_BLOCKS + 1) - 1: 0]          w_peg_num_counter;\n")
f.write("\twire    [1 : 0]                                     	w_backup_fifo_ena;\n\n")

f.write("\twire                                                	w_MK_data_valid;    // inputs of buff_schedule\n")
f.write("\twire                                                 	w_fifo_MK_rd_en;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]  	    w_MK_data_bus;      // " + str(NUM_PES*IN_DATA_TYPE) + "-bit each\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]      	w_MK_dest_bus;      // " + str(NUM_PES*LOG2_PES) + "-bit\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     	w_MK_vn_bus;        // " + str(NUM_PES*LOG2_PEGS) + "-bit\n")
f.write("\twire    [NUM_PEGS -1 : 0]                           	w_MK_add_bus;\n")
f.write("\twire    [NUM_PEGS * LOG2_PEGS - 1 : 0]                  w_MK_block_vn;      // MK block vn seperators\n")
f.write("\twire    [1 : 0]                                         w_MK_accum_ena;\n\n")

f.write("\t// outputs of buff_KN\n")
f.write("\twire    [PARA_BLOCKS-1 : 0]                       		w_fifo_KN_rd_en;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]  	    w_KN_data_bus;		// inputs of buff_schedule\n\n")

f.write("\t// outputs of buff_schedule\n")
f.write("\twire    [NUM_PEGS - 1 : 0]                          	o_data_valid;   // each unit is 1-bit\n")
f.write("\twire    [NUM_PEGS * NUM_PES * DATA_TYPE -1 : 0]  	    o_data_bus;     // " + str(NUM_PES*IN_DATA_TYPE) + "-bit each\n")
f.write("\twire    [NUM_PEGS -1 : 0]                           	o_stationary;   // 1-bit\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]      	o_dest_bus;     // " + str(NUM_PES*LOG2_PES) + "-bit\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     	o_vn_seperator; // " + str(NUM_PES*LOG2_PEGS) + "-bit\n")
f.write("\twire    [NUM_PEGS - 1 : 0]                          	o_data_add;\n")
f.write("\twire    [NUM_PEGS * LOG2_PEGS -1:0]                 	o_block_vn;\n")
f.write("\twire                                                	o_ctrl_en;\n\n\n\n")



f.write("\t// 5. instantiate DUT\n")
f.write("\t// 5.1 load mods\n")
f.write("\tload_MK # (\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),             // block_size is default as same as NUM_PES\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.LOG2_MEMD(LOG2_MEMD),\n")
f.write("\t\t.POINTER_WIDTH(POINTER_WIDTH)) \n")
f.write("\t\tmy_load_MK (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n")
f.write("\t\t\t.M_DIM(M_DIM),\n")
f.write("\t\t\t.K_DIM(K_DIM),\n\n")

f.write("\t\t\t.i_fifo_MK_rd_en(w_fifo_MK_rd_en),\n\n")

f.write("\t\t\t.o_fifo_MK_data_out(w_fifo_MK_data_out),\n")
f.write("\t\t\t.o_fifo_dest_out(w_fifo_dest_out),\n")
f.write("\t\t\t.o_fifo_vn_out(w_fifo_vn_out),\n")
f.write("\t\t\t.o_fifo_flag_out(w_fifo_flag_out),\n\n")

f.write("\t\t\t.o_fifo_MK_empty(w_fifo_MK_empty)\n")
f.write("\t);\n\n")

f.write("\tload_KN # (\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS))\n")
f.write("\t\tmy_load_KN (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n")
f.write("\t\t\t.M_DIM(M_DIM),\n")
f.write("\t\t\t.K_DIM(K_DIM),\n")
f.write("\t\t\t.K_PAD(K_PAD),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.i_fifo_KN_rd_en(w_fifo_KN_rd_en),\n\n")

f.write("\t\t\t.o_fifo_KN_data_out(w_fifo_KN_data_out),\n")
f.write("\t\t\t.o_fifo_KN_data_empty(w_fifo_KN_data_empty)\n")
f.write("\t);\n\n\n")


f.write("\t// 5.2 buff mods\n")
f.write("\tbuff_MK # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS) ) \n")
f.write("\t\tmy_buff_MK (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.M_DIM(M_DIM),\n\n")

f.write("\t\t\t.i_fifo_MK_data_out(w_fifo_MK_data_out),\n")
f.write("\t\t\t.i_fifo_dest_out(w_fifo_dest_out),\n")
f.write("\t\t\t.i_fifo_vn_out(w_fifo_vn_out),\n")
f.write("\t\t\t.i_fifo_flag_out(w_fifo_flag_out),\n")
f.write("\t\t\t.i_fifo_MK_empty(w_fifo_MK_empty),\n\n")

f.write("\t\t\t.data_source(data_source),\n\n")

f.write("\t\t\t// output\n")
f.write("\t\t\t.MK_data_valid(w_MK_data_valid),\n")
f.write("\t\t\t.fifo_MK_rd_en(w_fifo_MK_rd_en),\n\n")

f.write("\t\t\t.o_block_counter(w_block_counter),\n")
f.write("\t\t\t.o_peg_num_counter(w_peg_num_counter),\n")
f.write("\t\t\t.o_backup_fifo_ena(w_backup_fifo_ena),\n\n")

f.write("\t\t\t.o_MK_data_bus(w_MK_data_bus),  	// " + str(NUM_PES*IN_DATA_TYPE) + "-bit each\n")
f.write("\t\t\t.o_MK_dest_bus(w_MK_dest_bus),  	// " + str(NUM_PES*LOG2_PES) + "-bit\n")
f.write("\t\t\t.o_MK_vn_bus(w_MK_vn_bus),      	// " + str(NUM_PES*LOG2_PEGS) + "-bit\n")
f.write("\t\t\t.o_MK_add_bus(w_MK_add_bus),\n")
f.write("\t\t\t.o_MK_block_vn(w_MK_block_vn),   	// MK block vn seperators\n")
f.write("\t\t\t.o_MK_accum_ena(w_MK_accum_ena)\n")
f.write("\t);\n\n")

f.write("\tbuff_KN # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS) )\n")
f.write("\t\tmy_buff_KN (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n\n")

f.write("\t\t\t.i_fifo_KN_data_out(w_fifo_KN_data_out),\n")
f.write("\t\t\t.i_fifo_KN_data_empty(w_fifo_KN_data_empty),\n\n")

f.write("\t\t\t.i_backup_fifo_ena(w_backup_fifo_ena),\n")
f.write("\t\t\t.i_block_counter(w_block_counter),\n")
f.write("\t\t\t.i_peg_num_counter(w_peg_num_counter),\n\n")

f.write("\t\t\t.data_source(data_source),\n")
f.write("\t\t\t.KN_counter_ena(KN_counter_ena),\n\n")
			
f.write("\t\t\t// outputs\n")
f.write("\t\t\t.o_KN_data_bus(w_KN_data_bus),\n")
f.write("\t\t\t.o_fifo_KN_rd_en(w_fifo_KN_rd_en)\n")
f.write("\t);\n\n")

f.write("\tbuff_schedule # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE) )\n")
f.write("\t\tmy_buff_schedule (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.i_MK_data_valid(w_MK_data_valid),\n")
f.write("\t\t\t.i_MK_data_bus(w_MK_data_bus),\n")
f.write("\t\t\t.i_MK_dest_bus(w_MK_dest_bus),\n")
f.write("\t\t\t.i_MK_vn_bus(w_MK_vn_bus),\n")
f.write("\t\t\t.i_MK_add_bus(w_MK_add_bus),\n")
f.write("\t\t\t.i_MK_block_vn(w_MK_block_vn),\n")
f.write("\t\t\t.i_MK_accum_ena(w_MK_accum_ena),\n\n")

f.write("\t\t\t.i_fifo_KN_data_empty(w_fifo_KN_data_empty),\n")
f.write("\t\t\t.i_KN_data_bus(w_KN_data_bus),\n\n")

f.write("\t\t\t// outputs\n")
f.write("\t\t\t.data_source(data_source),\n")
f.write("\t\t\t.KN_counter_ena(KN_counter_ena),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),		// each unit is 1-bit\n")
f.write("\t\t\t.o_data_bus(o_data_bus),			// " + str(NUM_PES*IN_DATA_TYPE) + "-bit each\n")
f.write("\t\t\t.o_stationary(o_stationary),		// 1-bit\n")
f.write("\t\t\t.o_dest_bus(o_dest_bus),			// " + str(NUM_PES*LOG2_PES) + "-bit\n")
f.write("\t\t\t.o_vn_seperator(o_vn_seperator),	// " + str(NUM_PES*LOG2_PEGS) + "-bit\n")
f.write("\t\t\t.o_data_add(o_data_add),\n")
f.write("\t\t\t.o_block_vn(o_block_vn),			// others: MK block vn\n")
f.write("\t\t\t.o_ctrl_en(o_ctrl_en)\n")
f.write("\t);\n\n\n")


f.write("\t// 6. results save in files\n")
f.write("\tinteger data, stationary, dest, row_vn, add, block_vn;\n")
f.write("\tinitial begin\n")
f.write("\t\tdata = $fopen(\"tb_buff_data.txt\",\"w\");\n")
f.write("\t\tstationary = $fopen(\"tb_buff_stationary.txt\",\"w\");\n")
f.write("\t\tdest = $fopen(\"tb_buff_dest.txt\",\"w\");\n")
f.write("\t\trow_vn = $fopen(\"tb_buff_row_vn.txt\",\"w\");\n")
f.write("\t\tadd = $fopen(\"tb_buff_add.txt\",\"w\");\n")
f.write("\t\tblock_vn = $fopen(\"tb_buff_block_vn.txt\",\"w\");\n")
f.write("\t\t#1000000000 $finish;\n")
f.write("\tend\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_buff_schedule.o_ctrl_en != 1'b0 && my_buff_schedule.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(data, \"%h\\n\", my_buff_schedule.o_data_bus);\n")
f.write("\t\t\t$fwrite(stationary, \"%h\\n\", my_buff_schedule.o_stationary);\n")
f.write("\t\t\t$fwrite(dest, \"%h\\n\", my_buff_schedule.o_dest_bus);\n")
f.write("\t\t\t$fwrite(row_vn, \"%h\\n\", my_buff_schedule.o_vn_seperator);\n")
f.write("\t\t\t$fwrite(add, \"%h\\n\", my_buff_schedule.o_data_add);\n")
f.write("\t\t\t$fwrite(block_vn, \"%h\\n\", my_buff_schedule.o_block_vn);\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("endmodule\n")