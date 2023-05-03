# ================== 2. generate vmod ==================
# ======================================================
from fan_network_func import *

target_path = root_path + "\\vmod\\"

f = open(target_path + "middle_reduct.v", mode = 'w')


f.write("// reduct across pegs\n\n")

f.write("module middle_reduct_lvl0 # (\n")
f.write("\tparameter   NUM_PEGS    =   " + str(NUM_PEGS) +",\n")
f.write("\tparameter   NUM_PES     =   " + str(NUM_PES) +",\n")
f.write("\tparameter   DATA_TYPE   =   " + str(OUT_DATA_TYPE) +" ) (\n")
f.write("\tinput                                                       clk,\n")
f.write("\tinput                                                       rst,\n")
f.write("\tinput                                                       ena,\n\n")

f.write("\tinput           [NUM_PEGS - 1 : 0]                          i_data_add,\n")
f.write("\tinput           [NUM_PEGS * NUM_PES -1:0]                   i_data_valid,\n")
f.write("\tinput           [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    i_data_bus,\n")
f.write("\tinput           [DATA_TYPE - 1 : 0]                         i_data_temp,\n\n")

f.write("\toutput  reg     [NUM_PEGS * NUM_PES -1:0]                   o_data_valid,\n")
f.write("\toutput          [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    o_data_bus,\n")
f.write("\toutput          [DATA_TYPE - 1 : 0]                         o_data_temp\n")
f.write("\t);\n\n")

f.write("\twire        [NUM_PEGS * DATA_TYPE - 1 : 0]                  partial_data;\n\n")

f.write("\twire        [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]        data_bus;\n\n")

f.write("\twire        [NUM_PEGS * NUM_PES -1:0]                       w_data_valid;\n")
f.write("\twire        [DATA_TYPE - 1 : 0]                             w_data_temp;\n\n")

f.write("\t// 2 cycles\n")
f.write("\tmiddle_reduct_lvl0_0 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\tmy_middle_reduct_lvl0_0 (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n\n")

f.write("\t\t\t.i_data_add(i_data_add),\n")
f.write("\t\t\t.i_data_valid(i_data_valid),\n")
f.write("\t\t\t.i_data_bus(i_data_bus),\n")
f.write("\t\t\t.i_data_temp(i_data_temp),\n\n")

f.write("\t\t\t.o_data_valid(w_data_valid),\n")
f.write("\t\t\t.o_data_temp(w_data_temp),\n")
f.write("\t\t\t.data_bus(data_bus),\n")
f.write("\t\t\t.partial_data(partial_data)\n")
f.write("\t);\n\n")

f.write("\t// 1 cycles\n")
f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\to_data_valid    <=  'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_data_valid    <=  w_data_valid;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\tmiddle_reduct_lvl0_1 # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE) ) \n")
f.write("\t\tmy_middle_reduct_lvl0_1 (\n")
f.write("\t\t\t.clk(clk),\n")
f.write("\t\t\t.rst(rst),\n")
f.write("\t\t\t.ena(ena),\n\n")

f.write("\t\t\t.i_data_valid(w_data_valid),\n")
f.write("\t\t\t.data_bus(data_bus),\n")
f.write("\t\t\t.partial_data(partial_data),\n\n")

f.write("\t\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n")

f.write("\tassign o_data_temp = w_data_temp;\n\n")

f.write("endmodule\n\n\n")


f.write("module middle_reduct_lvl0_0 # (\n")
f.write("\tparameter                                                   NUM_PEGS    =   " + str(NUM_PEGS) +",\n")
f.write("\tparameter                                                   NUM_PES     =   " + str(NUM_PES) +",\n")
f.write("\tparameter                                                   DATA_TYPE   =   " + str(OUT_DATA_TYPE) +" ) (\n")
f.write("\tinput                                                       clk,\n")
f.write("\tinput                                                       rst,\n")
f.write("\tinput                                                       ena,\n\n")

f.write("\tinput           [NUM_PEGS - 1 : 0]                          i_data_add,\n")
f.write("\tinput           [NUM_PEGS * NUM_PES -1:0]                   i_data_valid,\n")
f.write("\tinput           [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    i_data_bus,\n")
f.write("\tinput           [DATA_TYPE - 1 : 0]                         i_data_temp,\n\n")

f.write("\toutput  reg     [NUM_PEGS * NUM_PES -1:0]                   o_data_valid,\n")
f.write("\toutput          [DATA_TYPE - 1 : 0]                         o_data_temp,\n")
f.write("\toutput  reg     [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    data_bus,\n")
f.write("\toutput          [NUM_PEGS * DATA_TYPE - 1 : 0]              partial_data\n")
f.write("\t);\n\n")

f.write("\treg             [NUM_PEGS * NUM_PES -1:0]                   data_valid;\n")
f.write("\treg             [NUM_PEGS * DATA_TYPE - 1 : 0]              data_temp;\n\n")

f.write("\treg             [NUM_PEGS * DATA_TYPE - 1 : 0]              r_adder_A;\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin\n")
f.write("\t\t\talways @(posedge clk) begin\n")
f.write("\t\t\t\t// data_valid[i*NUM_PES +: NUM_PES] = i_data_valid[i*NUM_PES +: NUM_PES];\n")
f.write("\t\t\t\t// data_temp[i*DATA_TYPE +: DATA_TYPE] = 'd0;\n\n")

f.write("\t\t\t\tif(rst) begin\n")
f.write("\t\t\t\t\tdata_valid[i*NUM_PES +: NUM_PES] <= 'd0;\n")
f.write("\t\t\t\t\tdata_temp[i*DATA_TYPE +: DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\tend else if(ena) begin\n\n")

f.write("\t\t\t\t\tif(i_data_add[i]) begin\n\n")
                        
f.write("\t\t\t\t\t\tcasex(i_data_valid[i*NUM_PES +: NUM_PES])\n")
for i in range(NUM_PES):
    str0 = "\t\t\t\t\t\t\t" + str(NUM_PES) + "'b"
    for j in range(i):
        str0 += "0"
    str0 += "1"
    for j in range(NUM_PES-i-1):
        str0 += "x"
    f.write(str0 + ": begin\n")
    str1 = "\t\t\t\t\t\t\t\tdata_valid[i*NUM_PES +: NUM_PES] <= {"
    if(i != 0):
        str1 += "i_data_valid[i*NUM_PES+NUM_PES-" + str(i) + " +: " + str(i) + "], "
    str1 += "1'b0"
    if(i == NUM_PES-1):
        str1 += "};\n"
    else:
        str1 += ", i_data_valid[i*NUM_PES +: NUM_PES-" + str(i+1) + "]};\n"
    f.write(str1)
    f.write("\t\t\t\t\t\t\t\tdata_temp[i*DATA_TYPE +: DATA_TYPE] <= i_data_bus[(i*NUM_PES+"+str(NUM_PES-i-1)+")*DATA_TYPE +: DATA_TYPE];\n")
    f.write("\t\t\t\t\t\t\tend\n")
f.write("\t\t\t\t\t\t\tdefault: begin\n")
f.write("\t\t\t\t\t\t\t\tdata_valid[i*NUM_PES +: NUM_PES] <= i_data_valid[i*NUM_PES +: NUM_PES];\n")
f.write("\t\t\t\t\t\t\t\tdata_temp[i*DATA_TYPE +: DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\t\t\t\tend\n")
f.write("\t\t\t\t\t\tendcase\n\n")

f.write("\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\tdata_valid[i*NUM_PES +: NUM_PES] <= i_data_valid[i*NUM_PES +: NUM_PES];\n")
f.write("\t\t\t\t\t\tdata_temp[i*DATA_TYPE +: DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\t\tend\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tdata_valid[i*NUM_PES +: NUM_PES] <= i_data_valid[i*NUM_PES +: NUM_PES];\n")
f.write("\t\t\t\t\tdata_temp[i*DATA_TYPE +: DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin\n")
f.write("\t\t\talways @(posedge clk) begin\n")
f.write("\t\t\t\tif(rst) begin\n")
f.write("\t\t\t\t\tr_adder_A[i*DATA_TYPE +: DATA_TYPE]     <=   'd0;\n")
f.write("\t\t\t\tend else if(ena) begin\n\n")

f.write("\t\t\t\t\tcasex(i_data_valid[i*NUM_PES +: NUM_PES])\n")
for i in range(NUM_PES):
    str0 = "\t\t\t\t\t\t" + str(NUM_PES) + "'b"
    for j in range(NUM_PES-i-1):
        str0 += "x"
    str0 += "1"
    for j in range(i):
        str0 += "0"
    str0 += ": r_adder_A[i*DATA_TYPE +: DATA_TYPE]   <=   i_data_bus[(i*NUM_PES+"
    f.write(str0 + str(i) + ")*DATA_TYPE +: DATA_TYPE];\n")
f.write("\t\t\t\t\t\tdefault: r_adder_A[i*DATA_TYPE +: DATA_TYPE]     <=   'd0;\n")
f.write("\t\t\t\t\tendcase\n\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_adder_A[i*DATA_TYPE +: DATA_TYPE]     <=   'd0;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

f.write("\t// ff\n")
f.write("\treg [DATA_TYPE - 1 : 0] r_data_temp;\n")
f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\tr_data_temp <= 'd0;\n")
f.write("\t\tend else if(ena) begin\n")
f.write("\t\t\tr_data_temp <= i_data_temp;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_data_temp <= r_data_temp;\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("\t// =============== the 2nd cycle ===========\n\n")

f.write("\tAdder_%d my_Adder_%d (\n" % (OUT_DATA_TYPE, OUT_DATA_TYPE))
f.write("\t\t.A(r_adder_A[0 +: DATA_TYPE]),\n")
f.write("\t\t.B(r_data_temp),\n")
f.write("\t\t.CLK(clk),\n")
f.write("\t\t.S(partial_data[0 +: DATA_TYPE])\n")
f.write("\t);\n\n")

f.write("\t// adder_n # (\n")
f.write("\t// 	.IN_DATA_TYPE(DATA_TYPE),\n")
f.write("\t// 	.OUT_DATA_TYPE(DATA_TYPE))\n")
f.write("\t// 	my_adder_n (\n")
f.write("\t// 	.clk(clk),\n")
f.write("\t// 	.rst(rst),\n")
f.write("\t// 	.A(r_adder_A[0 +: DATA_TYPE]),\n")
f.write("\t// 	.B(i_data_temp),\n")
f.write("\t// 	.O(partial_data[0 +: DATA_TYPE])\n")
f.write("\t// );\n\n")

f.write("\tgenerate\n")
f.write("\t\tfor(i = 1; i < NUM_PEGS; i = i + 1) begin\n\n")

f.write("\t\t\tAdder_%d my_Adder_%d (\n" % (OUT_DATA_TYPE, OUT_DATA_TYPE))
f.write("\t\t\t\t.A(r_adder_A[i*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t\t.B(data_temp[(i-1)*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t\t.CLK(clk),\n")
f.write("\t\t\t\t.S(partial_data[i*DATA_TYPE +: DATA_TYPE])\n")
f.write("\t\t\t);\n\n")

f.write("\t\t\t// adder_n # (\n")
f.write("\t\t\t// 	.IN_DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t\t// 	.OUT_DATA_TYPE(DATA_TYPE))\n")
f.write("\t\t\t// 	my_adder_n (\n")
f.write("\t\t\t// 	.clk(clk),\n")
f.write("\t\t\t// 	.rst(rst),\n")
f.write("\t\t\t// 	.A(r_adder_A[i*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t// 	.B(data_temp[(i-1)*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t// 	.O(partial_data[i*DATA_TYPE +: DATA_TYPE])\n")
f.write("\t\t\t// );\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")


f.write("\t// 3 ========== output\n\n")    

f.write("\talways @(posedge clk) begin\n")    
f.write("\t\tif(rst) begin\n")
f.write("\t\t\to_data_valid    <= 'd0;\n")             
f.write("\t\tend else if(ena) begin\n")
f.write("\t\t\to_data_valid    <= data_valid;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_data_valid    <= o_data_valid;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\treg [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]    r_data_bus;\n\n")

f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\tr_data_bus  <= 'd0;\n")
f.write("\t\t\tdata_bus    <= 'd0;\n")
f.write("\t\tend else if(ena) begin\n")
f.write("\t\t\tr_data_bus  <=  i_data_bus;\n")
f.write("\t\t\tdata_bus    <=  r_data_bus;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tdata_bus    <=  data_bus;\n")
f.write("\t\t\tr_data_bus  <=  r_data_bus;\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("\tassign o_data_temp = data_temp[(NUM_PEGS-1)*DATA_TYPE +: DATA_TYPE];\n\n\n")


f.write("endmodule\n\n\n")


f.write("module middle_reduct_lvl0_1 # (\n")
f.write("\tparameter                                                       NUM_PEGS    =   " + str(NUM_PEGS) + ",\n")
f.write("\tparameter                                                       NUM_PES     =   " + str(NUM_PES) + ",\n")
f.write("\tparameter                                                       DATA_TYPE   =   " + str(OUT_DATA_TYPE) + " ) (\n\n")

f.write("\tinput                                                           clk,\n")
f.write("\tinput                                                           rst,\n")
f.write("\tinput                                                           ena,\n\n")

f.write("\tinput           [NUM_PEGS * NUM_PES -1:0]                       i_data_valid,\n")
f.write("\tinput           [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]        data_bus,\n")
f.write("\tinput           [NUM_PEGS * DATA_TYPE - 1 : 0]                  partial_data,\n\n")

f.write("\toutput  reg     [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]        o_data_bus\n")
f.write("\t);\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin\n")
f.write("\t\t\talways @(posedge clk) begin\n")
f.write("\t\t\t\tif(rst) begin\n")
f.write("\t\t\t\t\to_data_bus[(i*NUM_PES)*DATA_TYPE +: NUM_PES*DATA_TYPE]  <=  'd0;\n")
f.write("\t\t\t\tend else if(ena) begin\n")
f.write("\t\t\t\t\tcasex(i_data_valid[i*NUM_PES +: NUM_PES])\n")
for i in range(NUM_PES):
    str0 = "\t\t\t\t\t\t" + str(NUM_PES) + "'b"
    for j in range(NUM_PES-i-1):
        str0 += "x"
    str0 += "1"
    for j in range(i):
        str0 += "0"
    str0 += ": o_data_bus[(i*NUM_PES)*DATA_TYPE +: NUM_PES*DATA_TYPE] <= {"
    if(i != NUM_PES - 1):
        str0 += "data_bus[(i*NUM_PES+" + str(i+1) + ")*DATA_TYPE +: (NUM_PES-" + str(i+1) + ")*DATA_TYPE], "
    str0 += "partial_data[i*DATA_TYPE +: DATA_TYPE]"
    if(i == 0):
        str0 += "};\n"
    else:
        str0 += ", data_bus[(i*NUM_PES)*DATA_TYPE +: " + str(i) + "*DATA_TYPE]};\n"
    f.write(str0)
f.write("\t\t\t\t\t\tdefault: o_data_bus[(i*NUM_PES)*DATA_TYPE +: NUM_PES*DATA_TYPE]  <=  data_bus[(i*NUM_PES)*DATA_TYPE +: NUM_PES*DATA_TYPE];\n")
f.write("\t\t\t\t\tendcase\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\to_data_bus[(i*NUM_PES)*DATA_TYPE +: NUM_PES*DATA_TYPE]  <=  data_bus[(i*NUM_PES)*DATA_TYPE +: NUM_PES*DATA_TYPE];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")


f.write("endmodule\n\n\n\n\n\n\n\n\n\n\n")










f.write("module middle_reduct_lvl1 # (\n")
f.write("\tparameter   NUM_PEGS    =   " + str(NUM_PEGS) + ",\n")
f.write("\tparameter   LOG2_PEGS   =   " + str(LOG2_PEGS) + ",\n\n")
f.write("\tparameter   NUM_PES     =   " + str(NUM_PES) + ",\n")
f.write("\tparameter   DATA_TYPE   =   " + str(OUT_DATA_TYPE) + " ) (\n\n")
    
f.write("\tinput                                                           clk,\n")
f.write("\tinput                                                           rst,\n")
f.write("\tinput                                                           ena,\n\n")

f.write("\tinput       [NUM_PEGS * NUM_PES -1 : 0]                         i_data_valid,\n")
f.write("\tinput       [NUM_PEGS * NUM_PES * DATA_TYPE - 1 : 0]            i_data_bus,\n")
f.write("\tinput       [NUM_PEGS * NUM_PES * LOG2_PEGS - 1 : 0]            i_data_rowid,\n\n")

f.write("\toutput  reg                                                     o_data_valid,\n")
f.write("\toutput      [NUM_PEGS * NUM_PEGS * DATA_TYPE - 1 : 0]           o_data_bus\n")
f.write("\t);\n\n")

f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\to_data_valid    <= 'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_data_valid    <=  i_data_valid == 'd0 ? 1'b0 : 1'b1;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin : middle_reduct_lvl1_0_gen\n\n")

f.write("\t\t\tmiddle_reduct_lvl1_0 # (\n")
f.write("\t\t\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\t\t\tmy_middle_reduct_lvl1_0 (\n")
f.write("\t\t\t\t\t.clk(clk),\n")
f.write("\t\t\t\t\t.rst(rst),\n")
f.write("\t\t\t\t\t.ena(ena),\n\n")

f.write("\t\t\t\t\t.i_data_valid(i_data_valid[i*NUM_PES +: NUM_PES]),\n")
f.write("\t\t\t\t\t.i_data_bus(i_data_bus[i*NUM_PES*DATA_TYPE +: NUM_PES*DATA_TYPE]),\n")
f.write("\t\t\t\t\t.i_data_rowid(i_data_rowid[i*NUM_PES*LOG2_PEGS +: NUM_PES*LOG2_PEGS]),\n\n")
                    
f.write("\t\t\t\t\t.o_data_bus(o_data_bus[i*NUM_PEGS*DATA_TYPE +: NUM_PEGS*DATA_TYPE])\n")
f.write("\t\t\t\t);\n\n")

f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

f.write("endmodule\n\n\n")


f.write("module middle_reduct_lvl1_0 # (\n")
f.write("\tparameter   NUM_PEGS    =   " + str(NUM_PEGS) + ",\n")
f.write("\tparameter   LOG2_PEGS   =   " + str(LOG2_PEGS) + ",\n")
f.write("\tparameter   NUM_PES     =   " + str(NUM_PES) + ",\n")
f.write("\tparameter   DATA_TYPE   =   " + str(OUT_DATA_TYPE) + " ) (\n\n")
    
f.write("\tinput                                           clk,\n")
f.write("\tinput                                           rst,\n")
f.write("\tinput                                           ena,\n\n")

f.write("\tinput       [NUM_PES -1 : 0]                    i_data_valid,\n")
f.write("\tinput       [NUM_PES * DATA_TYPE - 1 : 0]       i_data_bus,\n")
f.write("\tinput       [NUM_PES * LOG2_PEGS - 1 : 0]       i_data_rowid,\n\n")

f.write("\toutput  reg [NUM_PEGS * DATA_TYPE - 1 : 0]      o_data_bus\n")
f.write("\t);\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin\n")
f.write("\t\t\talways @(posedge clk) begin\n")
f.write("\t\t\t\tif(rst) begin\n")
f.write("\t\t\t\t\to_data_bus[i*DATA_TYPE +: DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tif(ena) begin\n")
for i in range(NUM_PES):
    str0 = "\t\t\t\t\t\t"
    if(i != 0):
        str0 += "end else "
    str0 += "if(i_data_valid[" + str(i) + "] && i_data_rowid[" + str(i) + "*LOG2_PEGS +: LOG2_PEGS] == i) begin\n"
    f.write(str0)
    str1 = "\t\t\t\t\t\t\to_data_bus[i*DATA_TYPE +: DATA_TYPE] <= i_data_bus[" + str(i) + "*DATA_TYPE +: DATA_TYPE];\n"
    f.write(str1)
f.write("\t\t\t\t\t\tend else begin\n")   
f.write("\t\t\t\t\t\t\to_data_bus[i*DATA_TYPE +: DATA_TYPE] <= 'd0;\n")       
f.write("\t\t\t\t\t\tend\n\n")             

f.write("\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\to_data_bus[i*DATA_TYPE +: DATA_TYPE] <= o_data_bus[i*DATA_TYPE +: DATA_TYPE];\n")
f.write("\t\t\t\t\tend\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")


f.write("endmodule\n")

