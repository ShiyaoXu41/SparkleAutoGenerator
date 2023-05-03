# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_load_MK.sv", mode = 'w')


f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_load_MK.sv\n")
f.write("// Parameterization: NUM_PEGS, NUM_PES, LOG2_MEMD, DATA_TYPE\n")
f.write("// Description: Testbench for load_MK vmod\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_load_MK ();\n\n")

f.write("\tparameter DATA_TYPE = " + str(IN_DATA_TYPE) + ";\n")
f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ";\n")
f.write("\tparameter LOG2_PEGS = " + str(LOG2_PEGS) + ";\n")
f.write("\tparameter NUM_PES = " + str(NUM_PES) + ";\n")
f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + ";\n")
f.write("\tparameter LOG2_MEMD = " + str(LOG2_MEMD) + ";\n")
f.write("\tparameter POINTER_WIDTH = " + str(POINTER_WIDTH) + ";\n\n")

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
f.write("\t\tena = 1'b1;\n")
f.write("\tend\n\n\n")


f.write("\treg     [20 : 0]      M_DIM     =   'd768;\n")
f.write("\treg     [20 : 0]      K_DIM     =   'd768;\n")
f.write("\treg     [20 : 0]      N_DIM     =   'd128;\n\n\n")


f.write("\treg     [DATA_TYPE * NUM_PES - 1 : 0]   o_fifo_MK_data_out;\n")
f.write("\treg     [LOG2_PES * NUM_PES - 1 : 0]    o_fifo_dest_out;\n")
f.write("\treg     [LOG2_PEGS * NUM_PES - 1 : 0]   o_fifo_vn_out;\n")
f.write("\treg     [1 : 0]                         o_fifo_flag_out;\n")
f.write("\treg                                     o_fifo_MK_empty;\n\n\n")


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

f.write("\t\t\t.i_fifo_MK_rd_en(1'b1),\n\n")

f.write("\t\t\t.o_fifo_MK_data_out(o_fifo_MK_data_out),\n")
f.write("\t\t\t.o_fifo_dest_out(o_fifo_dest_out),\n")
f.write("\t\t\t.o_fifo_vn_out(o_fifo_vn_out),\n")
f.write("\t\t\t.o_fifo_flag_out(o_fifo_flag_out),\n\n")

f.write("\t\t\t.o_fifo_MK_empty(o_fifo_MK_empty)\n")
f.write("\t);\n\n\n")


f.write("\tinteger data_mk, dest, vn, flag;\n")
f.write("\tinitial begin\n")
f.write("\t\tdata_mk = $fopen(\"tb_load_MK_data.txt\",\"w\");\n")
f.write("\t\tdest = $fopen(\"tb_load_dest.txt\",\"w\");\n")
f.write("\t\tvn = $fopen(\"tb_load_vn.txt\",\"w\");\n")
f.write("\t\tflag = $fopen(\"tb_load_flag.txt\",\"w\");\n")
f.write("\t\t#1000000000 $finish;\n")
f.write("\tend\n\n\n")


f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_load_MK.o_fifo_MK_empty != 1'b1) begin\n")
f.write("\t\t\t$fwrite(data_mk, \"%h\\n\", my_load_MK.o_fifo_MK_data_out);\n")
f.write("\t\t\t$fwrite(dest, \"%h\\n\", my_load_MK.o_fifo_dest_out);\n")
f.write("\t\t\t$fwrite(vn, \"%h\\n\", my_load_MK.o_fifo_vn_out);\n")
f.write("\t\t\t$fwrite(flag, \"%b\\n\", my_load_MK.o_fifo_flag_out);\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("endmodule\n\n")