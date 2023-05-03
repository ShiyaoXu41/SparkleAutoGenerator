# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# =============== 1. get target tb path ================
target_path = root_path + "\\tb\\"


# =================== 2. generate tb ===================
# ======================================================
from dec_conv_func import *

f = open(target_path + "tb_mid.sv", mode = 'w')

DATA_TYPE = OUT_DATA_TYPE


f.write("`timescale 1ns / 1ps\n")
f.write("////////////////////////////////////////////////////////////\n")
f.write("// Design: tb_mid.v\n")
f.write("// Parameterization: NUM_PEGS, NUM_PES, DATA_TYPE\n")
f.write("// Description: Testbench for middle_reduct_lvl0/1 vmod\n")
f.write("////////////////////////////////////////////////////////////\n\n")

f.write("module tb_mid ();\n\n")

f.write("\tparameter NUM_PEGS  = " + str(NUM_PEGS) + ";   // number of PE_group Inputs\n")
f.write("\tparameter LOG2_PEGS = " + str(LOG2_PEGS) + ";    // log2 of the number of PE_groups\n")
f.write("\tparameter NUM_PES   = " + str(NUM_PES) + ";   // number of PE Inputs\n")
f.write("\tparameter LOG2_PES  = " + str(LOG2_PES) + ";    // log2 of the number of PEs\n")
f.write("\tparameter DATA_TYPE = " + str(OUT_DATA_TYPE) + ";   // [output] data type width\n\n")

f.write("\tparameter NUM_TESTS = 5;    // simulate sparsity with [0, 20%, 40%, 60%, 80%]\n\n\n")


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


f.write("\t// counter\n")
f.write("\treg [20:0] counter = 'd0;\n\n")
    
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0) begin\n")
f.write("\t\t\tif (counter < NUM_TESTS) begin\n")
f.write("\t\t\t\tcounter <= counter + 1'b1;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")

# sparsity equals 0.2*tms, ranges from 0 to 0.8
sep = int(NUM_PES*0.2)
tms = [0, 1, 2, 3, 4]

f.write("\treg     [NUM_PEGS-1 : 0]                            i_data_add      [0:NUM_TESTS-1] = \n")
f.write("\t{\n")
for i in tms:
    str0 = "\t\t" + str(NUM_PEGS) + "'h"
    # intervals simulate the valid data
    itv = NUM_PES-i*sep
    # size NUM_PEGS * 1-bit
    add = ""
    for j in range(NUM_PEGS):
        if( (((j+1)*NUM_PES) % itv != 0) or (int(((j+1)*NUM_PES) / (NUM_PEGS*itv)) - int((j*NUM_PES) / (NUM_PEGS*itv)) > 1 and ((j+1)*NUM_PES) % (NUM_PEGS*itv) != 0) ):
            add = "1" + add
        else:
            add = "0" + add
    if(i != 4):
        f.write(str0 + unsigned_bin2hex(add, int(NUM_PEGS/4)) + ",\n")
    else:
        f.write(str0 + unsigned_bin2hex(add, int(NUM_PEGS/4)) + "\n")
f.write("\t};\n\n")

f.write("\treg     [NUM_PEGS * NUM_PES -1:0]                   i_data_valid    [0:NUM_TESTS-1] = \n")
f.write("\t{\n")
for i in tms:
    str0 = "\t\t" + str(NUM_PEGS*NUM_PES) + "'h"
    # intervals simulate the valid data
    itv = NUM_PES-i*sep
    # size NUM_PEGS * NUM_PES * 1-bit
    valid = ""  
    # allocate as more [NUM_PEGS*itv] nums to [NUM_PEGS*NUM_PES] PES
    for j in range(NUM_PEGS):
        for k in range(NUM_PES):
            if( ((j*NUM_PES+k+1) % itv == 0) or ((k == NUM_PES-1) and ((j*NUM_PES+k+1) % itv != 0)) ):
                valid = "1" + valid
            else:
                valid = "0" + valid
    if(i != 4):
        f.write(str0 + unsigned_bin2hex(valid, int(NUM_PEGS*NUM_PES/4)) + ",\n")
    else:
        f.write(str0 + unsigned_bin2hex(valid, int(NUM_PEGS*NUM_PES/4)) + "\n")
f.write("\t};\n\n")

f.write("\treg     [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    i_data_bus      [0:NUM_TESTS-1] = \n")
f.write("\t{\n")
str0 = "\t\t" + str(NUM_PEGS*NUM_PES*DATA_TYPE) + "'h"
for i in tms:
    # intervals simulate the valid data
    itv = NUM_PES-i*sep
    data = ""       # size NUM_PEGS * NUM_PES * DATA_TYPE
    # allocate as more [NUM_PEGS*itv] nums to [NUM_PEGS*NUM_PES] PES
    d_sum = 0
    for j in range(NUM_PEGS):
        for k in range(NUM_PES):
            d_sum += 1
            if( ((j*NUM_PES+k+1) % itv == 0) or ((k == NUM_PES-1) and ((j*NUM_PES+k+1) % itv != 0)) ):
                data = unsigned_dec2bin(d_sum, DATA_TYPE) + data
                d_sum = 0
            else:
                data = unsigned_dec2bin(0, DATA_TYPE) + data
    if(i != 4):
        f.write(str0 + unsigned_bin2hex(data, int(NUM_PEGS*NUM_PES*DATA_TYPE/4)) + ",\n")
    else:
        f.write(str0 + unsigned_bin2hex(data, int(NUM_PEGS*NUM_PES*DATA_TYPE/4)) + "\n")
f.write("\t};\n\n")

f.write("\treg     [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     i_vn            [0:NUM_TESTS-1] = \n")
f.write("\t{\n")
str0 = "\t\t" + str(NUM_PEGS*NUM_PES*LOG2_PEGS) + "'h"
for i in tms:
    # intervals simulate the valid data
    itv = NUM_PES-i*sep
    vn = ""         # size NUM_PEGS * NUM_PES * LOG2_PE
    for j in range(NUM_PEGS):
        for k in range(NUM_PES):
            vn = unsigned_dec2bin(int((j*NUM_PES+k)/itv) % NUM_PEGS, LOG2_PEGS) + vn
    if(i != 4):
        f.write(str0 + unsigned_bin2hex(vn, int(NUM_PEGS*NUM_PES*LOG2_PEGS/4)) + ",\n")
    else:
        f.write(str0 + unsigned_bin2hex(vn, int(NUM_PEGS*NUM_PES*LOG2_PEGS/4)) + "\n")            
f.write("\t};\n\n\n")


f.write("\t// register of the inputs\n\n")

f.write("\t// input for lvl0\n")
f.write("\treg     [NUM_PEGS-1 : 0]                            r_data_add      = 'd0;\n")
f.write("\treg     [NUM_PEGS * NUM_PES -1:0]                   r_data_valid    = 'd0;\n")
f.write("\treg     [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    r_data_bus      = 'd0;\n\n")
    
f.write("\t// input for lvl1\n")
f.write("\treg     [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     r_vn            = 'd0;  // limited in 0 to NUM_PES, LOG2_PES size\n\n")

f.write("\t// generate input signals to DUT\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b0 && counter < NUM_TESTS) begin\n")
f.write("\t\t\tr_data_add      <=  i_data_add[counter];\n")
f.write("\t\t\tr_data_valid    <=  i_data_valid[counter];\n")
f.write("\t\t\tr_data_bus      <=  i_data_bus[counter];\n")
f.write("\t\t\tr_vn            <=  i_vn[counter];\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_data_add      <=  'd0;\n")
f.write("\t\t\tr_data_valid    <=  'd0;\n")
f.write("\t\t\tr_data_bus      <=  'd0;\n")
f.write("\t\t\tr_vn            <=  'd0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\treg     [NUM_PEGS * NUM_PES * LOG2_PEGS -1 : 0]     r_vn_ff [0:2];\n")
f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst == 1'b0) begin\n")
f.write("\t\t\tr_vn_ff[0]      <=  r_vn;\n")
f.write("\t\t\tr_vn_ff[1]      <=  r_vn_ff[0];\n")
f.write("\t\t\tr_vn_ff[2]      <=  r_vn_ff[1];\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_vn_ff[0]   <=  'd0;\n")
f.write("\t\t\tr_vn_ff[1]   <=  'd0;\n")
f.write("\t\t\tr_vn_ff[2]   <=  'd0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\t// output for lvl0\n")
f.write("\twire    [DATA_TYPE - 1 : 0]                         w_data_temp;\n")
f.write("\twire    [NUM_PEGS * NUM_PES -1:0]                   w_data_valid;\n")
f.write("\twire    [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    w_data_bus;\n\n")

f.write("\t// output for lvl1\n")
f.write("\twire                                                o_data_valid;\n")
f.write("\twire    [NUM_PEGS * NUM_PEGS * DATA_TYPE - 1 : 0]   o_data_bus;\n\n")

f.write("\t// instantiate system (DUT)\n\n")

f.write("\tmiddle_reduct_lvl0 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\tmy_mid_reduct_lvl0 (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(1'b1),\n\n")

f.write("\t\t\t.i_data_add(r_data_add),\n")
f.write("\t\t\t.i_data_valid(r_data_valid),\n")
f.write("\t\t\t.i_data_bus(r_data_bus),\n")
f.write("\t\t\t.i_data_temp(w_data_temp),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid),\n")
f.write("\t\t\t.o_data_bus(w_data_bus),\n")
f.write("\t\t\t.o_data_temp(w_data_temp)\n")
f.write("\t);\n\n")

f.write("\tmiddle_reduct_lvl1 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.LOG2_PES(LOG2_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\tmy_mid_reduct_lvl1 (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(1'b1),\n\n")
            
f.write("\t\t\t.i_data_valid(w_data_valid),\n")
f.write("\t\t\t.i_data_bus(w_data_bus),\n")
f.write("\t\t\t.i_data_rowid(r_vn_ff[2]),\n\n")

f.write("\t\t\t.o_data_valid(o_data_valid),\n")
f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n\n")


f.write("\tinteger f0, f1;\n")
f.write("\tinitial begin\n")
f.write("\t\tf0 = $fopen(\"tb_mid0.txt\",\"w\");\n")
f.write("\t\tf1 = $fopen(\"tb_mid1.txt\",\"w\");\n")
f.write("\tend\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(my_mid_reduct_lvl0.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(f0, \"%h, %h\\n\", my_mid_reduct_lvl0.o_data_valid, my_mid_reduct_lvl0.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\t\tif(my_mid_reduct_lvl1.o_data_valid != 'd0) begin\n")
f.write("\t\t\t$fwrite(f1, \"%h, %h\\n\", my_mid_reduct_lvl1.o_data_valid, my_mid_reduct_lvl1.o_data_bus);\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("endmodule\n")
