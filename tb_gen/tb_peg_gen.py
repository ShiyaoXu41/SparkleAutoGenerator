# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_peg.sv", mode = 'w')

f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_peg.v\n")
f.write("// Parameterization: NUM_PEGS, NUM_PES, DATA_TYPE\n")
f.write("// Description: Testbench for PE_group vmod\n")
f.write("// for n in 'NUM_PES' cases\n")
f.write("// each case contains 'NUM_PES - n' tests\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_peg ();\n\n")

f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + "; // number of PE_group Inputs\n")
f.write("\tparameter NUM_PES = " + str(NUM_PES) + "; // number of PE Inputs\n")
f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + "; // log2 of the number of PEs\n")
f.write("\tparameter IN_DATA_TYPE = " + str(IN_DATA_TYPE) + "; // input data type width\n")
f.write("\tparameter OUT_DATA_TYPE = " + str(OUT_DATA_TYPE) + "; // output data type width\n\n")

# NUM_TESTS = 1*NUM_PES + NUM_PES*(NUM_PES-1)/2
f.write("\tparameter NUM_TESTS = " + str(int(NUM_PES+NUM_PES*(NUM_PES-1)/2)) +" + 1;\n\n")

f.write("\treg clk = 0;\n")
f.write("\treg rst;\n\n")

f.write("\treg i_data_valid = 1'b1;\n\n")

f.write("\treg [NUM_PES* IN_DATA_TYPE -1 : 0] i_data_bus [0:1] =\n")
f.write("\t\t{\n")
# f.write("\t\t\t256'h0101_0101_0101_0101_0101_0101_0101_0101_0101_0101_0101_0101_0101_0101_0101_0101,\n")
# f.write("\t\t\t256'h1F1E_1D1C_1B1A_1918_1716_1514_1312_1110_0F0E_0D0C_0B0A_0908_0706_0504_0302_0100\n")
str0 = ""
str1 = ""
for i in range(NUM_PES):
    str0 = unsigned_dec2bin(1, IN_DATA_TYPE) + str0
    str1 = unsigned_dec2bin(i, IN_DATA_TYPE) + str1
str0 = unsigned_bin2hex(str0, int(NUM_PES*IN_DATA_TYPE/4))
str1 = unsigned_bin2hex(str1, int(NUM_PES*IN_DATA_TYPE/4))
f.write("\t\t\t" + str(NUM_PES*IN_DATA_TYPE) + "'h" + str0 + ",\n")
f.write("\t\t\t" + str(NUM_PES*IN_DATA_TYPE) + "'h" + str1 + "\n")
f.write("\t\t};\n\n")

f.write("\treg [1:0] i_stationary = 2'b01;\n\n")

# f.write("\treg [NUM_PES * LOG2_PES -1:0] i_dest_bus = 160'hffbbcdeb38bdab49ca307b9ac5a928398a418820;\n\n")
str0 = ""
for i in range(NUM_PES):
    str0 = unsigned_dec2bin(i, LOG2_PES) + str0
str0 = unsigned_bin2hex(str0, int(NUM_PES*LOG2_PES/4))
str0 = "\treg [NUM_PES * LOG2_PES -1:0] i_dest_bus = " + str(NUM_PES*LOG2_PES) +"'h" + str0 + ";\n\n"
f.write(str0)

# seperator
f.write("\treg [NUM_PES * LOG2_PES -1:0] i_vn_seperator [0:NUM_TESTS-1] =\n")
f.write("\t\t{\n")
# the 1st is stationary vn
str0 = "\t\t\t" + str(NUM_PES*LOG2_PES) + "'b"
for i in range(NUM_PES):
    str0 += unsigned_dec2bin(0, LOG2_PES) + "_"
str0 += ",\n"
f.write(str0)
# 'NUM_PES' cases
for i in range(NUM_PES):
    # tests in each cases
    for j in range(1, NUM_PES-i+1):
        i_vn_seperator = ""
        for k in range(i):
            i_vn_seperator = unsigned_dec2bin(0, LOG2_PES) + "_" + i_vn_seperator
        # the rest is divied by j
        num = 1
        for k in range(0, NUM_PES-i, j):
            if(NUM_PES-i < k + j):
                for k1 in range(NUM_PES-i -k):
                    i_vn_seperator = unsigned_dec2bin(num%NUM_PES, LOG2_PES) + "_" + i_vn_seperator
            else:
                for k2 in range(j):
                    i_vn_seperator = unsigned_dec2bin(num%NUM_PES, LOG2_PES) + "_" + i_vn_seperator
            num += 1
        if(i == NUM_PES-1 and j == NUM_PES-i):
            f.write("\t\t\t" + str(NUM_PES*LOG2_PES) + "'b" + i_vn_seperator + "\n")
        else:
            f.write("\t\t\t" + str(NUM_PES*LOG2_PES) + "'b" + i_vn_seperator + ",\n")
f.write("\t\t};\n\n\n")

f.write("\treg [NUM_PEGS*NUM_PES-1:0] o_data_valid;\n")
f.write("\treg [NUM_PEGS*NUM_PES*OUT_DATA_TYPE -1 : 0] o_data_bus;\n\n")

f.write("\treg [20:0] counter = 'd0;\n\n")

f.write("\t// register of the inputs\n")
f.write("\treg [NUM_PEGS -1 : 0] r_data_valid                          = 'd0;\n")
f.write("\treg [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0] r_data_bus   = 'd0;\n")
f.write("\treg [NUM_PEGS -1 : 0] r_stationary                          = 'd0;\n")
f.write("\treg [NUM_PEGS * NUM_PES * LOG2_PES -1:0] r_dest_bus         = 'd0;\n")
f.write("\treg [NUM_PEGS * NUM_PES * LOG2_PES -1:0] r_vn_seperator     = 'd0;\n\n")

f.write("\t// generate simulation clock\n")
f.write("\talways #1 clk = !clk;\n\n")

f.write("\t// set reset signal\n")
f.write("\tinitial begin\n")
f.write("\t\trst = 1'b1;\n")
f.write("\t\t#4\n")
f.write("\t\trst = 1'b0;\n")
f.write("\tend\n\n")

f.write("\t// counter\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\tif (counter < NUM_TESTS) begin\n")
f.write("\t\t\t\tcounter <= counter + 1'b1;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n")


f.write("\t// generate input signals to DUT\n")
f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin: peg_input_gen\n")
f.write("\t\t\talways @ (posedge clk) begin\n")
f.write("\t\t\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\t\t\tif(0 < counter) begin\n")
f.write("\t\t\t\t\t\tr_data_valid[i] <= i_data_valid;\n")
f.write("\t\t\t\t\t\tr_data_bus[i*NUM_PES*IN_DATA_TYPE +: NUM_PES*IN_DATA_TYPE] <= i_data_bus[1];\n")
f.write("\t\t\t\t\t\tr_stationary[i] <= i_stationary[1];\n")
f.write("\t\t\t\t\t\tr_dest_bus[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES] <= i_dest_bus;\n")
f.write("\t\t\t\t\t\tr_vn_seperator[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES] <= i_vn_seperator[counter];\n")
f.write("\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\tr_data_valid[i] <= i_data_valid;\n")
f.write("\t\t\t\t\t\tr_data_bus[i*NUM_PES*IN_DATA_TYPE +: NUM_PES*IN_DATA_TYPE] <= i_data_bus[counter];\n")
f.write("\t\t\t\t\t\tr_stationary[i] <= i_stationary[counter];\n")
f.write("\t\t\t\t\t\tr_dest_bus[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES] <= i_dest_bus;\n")
f.write("\t\t\t\t\t\tr_vn_seperator[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES] <= i_vn_seperator[counter];\n")
f.write("\t\t\t\t\tend\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_data_valid[i] <= 'd0;\n")
f.write("\t\t\t\t\tr_data_bus[i*NUM_PES*IN_DATA_TYPE +: NUM_PES*IN_DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\t\tr_stationary[i] <= 'd0;\n")
f.write("\t\t\t\t\tr_dest_bus[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES] <= 'd0;\n")
f.write("\t\t\t\t\tr_vn_seperator[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES] <= 'd0;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")


f.write("\t// instantiate system (DUT)\n")
f.write("\tpe_group # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.IN_DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t.OUT_DATA_TYPE(OUT_DATA_TYPE))\n")
f.write("\t\tmy_peg (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.i_data_valid(r_data_valid),\n")
f.write("\t\t\t.i_data_bus(r_data_bus),\n")
f.write("\t\t\t.i_stationary(r_stationary),\n")
f.write("\t\t\t.i_dest_bus(r_dest_bus), \n")
f.write("\t\t\t.i_vn_seperator(r_vn_seperator),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),\n")
f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n")

f.write("\tinteger g;\n")
f.write("\tinitial begin\n")
f.write("\t\tg = $fopen(\"tb_peg.txt\",\"w\");\n")
f.write("\t\t// $fwrite(g, \"\\n------------------------------------------\\n\");\n")
f.write("\t\t// $fwrite(g, \"Timestamp - Valid - Value \");\n")
f.write("\t\t// $fwrite(g, \"\\n------------------------------------------\\n\");\n")
f.write("\tend\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_peg.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(g, \"%h, %h\\n\", my_peg.o_data_valid, my_peg.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("endmodule\n\n")
