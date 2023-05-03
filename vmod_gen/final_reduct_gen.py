# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
target_path = root_path + "\\vmod\\"


# ================== 2. generate vmod ==================
# ======================================================
from multi_fan_general_func import *

f = open(target_path + "final_reduct.v", mode = 'w')

f.write("/////////////////////////////////////////////////////////////////////////\n")
f.write("// Design: final_reduct.v\n")
f.write("// Description: An input-expanded FAN network\n")
f.write("/////////////////////////////////////////////////////////////////////////\n\n\n")


f.write("module final_reduct # (\n")
f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ",\n")
f.write("\tparameter LOG2_PEGS = " + str(LOG2_PEGS) + ",\n")
f.write("\tparameter DATA_TYPE = " + str(OUT_DATA_TYPE) + ")(\n")
f.write("\tclk,\n")
f.write("\trst,\n")
f.write("\ti_data_valid, // input data bus valid\n")
f.write("\ti_data_bus, // input data bus\n")
f.write("\ti_vn_seperator, // alternate virtual neuron seperator\n\n")

f.write("\to_data_valid, // valid data signals\n")
f.write("\to_data_bus // output data bus\n\n")

f.write(");\n\n")

f.write("\tinput clk;\n")
f.write("\tinput rst;\n")
f.write("\tinput i_data_valid;\n")
f.write("\tinput [NUM_PEGS * NUM_PEGS * DATA_TYPE -1 : 0] i_data_bus;\n")
f.write("\tinput [NUM_PEGS * LOG2_PEGS -1:0] i_vn_seperator;\n\n")

f.write("\toutput [NUM_PEGS -1:0] o_data_valid;\n")
f.write("\toutput [NUM_PEGS * NUM_PEGS * DATA_TYPE -1:0] o_data_bus;\n\n")

f.write("\twire [(NUM_PEGS-1)-1:0] w_reduction_add;\n")
f.write("\twire [3*(NUM_PEGS-1)-1:0] w_reduction_cmd;\n")
NUM_SEL_BITS = get_sel_bits()
f.write("\twire [" +  str(int(NUM_SEL_BITS- 1)) + " : 0] w_reduction_sel;\n")
# f.write("\twire [19 : 0] w_reduction_sel;\n")
f.write("\twire w_reduction_valid;\n\n")


f.write("\treg  [NUM_PEGS * NUM_PEGS * DATA_TYPE -1 : 0] r_data_bus_ff, r_data_bus_ff2, r_data_bus_ff3, r_data_bus_ff4;\n\n")

f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif(rst) begin\n")
f.write("\t\t\tr_data_bus_ff <= 'd0;\n")
f.write("\t\t\tr_data_bus_ff2 <= 'd0;\n")
f.write("\t\t\tr_data_bus_ff3 <= 'd0;\n")
f.write("\t\t\tr_data_bus_ff4 <= 'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_data_bus_ff <= i_data_bus;\n")
f.write("\t\t\tr_data_bus_ff2 <= r_data_bus_ff;\n")
f.write("\t\t\tr_data_bus_ff3 <= r_data_bus_ff2;\n")
f.write("\t\t\tr_data_bus_ff4 <= r_data_bus_ff3;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")


f.write("\t// instantize controller\n")
f.write("\tmulti_fan_ctrl # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.LOG2_PEGS(LOG2_PEGS),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\tmy_multi_fan_ctrl (\n")
f.write("\t\t.clk(clk),\n")
f.write("\t\t.rst(rst),\n")
f.write("\t\t.i_vn(i_vn_seperator),\n")
f.write("\t\t.i_stationary(1'b0),\n")
f.write("\t\t.i_data_valid(i_data_valid),\n\n")
		
f.write("\t\t.o_reduction_add(w_reduction_add),\n")
f.write("\t\t.o_reduction_cmd(w_reduction_cmd),\n")
f.write("\t\t.o_reduction_sel(w_reduction_sel),\n")
f.write("\t\t.o_reduction_valid(w_reduction_valid)\n")
f.write("\t);\n\n")

f.write("\t// instantiate fan reduction topology\n")
f.write("\tmulti_fan_network # (\n")
f.write("\t\t.NUM_PEGS(NUM_PEGS),\n")
f.write("\t\t.DATA_TYPE(DATA_TYPE))\n")
f.write("\t\tmy_multi_fan_network (\n")
f.write("\t\t.clk(clk),\n")
f.write("\t\t.rst(rst),\n")
f.write("\t\t.i_valid(w_reduction_valid),\n")
f.write("\t\t.i_data_bus(r_data_bus_ff4),\n")
f.write("\t\t.i_add_en_bus(w_reduction_add),\n")
f.write("\t\t.i_cmd_bus(w_reduction_cmd),\n")
f.write("\t\t.i_sel_bus(w_reduction_sel),\n\n")

f.write("\t\t.o_valid(o_data_valid),\n")
f.write("\t\t.o_data_bus(o_data_bus)\n")
f.write("\t);\n\n")

f.write("endmodule\n\n")





