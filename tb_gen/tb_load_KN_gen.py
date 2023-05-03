# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_load_KN.sv", mode = 'w')


f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_load_KN.sv\n")
f.write("// Parameterization: NUM_PES, PARA_BLOCKS, LOG2_MEMD, DATA_TYPE\n")
f.write("// Description: Testbench for load_MK vmod\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_load_KN ();\n\n")

f.write("\tparameter DATA_TYPE = " + str(IN_DATA_TYPE) + ";\n")
f.write("\tparameter NUM_PES = " + str(NUM_PES) + ";\n")
f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + ";\n")
f.write("\tparameter PARA_BLOCKS = " + str(PARA_BLOCKS) + ";\n\n")

f.write("\tparameter NUM_TESTS = " + str(int(N_DIM*PARA_BLOCKS*(PARA_BLOCKS-1) + N_DIM*(M_DIM/(PARA_BLOCKS*NUM_PES)-PARA_BLOCKS*(PARA_BLOCKS-1)/2))) + ";\n\n")

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


f.write("\treg [20:0] counter = 'd1;\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\tif (o_fifo_KN_data_empty != 1'b1 && counter < NUM_TESTS) begin\n")
f.write("\t\t\t\tcounter <= counter + 1'b1;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("\treg     [PARA_BLOCKS-1 : 0]                             i_fifo_KN_rd_en [0:" + str(int(PARA_BLOCKS*(PARA_BLOCKS-1) +(M_DIM/(PARA_BLOCKS*NUM_PES)-PARA_BLOCKS*(PARA_BLOCKS-1)/2))) + "] =\n")
f.write("\t{\n")
for i in range(PARA_BLOCKS):
    if(i == 0):
        f.write("\t\t// " + str(PARA_BLOCKS) + "'b")
        rd_en = ""
        for j in range(PARA_BLOCKS):
            rd_en += "0"
        f.write(rd_en + ",\n")
    else:
        for j in range(PARA_BLOCKS):
            start = j
            stop = (j + i - 1) % PARA_BLOCKS
            f.write("\t\t" + str(PARA_BLOCKS) + "'b")
            rd_en = ""
            for k in range(PARA_BLOCKS):
                if( (start <= k and k <= stop) or ((stop < start) and (k <= stop or start <= k)) ):
                    rd_en = "1" + rd_en
                else:
                    rd_en = "0" + rd_en
            f.write(rd_en + ",\n")
# the rest in all ones
for i in range(int(M_DIM/(PARA_BLOCKS*NUM_PES)-PARA_BLOCKS*(PARA_BLOCKS-1)/2)):
    f.write("\t\t" + str(PARA_BLOCKS) + "'b")
    rd_en = ""
    for j in range(PARA_BLOCKS):
        rd_en += "1"
    f.write(rd_en + ",\n")
f.write("\t\t" + str(PARA_BLOCKS) + "'b")
rd_en = ""
for j in range(PARA_BLOCKS):
    rd_en += "1"
f.write(rd_en + "\n")
f.write("\t};\n\n")

f.write("\treg     [PARA_BLOCKS-1 : 0]     r_fifo_KN_rd_en;\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\tr_fifo_KN_rd_en <=  i_fifo_KN_rd_en[counter/N_DIM];\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_fifo_KN_rd_en <= 'd0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")

    
f.write("\treg     [PARA_BLOCKS * DATA_TYPE * NUM_PES - 1 : 0]     o_fifo_KN_data_out;\n")
f.write("\treg                                                     o_fifo_KN_data_empty;\n\n\n")


f.write("\tload_KN # (\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS)) \n")
f.write("\t\tmy_load_KN (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n")
f.write("\t\t\t.M_DIM(M_DIM),\n")
f.write("\t\t\t.K_DIM(K_DIM),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.i_fifo_KN_rd_en(r_fifo_KN_rd_en),\n\n")
            
f.write("\t\t\t.o_fifo_KN_data_out(o_fifo_KN_data_out),\n")
f.write("\t\t\t.o_fifo_KN_data_empty(o_fifo_KN_data_empty)\n")
f.write("\t);\n\n")

f.write("\tinteger data_kn;\n")
f.write("\tinitial begin\n")
f.write("\t\tdata_kn = $fopen(\"tb_load_KN.txt\",\"w\");\n")
f.write("\t\t#1000000000 $finish;\n")
f.write("\tend\n\n\n")


f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_load_KN.o_fifo_KN_data_empty != 1'b1) begin\n")
f.write("\t\t\t$fwrite(data_kn, \"%h\\n\", my_load_KN.o_fifo_KN_data_out);\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("endmodule\n\n")
