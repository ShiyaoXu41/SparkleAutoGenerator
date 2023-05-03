# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
if not os.path.exists(root_path + "\\tb"):
    os.makedirs(root_path + "\\tb")
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_top.sv", mode = 'w')

f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_top.sv\n")
f.write("// Parameterization: NUM_PEGS, NUM_PES, DATA_TYPE, PARA_BLOCKS, POINTER_WIDTH, MAX_N_DIM\n")
f.write("// Description: Testbench for top vmod\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_top ();\n\n")

f.write("\tparameter   NUM_PEGS            =   " + str(NUM_PEGS) + ";\n")
f.write("\tparameter   LOG2_PEGS           =   " + str(LOG2_PEGS) + ";\n\n")

f.write("\tparameter   NUM_PES             =   " + str(NUM_PES) + ";\n")
f.write("\tparameter   LOG2_PES            =   " + str(LOG2_PES) + ";\n\n")

f.write("\tparameter   IN_DATA_TYPE        =   " + str(IN_DATA_TYPE) + ";\n")
f.write("\tparameter   OUT_DATA_TYPE       =   " + str(OUT_DATA_TYPE) + ";\n\n")

f.write("\tparameter   PARA_BLOCKS         =   " + str(PARA_BLOCKS) + ";\n")
f.write("\tparameter   LOG2_PARA_BLOCKS    =   " + str(LOG2_PARA_BLOCKS) + ";\n\n")

f.write("\tparameter   POINTER_WIDTH       =   " + str(POINTER_WIDTH) + ";\n")
f.write("\tparameter   LOG2_MEMD           =   " + str(LOG2_MEMD) + ";\n\n")

f.write("\tparameter   MAX_N_DIM           =   " + str(MAX_N_DIM) + ";\n\n\n\n")



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
f.write("\tend\n\n\n")


f.write("\treg     [20 : 0]      M_DIM     =   'd" + str(M_DIM) + ";\n")
f.write("\treg     [20 : 0]      K_DIM     =   'd" + str(K_DIM) + ";\n")
f.write("\treg     [20 : 0]      K_PAD     =   'd" + str(K_PAD) + ";\n")
f.write("\treg     [20 : 0]      N_DIM     =   'd" + str(N_DIM) + ";\n\n")

f.write("\t// outputs\n")
f.write("\twire                                    o_data_valid;\n")
f.write("\twire    [NUM_PEGS*OUT_DATA_TYPE-1:0]    o_data_bus;\n\n\n")


f.write("\ttop #(\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.IN_DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.OUT_DATA_TYPE(OUT_DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.LOG2_PARA_BLOCKS(LOG2_PARA_BLOCKS),\n")
f.write("\t\t.POINTER_WIDTH(POINTER_WIDTH),\n")
f.write("\t\t.LOG2_MEMD(LOG2_MEMD),\n")
f.write("\t\t.MAX_N_DIM(MAX_N_DIM))\n")
f.write("\t\tmy_top (\n")
f.write("\t\t\t// .clk_in(clk),\n")
f.write("\t\t\t.clk_out(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n")
f.write("\t\t\t.M_DIM(M_DIM),\n")
f.write("\t\t\t.K_DIM(K_DIM),\n")
f.write("\t\t\t.K_PAD(K_PAD),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),\n")
f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n\n")


f.write("\tinteger f_data;\n")
f.write("\tinitial begin\n")
f.write("\t\tf_data = $fopen(\"tb_top_s" + str(int(SPARSITY*10)) + ".txt\",\"w\");\n")
f.write("\tend\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_top.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(f_data, \"%dns, %h\\n\", $time, my_top.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\t// genvar i;\n")
f.write("\t// generate\n")
f.write("\t// 	for(i = PARA_BLOCKS; i >= 0; i = i - 1) begin\n")
f.write("\t// 		always @ (posedge clk) begin\n")
f.write("\t// 			if(my_top.o_data_valid != 'd0) begin\n")
f.write("\t// 				if(my_top.o_data_valid[i] == 1'b1) begin\n")
f.write("\t// 					$fwrite(f_data, \"%h\", my_top.o_data_bus[i*NUM_PEGS*OUT_DATA_TYPE +: NUM_PEGS*OUT_DATA_TYPE]);\n")
f.write("\t// 				end\n")
f.write("\t// 				if(i == 0) begin\n")
f.write("\t// 					$fwrite(f_data, \"\\n\");\n")
f.write("\t// 				end\n")
f.write("\t// 			end\n")
f.write("\t// 		end\n")
f.write("\t// 	end\n")
f.write("\t// endgenerate\n\n")

f.write("endmodule\n")