# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
target_path = root_path + "\\vmod\\"


# ================== 2. generate vmod ==================
# ======================================================
f = open(target_path + "results_accum.v", mode = 'w')

f.write("module results_accum_lvl0 # (\n")
f.write("\tparameter   NUM_PEGS        =   " + str(NUM_PEGS) +",\n")
f.write("\tparameter   LOG2_PEGS       =   " + str(LOG2_PEGS) +",\n")
f.write("\tparameter   DATA_TYPE       =   " + str(OUT_DATA_TYPE) +",\n")
f.write("\tparameter   PARA_BLOCKS     =   " + str(PARA_BLOCKS) + ") (\n\n")

f.write("\tinput                                                               clk,\n")
f.write("\tinput                                                               rst,\n\n")

f.write("\tinput           [NUM_PEGS -1:0]                                     i_data_valid,\n")
f.write("\tinput           [NUM_PEGS * NUM_PEGS * DATA_TYPE -1:0]              i_data_bus,\n\n")

f.write("\toutput  reg     [PARA_BLOCKS:0]                                     o_data_valid,\n")
f.write("\toutput  reg     [(PARA_BLOCKS + 1) * NUM_PEGS * DATA_TYPE -1:0]     o_data_bus,\n")
f.write("\toutput  reg     [LOG2_PEGS:0]                                       o_data_num\n\n")

f.write(");\n\n")

f.write("\t// get num of block results\n\n")

f.write("\twire    [(LOG2_PEGS+1)*NUM_PEGS-1:0] w_results_block_row_idx;\n\n")

f.write("\tpresum_" + str(NUM_PEGS) + " my_presum_" + str(NUM_PEGS) + " (\n")
f.write("\t\t.din(i_data_valid),\n")
f.write("\t\t.dout(w_results_block_row_idx)\n")
f.write("\t);\n\n\n")


f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
# f.write("\t\t\to_data_valid    <=  1'b0;\n")
f.write("\t\t\to_data_num      <=  'd0;\n")
f.write("\t\tend else begin\n")
# f.write("\t\t\to_data_valid    <=  i_data_valid;\n")
f.write("\t\t\to_data_num      <=  w_results_block_row_idx[(LOG2_PEGS+1)*(NUM_PEGS-1) +: (LOG2_PEGS+1)];\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


# f.write("\treg     [(LOG2_PEGS+1)*NUM_PEGS-1:0] r_results_block_row_idx;\n\n")

# f.write("\talways @(posedge clk) begin\n")
# f.write("\t\tif(rst) begin\n")
# f.write("\t\t\tr_results_block_row_idx <=  'd0;\n")
# f.write("\t\tend else begin\n")
# f.write("\t\t\tr_results_block_row_idx <=  w_results_block_row_idx;\n")
# f.write("\t\tend\n")
# f.write("\tend\n\n\n")


f.write("\tgenvar j;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(j = 0; j < PARA_BLOCKS + 1; j = j + 1) begin\n")
f.write("\t\t\talways @(posedge clk) begin\n")
for i in range(NUM_PEGS):
    str0 = "\t\t\t\t"
    if(i != 0):
        str0 += "end else "
    # str0 += "if(w_results_block_row_idx["+str(6*(i+1)-1)+":"+str(6*i)+"] == j+1) begin\n"
    str0 += "if(w_results_block_row_idx["+str(i)+"*(LOG2_PEGS+1) +: (LOG2_PEGS+1)] == j+1) begin\n"
    f.write(str0)
    str1 = "\t\t\t\t\to_data_bus[j*NUM_PEGS*DATA_TYPE +: NUM_PEGS*DATA_TYPE] <= i_data_bus[" + str(i) + "*NUM_PEGS*DATA_TYPE +: NUM_PEGS*DATA_TYPE];\n"
    f.write(str1)
    f.write("\t\t\t\t\to_data_valid[j] <= 1'b1;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\to_data_bus[j*NUM_PEGS*DATA_TYPE +: NUM_PEGS*DATA_TYPE] <= 'd0;\n")
f.write("\t\t\t\t\to_data_valid[j] <= 1'b0;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")


f.write("endmodule\n\n\n\n\n\n")





f.write("module results_accum_lvl1 # (\n")
f.write("\tparameter   NUM_PEGS    =   " + str(NUM_PEGS) +",\n")
f.write("\tparameter   LOG2_PEGS   =   " + str(LOG2_PEGS) +",\n")
f.write("\tparameter   DATA_TYPE   =   " + str(OUT_DATA_TYPE) +",\n")
f.write("\tparameter   PARA_BLOCKS =   " + str(PARA_BLOCKS) + ",\n")
f.write("\tparameter   MAX_N_DIM   =   " + str(MAX_N_DIM) + ") (\n\n")
    
f.write("\tinput                                                       clk,\n")
f.write("\tinput                                                       rst,\n")
f.write("\tinput       [20 : 0]                                        N_DIM,\n\n")

f.write("\tinput       [PARA_BLOCKS:0]                                 i_data_valid,\n")
f.write("\tinput       [(PARA_BLOCKS + 1) * NUM_PEGS * DATA_TYPE -1:0] i_data_bus,\n")
f.write("\tinput       [LOG2_PEGS:0]                                   i_data_num,\n")
f.write("\tinput       [1:0]                                           i_accum_ena,\n\n")

f.write("\toutput  reg [PARA_BLOCKS:0]                                 o_data_valid,\n")
f.write("\toutput  reg [(PARA_BLOCKS + 1) * NUM_PEGS * DATA_TYPE -1:0] o_data_bus\n")
f.write(");\n\n\n")


f.write("\t// counter to count columns\n")
f.write("\treg     [10 : 0]    results_col_counter;\n")
f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\tresults_col_counter <=  'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tif(i_data_valid != 'd0) begin\n")
f.write("\t\t\t\tif(results_col_counter == N_DIM - 1) begin\n")
f.write("\t\t\t\t\tresults_col_counter <=  'd0;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tresults_col_counter <=  results_col_counter + 1'b1;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\tresults_col_counter <=  results_col_counter;\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("\t// accumulate into partial results (or not)\n")
f.write("\treg     [NUM_PEGS * DATA_TYPE - 1 : 0]  partial_results [0 : MAX_N_DIM];\n\n")

f.write("\twire    [NUM_PEGS * DATA_TYPE - 1 : 0]  w_adder_a;\n")
f.write("\twire    [NUM_PEGS * DATA_TYPE - 1 : 0]  w_adder_o;\n\n")

f.write("\tassign  w_adder_a   =   partial_results[results_col_counter];\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin\n\n")

f.write("\t\t\t// instantiate INTx adder\n")
f.write("\t\t\t// IP CORE\n")
f.write("\t\t\tAdder_%d my_Adder_%d (\n" % (OUT_DATA_TYPE, OUT_DATA_TYPE))
f.write("\t\t\t\t.A(w_adder_a[i*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t\t.B(i_data_bus[i*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t\t.CLK(clk),\n")
f.write("\t\t\t\t.S(w_adder_o[i*DATA_TYPE +: DATA_TYPE])\n")
f.write("\t\t\t);\n\n")

f.write("\t\t\t// adder_n # (\n")
f.write("\t\t\t// 	.IN_DATA_TYPE(DATA_TYPE),\n")
f.write("\t\t\t// 	.OUT_DATA_TYPE(DATA_TYPE))\n")
f.write("\t\t\t// 	my_adder_n (\n")
f.write("\t\t\t// 	.clk(clk),\n")
f.write("\t\t\t// 	.rst(rst),\n")
f.write("\t\t\t// 	.A(w_adder_a[i*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t// 	.B(i_data_bus[i*DATA_TYPE +: DATA_TYPE]),\n")
f.write("\t\t\t// 	.O(w_adder_o[i*DATA_TYPE +: DATA_TYPE])\n")
f.write("\t\t\t// );\n\n")

f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")


f.write("\t// registers\n")
f.write("\treg     [PARA_BLOCKS:0]                                 i_data_valid_ff;\n")
f.write("\treg     [(PARA_BLOCKS + 1) * NUM_PEGS * DATA_TYPE -1:0] i_data_bus_ff;\n")
f.write("\treg     [LOG2_PEGS:0]                                   i_data_num_ff;\n")
f.write("\treg     [1:0]                                           i_accum_ena_ff;\n")
f.write("\treg     [10 : 0]                                        results_col_counter_ff;\n\n")

f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\ti_data_valid_ff         <=  'd0;\n")
f.write("\t\t\ti_data_bus_ff           <=  'd0;\n")
f.write("\t\t\ti_data_num_ff           <=  'd0;\n")
f.write("\t\t\ti_accum_ena_ff          <=  'd0;\n")
f.write("\t\t\tresults_col_counter_ff  <=  'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\ti_data_valid_ff         <=  i_data_valid;\n")
f.write("\t\t\ti_data_bus_ff           <=  i_data_bus;\n")
f.write("\t\t\ti_data_num_ff           <=  i_data_num;\n")
f.write("\t\t\ti_accum_ena_ff          <=  i_accum_ena;\n")
f.write("\t\t\tresults_col_counter_ff  <=  results_col_counter;\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("\t// partial_results store i_data or adder_o\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < MAX_N_DIM; i = i + 1) begin\n")
f.write("\t\t\talways @(posedge clk) begin\n")
f.write("\t\t\t\tif(rst) begin\n")
f.write("\t\t\t\t\tpartial_results[i]  <=  'd0;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tif(i_data_valid_ff == 'd0 || i != results_col_counter_ff) begin\n")
f.write("\t\t\t\t\t\tpartial_results[i]  <=  partial_results[i];\n")
f.write("\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\tif(i_accum_ena_ff[1] == 1'b0) begin\n")
f.write("\t\t\t\t\t\t\tpartial_results[i]  <=  'd0;\n")
f.write("\t\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\t\tif(i_data_num_ff > 'd1) begin\n")
f.write("\t\t\t\t\t\t\t\tpartial_results[i]  <=  i_data_bus_ff[(i_data_num_ff-1)*NUM_PEGS*DATA_TYPE +: NUM_PEGS*DATA_TYPE];\n")
f.write("\t\t\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\t\t\tpartial_results[i]  <=  w_adder_o;\n")
f.write("\t\t\t\t\t\t\tend\n")
f.write("\t\t\t\t\t\tend\n")
f.write("\t\t\t\t\tend\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n\n")
            
    
f.write("\t// results\n")
f.write("\talways @(posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\to_data_valid    <=  'd0;\n")
f.write("\t\t\to_data_bus      <=  'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tif(i_accum_ena_ff == 2'b00) begin\n")
f.write("\t\t\t\to_data_valid    <=  i_data_valid_ff;\n")
f.write("\t\t\t\to_data_bus      <=  i_data_bus_ff;\n")
f.write("\t\t\tend else if(i_accum_ena_ff == 2'b10) begin  // accumulate with the next one\n")
for i in range(PARA_BLOCKS):
    str0 = "\t\t\t\t"
    if(i != 0):
        str0 += "end else "
    str0 += "if(i_data_valid_ff[PARA_BLOCKS-" + str(i) + "] == 1'b1) begin\n"
    f.write(str0)
    str0 = "\t\t\t\t\to_data_valid    <=  {" + str(i+1) + "'d0, i_data_valid_ff[PARA_BLOCKS-" + str(i+1) + ":0]};\n"
    f.write(str0)
    str0 = "\t\t\t\t\to_data_bus      <=  {{(" + str(i+1) + "*(NUM_PEGS*DATA_TYPE)){1'b0}}, i_data_bus_ff[(PARA_BLOCKS-" + str(i) + ")*(NUM_PEGS*DATA_TYPE)-1:0]};\n"
    f.write(str0)
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\to_data_valid    <=  'd0;\n")
f.write("\t\t\t\t\to_data_bus      <=  'd0;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend else if(i_accum_ena_ff == 2'b01) begin  // accumulate with the last one\n")
f.write("\t\t\t\to_data_valid    <=  i_data_valid_ff;\n")
f.write("\t\t\t\to_data_bus      <=  {i_data_bus_ff[(PARA_BLOCKS+1)*(NUM_PEGS*DATA_TYPE)-1:(NUM_PEGS*DATA_TYPE)], w_adder_o};\n")
f.write("\t\t\tend else if(i_accum_ena_ff == 2'b11) begin  // accumulate with the last and the next one\n")
for i in range(PARA_BLOCKS):
    str0 = "\t\t\t\t"
    if(i != 0):
        str0 += "end else "
    str0 += "if(i_data_valid_ff[PARA_BLOCKS-" + str(i) + "] == 1'b1) begin\n"
    f.write(str0)
    str0 = "\t\t\t\t\to_data_valid    <=  {" + str(i+1) + "'d0, i_data_valid_ff[PARA_BLOCKS-" + str(i+1) + ":0]};\n"
    f.write(str0)
    if(i != PARA_BLOCKS-1):
        str0 = "\t\t\t\t\to_data_bus      <=  {{(" + str(i+1) + "*(NUM_PEGS*DATA_TYPE)){1'b0}}, i_data_bus_ff[(PARA_BLOCKS-" + str(i) + ")*(NUM_PEGS*DATA_TYPE)-1:(NUM_PEGS*DATA_TYPE)], w_adder_o};\n"
    else:
        str0 = "\t\t\t\t\to_data_bus      <=  {{(" + str(i+1) + "*(NUM_PEGS*DATA_TYPE)){1'b0}}, w_adder_o};\n"
    f.write(str0)
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\to_data_valid    <=  'd0;\n")
f.write("\t\t\t\t\to_data_bus      <=  'd0;\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tend\n\n\n")


f.write("endmodule\n")


