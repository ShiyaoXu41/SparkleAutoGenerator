# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_fin.sv", mode = 'w')

DATA_TYPE = OUT_DATA_TYPE


f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_fin.v\n")
f.write("// Parameterization: NUM_PEGS, DATA_TYPE\n")
f.write("// Description: Testbench for final_reduct vmod\n")
f.write("// for n in 'NUM_PEGS' cases\n")
f.write("// each case contains 'NUM_PEGS - n' tests\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_fin ();\n\n")

f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ";\n")
f.write("\tparameter LOG2_PEGS = " + str(LOG2_PEGS) + ";\n")
f.write("\tparameter DATA_TYPE = " + str(DATA_TYPE) + ";\n\n")


# NUM_TESTS = 1*NUM_PEGS + NUM_PEGS*(NUM_PEGS-1)/2
f.write("\tparameter NUM_TESTS = " + str(int(NUM_PEGS+NUM_PEGS*(NUM_PEGS-1)/2)) +";\n\n")

f.write("\treg clk = 0;\n")
f.write("\treg rst;\n\n")
    
f.write("\treg i_data_valid = 1'b1;\n\n")

f.write("\treg [NUM_PEGS * NUM_PEGS * DATA_TYPE -1 : 0] i_data_bus = \n")
str0 = ""
for i in range(NUM_PEGS):
    for j in range(NUM_PEGS):
        str0 = signed_dec2hex(((-1)**i)*j, int(DATA_TYPE/4))[2:] + str0
f.write("\t\t" + str(NUM_PEGS*NUM_PEGS*DATA_TYPE) + "'h" + str0 + ";\n\n")

f.write("\treg [NUM_PEGS * LOG2_PEGS -1:0] i_vn_seperator [0:NUM_TESTS-1] = \n")
f.write("\t\t{\n")
# 'NUM_PEGS' cases
for i in range(NUM_PEGS):
    # tests in each cases
    for j in range(1, NUM_PEGS-i+1):
        i_vn_seperator = ""
        for k in range(i):
            i_vn_seperator = unsigned_dec2bin(0, LOG2_PEGS) + "_" + i_vn_seperator
        # the rest is divied by j
        num = 1
        for k in range(0, NUM_PEGS-i, j):
            if(NUM_PEGS-i < k + j):
                for k1 in range(NUM_PEGS-i -k):
                    i_vn_seperator = unsigned_dec2bin(num%NUM_PEGS, LOG2_PEGS) + "_" + i_vn_seperator
            else:
                for k2 in range(j):
                    i_vn_seperator = unsigned_dec2bin(num%NUM_PEGS, LOG2_PEGS) + "_" + i_vn_seperator
            num += 1
        if(i == NUM_PEGS-1 and j == NUM_PEGS-i):
            f.write("\t\t\t" + str(NUM_PEGS*LOG2_PEGS) + "'b" + i_vn_seperator + "\n")
        else:
            f.write("\t\t\t" + str(NUM_PEGS*LOG2_PEGS) + "'b" + i_vn_seperator + ",\n")
f.write("\t\t};\n\n\n")

	
f.write("\treg [NUM_PEGS -1:0] o_data_valid;\n")
f.write("\treg [NUM_PEGS * NUM_PEGS * DATA_TYPE -1:0] o_data_bus;\n\n\n")


f.write("\t// register of the inputs \n")
f.write("\treg [NUM_PEGS * NUM_PEGS * DATA_TYPE -1 : 0] r_data_bus = 'd0;\n")
f.write("\treg r_data_valid = 1'b0;\n")
f.write("\treg [NUM_PEGS * LOG2_PEGS -1:0] r_vn_seperator = 'd0;\n\n")

f.write("\t// generate simulation clock\n")
f.write("\talways #1 clk = !clk;\n\n")

f.write("\t// set reset signal\n")
f.write("\tinitial begin\n")
f.write("\t\trst = 1'b1;\n")
f.write("\t\t#4\n")
f.write("\t\trst = 1'b0;\n")
f.write("\tend\n\n\n")


f.write("\t// counter\n")
f.write("\treg [20:0] counter = 'd0;\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\tif (counter < NUM_TESTS) begin\n")
f.write("\t\t\t\tcounter <= counter + 1'b1;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")

f.write("\t// generate input signals to DUT\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0 && counter < NUM_TESTS) begin\n")
f.write("\t\t\tr_data_bus = i_data_bus;\n")
f.write("\t\t\tr_data_valid = i_data_valid;\n")
f.write("\t\t\tr_vn_seperator = i_vn_seperator[counter];\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_data_bus = 'd0;\n")
f.write("\t\t\tr_data_valid = 'd0;\n")
f.write("\t\t\tr_vn_seperator = 'd0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\t// instantiate system (DUT)\n")
f.write("\tfinal_reduct # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\tmy_final_reduct (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.i_data_valid(r_data_valid),\n")
f.write("\t\t\t.i_data_bus(r_data_bus),\n")
f.write("\t\t\t.i_vn_seperator(r_vn_seperator),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),\n")
f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n\n")


f.write("\tinteger f;\n")
f.write("\tinitial begin\n")
f.write("\t\tf = $fopen(\"tb_fin.txt\",\"w\");\n")
f.write("\tend\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_final_reduct.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(f, \"%h, %h\\n\", my_final_reduct.o_data_valid, my_final_reduct.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("endmodule\n")
