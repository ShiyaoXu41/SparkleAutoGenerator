# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
if not os.path.exists(root_path + "\\vmod"):
    os.makedirs(root_path + "\\vmod")

source_path = os.getcwd() + "\\vmod\\"
target_path = root_path + "\\vmod\\"



# ============= 2. copy some vmods directly ============
from shutil import copyfile
copyfile(source_path + "load_data_units.v", target_path + "load_data_units.v")
copyfile(source_path + "load_MK_fifo.v", target_path + "load_MK_fifo.v")
copyfile(source_path + "buff_MK.v", target_path + "buff_MK.v")
copyfile(source_path + "buff_schedule.v", target_path + "buff_schedule.v")
copyfile(source_path + "xbar.v", target_path + "xbar.v")
copyfile(source_path + "mult_gen.v", target_path + "mult_gen.v")
copyfile(source_path + "reduction_mux.v", target_path + "reduction_mux.v")


# ================== 3. generate vmod ==================
# ======================================================
f = open(target_path + "top.v", mode = 'w')


f.write("/////////////////////////////////////////////////////////////////////////\n")
f.write("// Design: top.v\n")
f.write("// Description: the top module for Sparkle in parameterization\n")
f.write("/////////////////////////////////////////////////////////////////////////\n\n\n")


f.write("module top # (\n")
f.write("\tparameter   NUM_PEGS            =   " + str(NUM_PEGS) + ",\n")
f.write("\tparameter   LOG2_PEGS           =   " + str(LOG2_PEGS) + ",\n\n")

f.write("\tparameter   NUM_PES             =   " + str(NUM_PES) + ",\n")
f.write("\tparameter   LOG2_PES            =   " + str(LOG2_PES) + ",\n\n")

f.write("\tparameter   IN_DATA_TYPE        =   " + str(IN_DATA_TYPE) + ",\n")
f.write("\tparameter   OUT_DATA_TYPE       =   " + str(OUT_DATA_TYPE) + ",\n\n")

f.write("\tparameter   PARA_BLOCKS         =   " + str(PARA_BLOCKS) + ",\n")
f.write("\tparameter   LOG2_PARA_BLOCKS    =   " + str(LOG2_PARA_BLOCKS) + ",\n\n")

f.write("\tparameter   POINTER_WIDTH       =   " + str(POINTER_WIDTH) + ",\n")
f.write("\tparameter   LOG2_MEMD           =   " + str(LOG2_MEMD) + ",\n\n")

f.write("\tparameter   MAX_N_DIM           =   " + str(MAX_N_DIM) + " )(\n\n")

f.write("\t// input                                       clk_in,\n")
f.write("\tinput                                       clk_out,\n")
f.write("\tinput                                       rst,\n")
f.write("\tinput                                       ena,\n")
f.write("\tinput       [20 : 0]                        M_DIM,\n")
f.write("\tinput       [20 : 0]                        K_DIM,\n")
f.write("\tinput       [20 : 0]                        K_PAD,\n")
f.write("\tinput       [20 : 0]                        N_DIM,\n\n")

f.write("\toutput                                      o_data_valid,\n")
f.write("\toutput      [NUM_PEGS*OUT_DATA_TYPE-1:0]    o_data_bus\n")
f.write(");\n\n\n\n")



f.write("/*\n")
f.write("\twire clk_out;\n")
f.write("\tcreate_clock clock\n")
f.write("\t(\n")
f.write("\t\t// Clock out ports\n")
f.write("\t\t.clk_in1(clk_in),           // output clk_in1\n")
f.write("\t\t// Status and control signals\n")
f.write("\t\t.reset(rst), // input reset\n")
f.write("\t\t// Clock in ports\n")
f.write("\t\t.clk_out1(clk_out)          // input clk_out1\n")
f.write("\t);\n")
f.write("*/\n\n\n\n")



f.write("\t// ======================= 1 load =======================\n\n")

f.write("\t// ======================= 1.1 load MK\n")
f.write("\twire                                                 	w_fifo_MK_rd_en;\n\n")

f.write("\twire    [IN_DATA_TYPE * NUM_PES - 1 : 0]    		    w_fifo_MK_data_out;\n")
f.write("\twire    [LOG2_PES * NUM_PES - 1 : 0]        			w_fifo_dest_out;\n")
f.write("\twire    [LOG2_PEGS * NUM_PES - 1 : 0]       			w_fifo_vn_out;\n")
f.write("\twire    [1 : 0]                             			w_fifo_flag_out;\n\n")

f.write("\twire                                        			w_fifo_MK_empty;\n\n")

f.write("\tload_MK # (\n")
f.write("\t\t.DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),             // block_size is default as same as NUM_PES\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.LOG2_MEMD(LOG2_MEMD),\n")
f.write("\t\t.POINTER_WIDTH(POINTER_WIDTH))\n")
f.write("\t\tmy_load_MK (\n")
f.write("\t\t\t.clk(clk_out),\n")
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
f.write("\t);\n\n\n")


f.write("\t// ======================= 1.2 load KN\n")
f.write("\twire    [PARA_BLOCKS-1 : 0]                       		w_fifo_KN_rd_en;\n\n")

f.write("\twire    [PARA_BLOCKS * IN_DATA_TYPE * NUM_PES - 1 : 0]  w_fifo_KN_data_out;\n")
f.write("\twire                                                    w_fifo_KN_data_empty;\n\n")

f.write("\tload_KN # (\n")
f.write("\t\t.DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS))\n")
f.write("\t\tmy_load_KN (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n")
f.write("\t\t\t.M_DIM(M_DIM),\n")
f.write("\t\t\t.K_DIM(K_DIM),\n")
f.write("\t\t\t.K_PAD(K_PAD),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.i_fifo_KN_rd_en(w_fifo_KN_rd_en),\n\n")

f.write("\t\t\t.o_fifo_KN_data_out(w_fifo_KN_data_out),\n")
f.write("\t\t\t.o_fifo_KN_data_empty(w_fifo_KN_data_empty)\n")
f.write("\t);\n\n\n\n")



f.write("\t// ======================= 2 buff =======================\n\n")

f.write("\t// ======================= 2.1 buff MK\n")
f.write("\twire                                                	data_source;        // 1 is from MK, 0 is from KN\n\n")

f.write("\twire                                                	w_MK_data_valid;\n\n")
    
f.write("\twire    [LOG2_PARA_BLOCKS : 0]                          w_block_counter;\n")
f.write("\twire    [LOG2_PEGS * (PARA_BLOCKS + 1) - 1: 0]          w_peg_num_counter;\n")
f.write("\twire    [1 : 0]                                     	w_backup_fifo_ena;\n\n")

f.write("\twire    [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0]      w_MK_data_bus;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]      	w_MK_dest_bus;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     	w_MK_vn_bus;\n")
f.write("\twire    [NUM_PEGS -1 : 0]                           	w_MK_add_bus;\n")
f.write("\twire    [NUM_PEGS * LOG2_PEGS - 1 : 0]              	w_MK_block_vn;      // MK block vn seperators\n")
f.write("\twire    [1 : 0]                                         w_MK_accum_ena;\n\n")

f.write("\tbuff_MK # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS) ) \n")
f.write("\t\tmy_buff_MK (\n")
f.write("\t\t\t.clk(clk_out),\n")
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

f.write("\t\t\t.o_MK_data_bus(w_MK_data_bus),\n")
f.write("\t\t\t.o_MK_dest_bus(w_MK_dest_bus),\n")
f.write("\t\t\t.o_MK_vn_bus(w_MK_vn_bus),\n")
f.write("\t\t\t.o_MK_add_bus(w_MK_add_bus),\n")
f.write("\t\t\t.o_MK_block_vn(w_MK_block_vn),   	// MK block vn seperators\n")
f.write("\t\t\t.o_MK_accum_ena(w_MK_accum_ena)\n")
f.write("\t);\n\n\n")


f.write("\t// ======================= 2.2 buff KN\n")
f.write("\twire    												KN_counter_ena;\n\n")

f.write("\twire    [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0]      w_KN_data_bus;\n\n")

f.write("\tbuff_KN # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS))\n")
f.write("\t\tmy_buff_KN (\n")
f.write("\t\t\t.clk(clk_out),\n")
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
f.write("\t);\n\n\n")


f.write("\t// ======================= 2.3 buff schedule\n")
f.write("\twire    [NUM_PEGS - 1 : 0]                          	w_data_valid;   // each unit is 1-bit\n")
f.write("\twire    [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0]      w_data_bus;\n")
f.write("\twire    [NUM_PEGS -1 : 0]                           	w_stationary;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]      	w_dest_bus;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]         w_vn_seperator;\n")
f.write("\twire    [NUM_PEGS - 1 : 0]                          	w_data_add;\n")
f.write("\twire    [NUM_PEGS * LOG2_PEGS -1:0]                 	w_block_vn;\n")
f.write("\twire    [1 : 0]                                         w_accum_ena;\n")
f.write("\twire                                                	w_ctrl_en;\n\n")

f.write("\tbuff_schedule # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.DATA_TYPE(IN_DATA_TYPE) )\n")
f.write("\t\tmy_buff_schedule (\n")
f.write("\t\t\t.clk(clk_out),\n")
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

f.write("\t\t\t.o_data_valid(w_data_valid),		// each unit is 1-bit\n")
f.write("\t\t\t.o_data_bus(w_data_bus),\n")
f.write("\t\t\t.o_stationary(w_stationary),\n")
f.write("\t\t\t.o_dest_bus(w_dest_bus),\n")
f.write("\t\t\t.o_vn_seperator(w_vn_seperator),\n\n")

f.write("\t\t\t.o_data_add(w_data_add),\n")
f.write("\t\t\t.o_block_vn(w_block_vn),\n")
f.write("\t\t\t.o_accum_ena(w_accum_ena),\n")
f.write("\t\t\t.o_ctrl_en(w_ctrl_en)\n")
f.write("\t);\n\n\n\n")



f.write("\t// ======================= 3 peg =======================\n\n")

f.write("\twire    [NUM_PEGS - 1 : 0]                              w_in_data_valid;\n")
f.write("\tassign  w_in_data_valid = w_ctrl_en ? w_data_valid : 'd0;\n\n")

f.write("\treg     [NUM_PES * LOG2_PES -1 : 0]                     dest_default = 0;\n")
f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 1; i < NUM_PES; i = i + 1) begin\n")
f.write("\t\t\talways @(*) begin\n")
f.write("\t\t\t\tdest_default[i*LOG2_PES +: LOG2_PES] = dest_default[(i-1)*LOG2_PES +: LOG2_PES] + 'd1;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]          w_in_dest_bus;\n")
f.write("\tassign  w_in_dest_bus = (w_stationary == 'd0) ? w_dest_bus : { (NUM_PEGS){dest_default}};\n\n\n")

f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PES -1 : 0]          w_in_vn_seperator;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS * NUM_PES; i = i + 1) begin\n")
f.write("\t\t\tassign w_in_vn_seperator[i*LOG2_PES +: LOG2_PES] = w_vn_seperator[i*LOG2_PEGS +: LOG2_PEGS];\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

f.write("\twire    [NUM_PEGS*NUM_PES-1:0]                          w_data_valid_0;\n")
f.write("\twire    [NUM_PEGS*NUM_PES*OUT_DATA_TYPE -1 : 0]         w_data_bus_0;\n\n")

f.write("\t// " + str(7+LOG2_PES) + " cycles\n")
f.write("\tpe_group # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.IN_DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.OUT_DATA_TYPE(OUT_DATA_TYPE))\n")
f.write("\t\tmy_peg (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n\n")

f.write("\t\t\t.i_data_valid(w_in_data_valid),\n")
f.write("\t\t\t.i_data_bus(w_data_bus),\n")
f.write("\t\t\t.i_stationary(w_stationary),\n")
f.write("\t\t\t.i_dest_bus(w_in_dest_bus), \n")
f.write("\t\t\t.i_vn_seperator(w_in_vn_seperator),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid_0),\n")
f.write("\t\t\t.o_data_bus(w_data_bus_0)\n")
f.write("\t);\n\n\n\n")



f.write("\t// ======================= 4 mid =======================\n")
f.write("\t// input for lvl0\n")
f.write("\t// ff  w_data_add   " + str(7+LOG2_PES) + " cycles\n")
f.write("\treg     [" + str(7+LOG2_PES) + "*NUM_PEGS-1 : 0]     r_data_add_ff;\n")
f.write("\tinteger j;\n")
f.write("\talways @(posedge clk_out) begin\n")
f.write("\t\tfor(j = 0; j < " + str(7+LOG2_PES) + "; j = j + 1) begin\n")
f.write("\t\t\tif(rst) begin\n")
f.write("\t\t\t\tr_data_add_ff[j*NUM_PEGS +: NUM_PEGS]   <=  'd0;\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\tif(j == 0) begin\n")
f.write("\t\t\t\t\tr_data_add_ff[j*NUM_PEGS +: NUM_PEGS]   <=  w_data_add;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_data_add_ff[j*NUM_PEGS +: NUM_PEGS]   <=  r_data_add_ff[(j-1)*NUM_PEGS +: NUM_PEGS];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\twire    [NUM_PEGS-1 : 0]        w_data_add_0;\n")
f.write("\tassign  w_data_add_0 = r_data_add_ff[" + str(6+LOG2_PES) + "*NUM_PEGS +: NUM_PEGS];\n\n")

f.write("\t// output for lvl0\n")
f.write("\twire    [NUM_PEGS * NUM_PES -1:0]                       w_data_valid_1;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * OUT_DATA_TYPE - 1 : 0]    w_data_bus_1;\n")
f.write("\twire    [OUT_DATA_TYPE - 1 : 0]                         w_data_temp;\n\n\n")


f.write("\t// 3 cycles\n")
f.write("\tmiddle_reduct_lvl0 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(OUT_DATA_TYPE))\n")
f.write("\t\tmy_mid_reduct_lvl0 (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n\n")

f.write("\t\t\t.i_data_add(w_data_add_0),\n")
f.write("\t\t\t.i_data_valid(w_data_valid_0),\n")
f.write("\t\t\t.i_data_bus(w_data_bus_0),\n")
f.write("\t\t\t.i_data_temp(w_data_temp),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid_1),\n")
f.write("\t\t\t.o_data_bus(w_data_bus_1),\n")
f.write("\t\t\t.o_data_temp(w_data_temp)\n")
f.write("\t);\n\n\n")


f.write("\t// input for lvl1\n")
f.write("\t// ff  r_vn (" + str(7+LOG2_PES) + "+3) cycles\n")
f.write("\treg     [" + str(10+LOG2_PES) + " * NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]      r_vn_ff;  // limited in 0 to NUM_PES, LOG2_PES size\n")
f.write("\talways @(posedge clk_out) begin\n")
f.write("\t\tfor(j = 0; j < " + str(10+LOG2_PES) + "; j = j + 1) begin\n")
f.write("\t\t\tif(rst) begin\n")
f.write("\t\t\t\tr_vn_ff[j*NUM_PEGS*NUM_PES*LOG2_PEGS +: NUM_PEGS*NUM_PES*LOG2_PEGS]   <=  'd0;\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\tif(j == 0) begin\n")
f.write("\t\t\t\t\tr_vn_ff[0 +: NUM_PEGS*NUM_PES*LOG2_PEGS]    <=  w_vn_seperator;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_vn_ff[j*NUM_PEGS*NUM_PES*LOG2_PEGS +: NUM_PEGS*NUM_PES*LOG2_PEGS]   <=  r_vn_ff[(j-1)*NUM_PEGS*NUM_PES*LOG2_PEGS +: NUM_PEGS*NUM_PES*LOG2_PEGS];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\twire    [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]          w_vn_ff_1;\n")
f.write("\tassign  w_vn_ff_1 = r_vn_ff[" + str(9+LOG2_PES) + "*NUM_PEGS*NUM_PES*LOG2_PEGS +: NUM_PEGS*NUM_PES*LOG2_PEGS];\n\n")

f.write("\t// output for lvl1\n")
f.write("\twire                                                    w_data_valid_2;\n")
f.write("\twire    [NUM_PEGS * NUM_PEGS * OUT_DATA_TYPE - 1 : 0]   w_data_bus_2;\n\n")

f.write("\t// 1 cycle\n")
f.write("\tmiddle_reduct_lvl1 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(OUT_DATA_TYPE))\n")
f.write("\t\tmy_mid_reduct_lvl1 (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n\n")

f.write("\t\t\t.i_data_valid(w_data_valid_1),\n")
f.write("\t\t\t.i_data_bus(w_data_bus_1),\n")
f.write("\t\t\t.i_data_rowid(w_vn_ff_1),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid_2),\n")
f.write("\t\t\t.o_data_bus(w_data_bus_2)\n")
f.write("\t);\n\n\n\n")



f.write("\t// ======================= 5 fin =======================\n")
f.write("\t// ff  r_block_vn   (" + str(7+LOG2_PES) + "+3+1) cycles\n")
f.write("\treg     [" + str(11+LOG2_PES) + " * NUM_PEGS * LOG2_PEGS -1 : 0]   r_block_vn_ff;\n")
f.write("\talways @(posedge clk_out) begin\n")
f.write("\t\tfor(j = 0; j < " + str(11+LOG2_PES) + "; j = j + 1) begin\n")
f.write("\t\t\tif(rst) begin\n")
f.write("\t\t\t\tr_block_vn_ff[j*NUM_PEGS*LOG2_PEGS +: NUM_PEGS*LOG2_PEGS]   <=  'd0;\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\tif(j == 0) begin\n")
f.write("\t\t\t\t\tr_block_vn_ff[j*NUM_PEGS*LOG2_PEGS +: NUM_PEGS*LOG2_PEGS]   <=  w_block_vn;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_block_vn_ff[j*NUM_PEGS*LOG2_PEGS +: NUM_PEGS*LOG2_PEGS]   <=  r_block_vn_ff[(j-1)*NUM_PEGS*LOG2_PEGS +: NUM_PEGS*LOG2_PEGS];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\twire    [NUM_PEGS * LOG2_PEGS -1 : 0]        w_block_vn_2;\n")
f.write("\tassign  w_block_vn_2 = r_block_vn_ff[" + str(10+LOG2_PES) + "*NUM_PEGS*LOG2_PEGS +: NUM_PEGS*LOG2_PEGS];\n\n")


f.write("\twire    [NUM_PEGS -1:0]                                 w_data_valid_3;\n")
f.write("\twire    [NUM_PEGS * NUM_PEGS * OUT_DATA_TYPE -1:0]      w_data_bus_3;\n\n")

f.write("\t// " + str(5+LOG2_PEGS) + " cycles\n")
f.write("\tfinal_reduct # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.DATA_TYPE(OUT_DATA_TYPE))\n")
f.write("\t\tmy_final_reduct (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.i_data_valid(w_data_valid_2),\n")
f.write("\t\t\t.i_data_bus(w_data_bus_2),\n")
f.write("\t\t\t.i_vn_seperator(w_block_vn_2),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid_3),\n")
f.write("\t\t\t.o_data_bus(w_data_bus_3)\n")
f.write("\t);\n\n\n\n")



f.write("\t// ======================= 6 res =======================\n")
f.write("\twire    [PARA_BLOCKS:0]                                     w_data_valid_4;\n")
f.write("\twire    [(PARA_BLOCKS + 1) * NUM_PEGS * OUT_DATA_TYPE -1:0] w_data_bus_4;\n")
f.write("\twire    [LOG2_PEGS:0]                                       w_data_num;\n\n")

f.write("\t// 1 cycles\n")
f.write("\tresults_accum_lvl0 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.DATA_TYPE(OUT_DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS)) \n")
f.write("\t\tmy_res_lvl0 (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n\n")

f.write("\t\t\t.i_data_valid(w_data_valid_3),\n")
f.write("\t\t\t.i_data_bus(w_data_bus_3),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid_4),\n")
f.write("\t\t\t.o_data_bus(w_data_bus_4),\n")
f.write("\t\t\t.o_data_num(w_data_num)\n")
f.write("\t);\n\n\n")


f.write("\t// ff  r_accum_ena   (" + str(7+LOG2_PES) + "+3+1+" + str(5+LOG2_PEGS) + "+1) cycles\n")
f.write("\treg     [" + str(17+LOG2_PEGS+LOG2_PES) + "*2-1 : 0]                             	    r_accum_ena_ff;\n")
f.write("\talways @(posedge clk_out) begin\n")
f.write("\t\tfor(j = 0; j < " + str(17+LOG2_PEGS+LOG2_PES) + "; j = j + 1) begin\n")
f.write("\t\t\tif(rst) begin\n")
f.write("\t\t\t\tr_accum_ena_ff[j*2 +: 2]   <=  'd0;\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\tif(j == 0) begin\n")
f.write("\t\t\t\t\tr_accum_ena_ff[j*2 +: 2]   <=  w_accum_ena;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_accum_ena_ff[j*2 +: 2]   <=  r_accum_ena_ff[(j-1)*2 +: 2];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\twire    [1 : 0]                                         w_accum_ena_4;\n")
f.write("\tassign  w_accum_ena_4 = r_accum_ena_ff[" + str(16+LOG2_PEGS+LOG2_PES) + "*2 +: 2];\n\n\n")


f.write("\twire    [PARA_BLOCKS:0]                                 w_data_valid_5;\n")
f.write("\twire    [(PARA_BLOCKS + 1)*NUM_PEGS*OUT_DATA_TYPE-1:0]  w_data_bus_5;\n\n")

f.write("\t// 2 cycles\n")
f.write("\tresults_accum_lvl1 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.DATA_TYPE(OUT_DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.MAX_N_DIM(MAX_N_DIM)) \n")
f.write("\t\tmy_res_lvl1 (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.i_data_valid(w_data_valid_4),\n")
f.write("\t\t\t.i_data_bus(w_data_bus_4),\n")
f.write("\t\t\t.i_data_num(w_data_num),\n")
f.write("\t\t\t.i_accum_ena(w_accum_ena_4),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid_5),\n")
f.write("\t\t\t.o_data_bus(w_data_bus_5)\n")
f.write("\t);\n\n\n")


f.write("\tres_output # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.DATA_TYPE(OUT_DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS)) \n")
f.write("\t\tmy_res_output (\n")
f.write("\t\t\t.clk(clk_out),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n\n")

f.write("\t\t\t.i_data_valid(w_data_valid_5),\n")
f.write("\t\t\t.i_data_bus(w_data_bus_5),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),\n")
f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n")

f.write("endmodule\n")

