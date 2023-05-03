# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
import math
from dec_conv_func import *

f = open(target_path + "tb_res.sv", mode = 'w')

f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_res.sv\n")
f.write("// Parameterization: NUM_PEGS, PARA_BLOCKS, DATA_TYPE\n")
f.write("// Description: Testbench for results_accum vmod\n")
f.write("// for (PARA_BLOCKS + 1) cases\n")
f.write("// each case contains 4 tests for acum_ena\n")
f.write("////////////////////////////////////////////////////////////\n\n")

N_DIM = 5
# ena_num = 4 # 00, 01, 11, 10
ena_num = 5 # 00, 01, 11, 11, 10

f.write("module tb_res ();\n\n")

f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ";\n")
f.write("\tparameter LOG2_PEGS = " + str(LOG2_PEGS) + ";\n")
f.write("\tparameter DATA_TYPE = " + str(OUT_DATA_TYPE) + ";\n")
f.write("\tparameter PARA_BLOCKS = " + str(PARA_BLOCKS) + ";\n")
f.write("\tparameter MAX_N_DIM = " + str(MAX_N_DIM) + ";\n\n")

f.write("\tparameter NUM_TESTS = " + str(N_DIM*ena_num*(PARA_BLOCKS + 1)) + ";    // N_DIM*ena_num*(PARA_BLOCKS + 1)\n\n\n")


f.write("\treg clk = 0;\n")
f.write("\treg rst;\n\n")

f.write("\t// generate simulation clock\n")
f.write("\talways #1 clk = !clk;\n\n")

f.write("\t// set reset signal\n")
f.write("\tinitial begin\n")
f.write("\t\trst = 1'b1;\n")
f.write("\t\t#4\n")
f.write("\t\trst = 1'b0;\n")
f.write("\tend\n\n\n")


f.write("\treg [20:0] N_DIM = 'd" + str(N_DIM) + ";\n\n")

f.write("\t// counter\n")
f.write("\treg [20:0] counter = 'd0;\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\tif (counter < NUM_TESTS) begin\n")
f.write("\t\t\t\tcounter <= counter + 1'b1;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n\n")



f.write("\treg     [NUM_PEGS -1:0]                                 i_data_valid    [0 : PARA_BLOCKS] = \n")
f.write("\t{\n")
for i in range(PARA_BLOCKS+1, 0, -1):
    str0 = "\t\t" + str(NUM_PEGS) + "'h"
    # ivt = int(NUM_PEGS/i)
    ivt = math.ceil(NUM_PEGS/i)
    str1 = ""
    for j in range(NUM_PEGS):
        if((j+1)%ivt == 0):
            str1 = "1" + str1
        else:
            str1 = "0" + str1
    str2 = unsigned_bin2hex(str1, int(NUM_PEGS/4))
    if(i != 1):
        f.write(str0 + str2 + ",\t// " + str(NUM_PEGS) + "/" + str(i) + " " + str1 + "\n")
    else:
        f.write(str0 + str2 + "\t// " + str(NUM_PEGS) + "/" + str(i) + " " + str1 + "\n")
f.write("\t};\n\n")

f.write("\treg     [NUM_PEGS * NUM_PEGS * DATA_TYPE -1:0]          i_data_bus      [0 : PARA_BLOCKS] = \n")
f.write("\t{\n")
for i in range(PARA_BLOCKS+1, 0, -1):
    str0 = "\t\t" + str(NUM_PEGS*NUM_PEGS*OUT_DATA_TYPE) + "'h"
    # ivt = int(NUM_PEGS/i)
    ivt = math.ceil(NUM_PEGS/i)
    str1 = ""
    for j in range(NUM_PEGS):
        if((j+1)%ivt == 0):
            str1 = unsigned_dec2bin(i, OUT_DATA_TYPE)*NUM_PEGS + str1
        else:
            str1 = unsigned_dec2bin(0, OUT_DATA_TYPE)*NUM_PEGS + str1
    str2 = unsigned_bin2hex(str1, int(NUM_PEGS*NUM_PEGS*OUT_DATA_TYPE/4))
    if(i != 1):
        f.write(str0 + str2 + ",\t// " + str(i)*NUM_PEGS + "\n")
    else:
        f.write(str0 + str2 + "\t// " + str(i)*NUM_PEGS + "\n")
f.write("\t};\n\n\n")

    
f.write("\treg     [1:0]                                           i_accum_ena     [0:" + str(ena_num-1) + "]             = \n")
f.write("\t{\n")
f.write("\t\t2'b00,\n")
f.write("\t\t2'b10,\n")
f.write("\t\t2'b11,\n")
f.write("\t\t2'b11,\n")
f.write("\t\t2'b01\n")
f.write("\t};\n\n\n")


f.write("\t// outputs of results_accum_lvl0\n")
f.write("\twire    [PARA_BLOCKS:0]                                 w_data_valid;\n")
f.write("\twire    [(PARA_BLOCKS + 1) * NUM_PEGS * DATA_TYPE -1:0] w_data_bus;\n")
f.write("\twire    [LOG2_PEGS:0]                                   w_data_num;\n\n")

f.write("\t// outputs of results_accum_lvl1\n")
f.write("\twire    [PARA_BLOCKS:0]                                 o_data_valid;\n")
f.write("\twire    [(PARA_BLOCKS + 1) * NUM_PEGS * DATA_TYPE -1:0] o_data_bus;\n\n\n")


f.write("\t// register of the inputs\n")
f.write("\t// inputs of results_accum_lvl0\n")
f.write("\treg     [NUM_PEGS -1:0]                                 r_data_valid    =   'd0;\n")
f.write("\treg     [NUM_PEGS * NUM_PEGS * DATA_TYPE -1:0]          r_data_bus      =   'd0;\n")
f.write("\t// inputs of results_accum_lvl1\n")
f.write("\treg     [1:0]                                           r_accum_ena     =   'd0;\n\n")

f.write("\t// generate input signals to DUT\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0 && counter < NUM_TESTS) begin\n")
f.write("\t\t\tr_data_valid <= i_data_valid[counter/(" + str(N_DIM) + "*" + str(ena_num) + ")];\n")
f.write("\t\t\tr_data_bus <= i_data_bus[counter/(" + str(N_DIM) + "*" + str(ena_num) + ")];\n")
f.write("\t\t\tr_accum_ena <= i_accum_ena[(counter/" + str(N_DIM) + ")%" + str(ena_num) + "];\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_data_valid <= 'd0;\n")
f.write("\t\t\tr_data_bus <= 'd0;\n")
f.write("\t\t\tr_accum_ena <= 'd0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\treg     [1:0]                                           r_accum_ena_ff  =   'd0;\n")
f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst == 1'b0) begin\n")
f.write("\t\t\tr_accum_ena_ff  <=  r_accum_ena;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_accum_ena_ff  <=  'd0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\t// instantiate system (DUT)\n")
f.write("\tresults_accum_lvl0 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS)) \n")
f.write("\t\tmy_res_lvl0 (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n\n")

f.write("\t\t\t.i_data_valid(r_data_valid),\n")
f.write("\t\t\t.i_data_bus(r_data_bus),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid),\n")
f.write("\t\t\t.o_data_bus(w_data_bus),\n")
f.write("\t\t\t.o_data_num(w_data_num)\n")
f.write("\t);\n\n")

f.write("\tresults_accum_lvl1 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t.PARA_BLOCKS(PARA_BLOCKS),\n")
f.write("\t\t.MAX_N_DIM(MAX_N_DIM)) \n")
f.write("\t\tmy_res_lvl1 (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.N_DIM(N_DIM),\n\n")

f.write("\t\t\t.i_data_valid(w_data_valid),\n")
f.write("\t\t\t.i_data_bus(w_data_bus),\n")
f.write("\t\t\t.i_data_num(w_data_num),\n")
f.write("\t\t\t.i_accum_ena(r_accum_ena_ff),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),\n")
f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n\n")


f.write("\tinteger f0, f1;\n")
f.write("\tinitial begin\n")
f.write("\t\tf0 = $fopen(\"tb_res0.txt\",\"w\");\n")
f.write("\t\tf1 = $fopen(\"tb_res1.txt\",\"w\");\n")
f.write("\tend\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_res_lvl0.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(f0, \"%h, %h\\n\", my_res_lvl0.o_data_valid, my_res_lvl0.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\t\tif(my_res_lvl1.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(f1, \"%h, %h\\n\", my_res_lvl1.o_data_valid, my_res_lvl1.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("endmodule\n\n\n")

