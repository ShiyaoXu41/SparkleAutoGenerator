# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
target_path = root_path + "\\vmod\\"


# ================== 2. generate vmod ==================
# ======================================================
from fan_network_func import *

f = open(target_path + "pe_group.v", mode = 'w')

f.write("/////////////////////////////////////////////////////////////////////////\n\n")

f.write("// Description: Sparkle Macro PE-group top level design\n\n")

f.write("/////////////////////////////////////////////////////////////////////////\n\n")

f.write("module pe_group # (\n")
f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ", // number of PE_groups\n")
f.write("\tparameter NUM_PES = " + str(NUM_PES) + ", // number of PES\n")
f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + ",\n")
f.write("\tparameter IN_DATA_TYPE = " + str(IN_DATA_TYPE) + ", // input data type width (BFP16)\n")
f.write("\tparameter OUT_DATA_TYPE = " + str(OUT_DATA_TYPE) + ")( // output data type width (FP32)\n")
f.write("\t\tclk,\n")
f.write("\t\trst,\n")
f.write("\t\ti_data_valid, // input data bus valid\n")
f.write("\t\ti_data_bus, // input data bus\n")
f.write("\t\ti_stationary, // control bit signaling input data is stored in stationary buffer\n")
f.write("\t\ti_dest_bus, // dest bus for xbar network\n")
f.write("\t\ti_vn_seperator, // alternate virtual neuron seperator\n\n")

f.write("\t\to_data_valid, // valid data signals\n")
f.write("\t\to_data_bus // output data bus\n")
f.write(");\n\n")

# f.write("\tparameter IN_DATA_TYPE = 16; // input data type width (BFP16)\n")
# f.write("\tparameter OUT_DATA_TYPE = 32; // output data type width (FP32)\n")
# f.write("\tparameter NUM_PES = " + str(NUM_PES) + "; // number of PES\n")
# f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + \n");\n\n")

f.write("\tinput clk;\n")
f.write("\tinput rst;\n")
f.write("\tinput [NUM_PEGS -1 : 0] i_data_valid;\n")
f.write("\tinput [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0] i_data_bus;\n")
f.write("\tinput [NUM_PEGS -1 : 0] i_stationary;\n")
f.write("\tinput [NUM_PEGS * NUM_PES * LOG2_PES -1:0] i_dest_bus;\n")
f.write("\tinput [NUM_PEGS * NUM_PES * LOG2_PES -1:0] i_vn_seperator;\n\n")
	
f.write("\toutput [NUM_PEGS * NUM_PES -1:0] o_data_valid;\n")
f.write("\toutput [NUM_PEGS * NUM_PES * OUT_DATA_TYPE -1:0] o_data_bus;\n\n")
	
f.write("\twire [NUM_PEGS*(NUM_PES-1)-1:0] w_reduction_add;\n")
f.write("\twire [3*NUM_PEGS*(NUM_PES-1)-1:0] w_reduction_cmd;\n")
# import from general_func->fan_func
NUM_SEL_BITS = get_sel_bits()
f.write("\twire [NUM_PEGS*" + str(NUM_SEL_BITS) + "-1 : 0] w_reduction_sel;\n")
f.write("\twire [NUM_PEGS-1:0] w_reduction_valid;\n\n")

# f.write("\treg [NUM_PES * OUT_DATA_TYPE -1: 0] r_mult;\n\n")
f.write("\twire [NUM_PEGS * NUM_PES * OUT_DATA_TYPE -1: 0] r_mult;\n\n")

f.write("\twire [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0]  w_dist_bus; // output of xbar network\n")
f.write("\twire [NUM_PEGS - 1 : 0] w_mult_valid;\n\n")

f.write("\treg [NUM_PEGS * NUM_PES * IN_DATA_TYPE -1 : 0] r_data_bus_ff, r_data_bus_ff2;\n")
f.write("\treg [NUM_PEGS - 1 : 0] r_data_valid_ff, r_data_valid_ff2;\n")
f.write("\treg [NUM_PEGS - 1 : 0] r_stationary_ff, r_stationary_ff2;\n")
f.write("\treg [NUM_PEGS * NUM_PES * LOG2_PES -1:0] r_dest_bus_ff, r_dest_bus_ff2;\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor (i=0; i < NUM_PEGS; i=i+1) begin\n\n")

f.write("\t\t\t// adjust some input signal delays from xbar and controller\n")
f.write("\t\t\talways @ (posedge clk) begin\n")
f.write("\t\t\t\tr_data_bus_ff[(i+1) * NUM_PES * IN_DATA_TYPE -1 : i * NUM_PES * IN_DATA_TYPE] <= i_data_bus[(i+1) * NUM_PES * IN_DATA_TYPE -1 : i * NUM_PES * IN_DATA_TYPE];\n")
f.write("\t\t\t\tr_data_bus_ff2[(i+1) * NUM_PES * IN_DATA_TYPE -1 : i * NUM_PES * IN_DATA_TYPE] <= r_data_bus_ff[(i+1) * NUM_PES * IN_DATA_TYPE -1 : i * NUM_PES * IN_DATA_TYPE];\n")
f.write("\t\t\t\tr_data_valid_ff[i] <= i_data_valid[i];\n")
f.write("\t\t\t\tr_data_valid_ff2[i] <= r_data_valid_ff[i];\n")
f.write("\t\t\t\tr_stationary_ff[i] <= i_stationary[i];\n")
f.write("\t\t\t\tr_stationary_ff2[i] <= r_stationary_ff[i];\n")
f.write("\t\t\t\tr_dest_bus_ff[(i+1) * NUM_PES * LOG2_PES -1 : i * NUM_PES * LOG2_PES] <= i_dest_bus[(i+1) * NUM_PES * LOG2_PES -1 : i * NUM_PES * LOG2_PES];\n")
f.write("\t\t\t\tr_dest_bus_ff2[(i+1) * NUM_PES * LOG2_PES -1 : i * NUM_PES * LOG2_PES] <= r_dest_bus_ff[(i+1) * NUM_PES * LOG2_PES -1 : i * NUM_PES * LOG2_PES];\n")
f.write("\t\t\tend\n\n")

f.write("\t\t\t// instantize controller\n")
f.write("\t\t\tfan_ctrl #(\n")
f.write("\t\t\t\t.DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t\t\t.LOG2_PES(LOG2_PES))\n")
f.write("\t\t\t\tmy_fan_ctrl (\n")
f.write("\t\t\t\t.clk(clk),\n")
f.write("\t\t\t\t.rst(rst),\n")
f.write("\t\t\t\t.i_vn(i_vn_seperator[i*NUM_PES*LOG2_PES +: NUM_PES*LOG2_PES]),\n")
f.write("\t\t\t\t.i_stationary(i_stationary[i]),\n")
f.write("\t\t\t\t.i_data_valid(i_data_valid[i]),\n")
f.write("\t\t\t\t.o_reduction_add(w_reduction_add[(i+1)*(NUM_PES-1)-1:i*(NUM_PES-1)]),\n")
f.write("\t\t\t\t.o_reduction_cmd(w_reduction_cmd[3*(i+1)*(NUM_PES-1)-1:3*i*(NUM_PES-1)]),\n")
f.write("\t\t\t\t.o_reduction_sel(w_reduction_sel[(i+1)*"+str(NUM_SEL_BITS)+"-1:i*"+str(NUM_SEL_BITS)+"]),\n")
f.write("\t\t\t\t.o_reduction_valid(w_reduction_valid[i])\n")
f.write("\t\t\t);\n\n")

f.write("\t\t\t// instantize distribution network  (xbar)\n")
f.write("\t\t\txbar #(\n")
f.write("\t\t\t\t.DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t\t\t.INPUT_BW(NUM_PES),\n")
f.write("\t\t\t\t.LOG2_PES(LOG2_PES))\n")
f.write("\t\t\t\tmy_xbar (\n")
f.write("\t\t\t\t.clk(clk),\n")
f.write("\t\t\t\t.rst(rst),\n")
f.write("\t\t\t\t.i_data_bus(r_data_bus_ff2[(i+1) * NUM_PES * IN_DATA_TYPE -1 : i * NUM_PES * IN_DATA_TYPE]),\n")
f.write("\t\t\t\t.i_mux_bus(r_dest_bus_ff2[(i+1) * NUM_PES * LOG2_PES -1 : i * NUM_PES * LOG2_PES]),\n")
f.write("\t\t\t\t.o_dist_bus(w_dist_bus[(i+1)*NUM_PES*IN_DATA_TYPE-1:i*NUM_PES*IN_DATA_TYPE])\n")
f.write("\t\t\t);\n\n")
	
f.write("\t\t\t// generate multiplier chain (output of xbar to input of multiplier chain)\n")
f.write("\t\t\tmult_gen #(\n")
f.write("\t\t\t\t.IN_DATA_TYPE(IN_DATA_TYPE),\n")
f.write("\t\t\t\t.OUT_DATA_TYPE(OUT_DATA_TYPE),\n")
f.write("\t\t\t\t.NUM_PES(NUM_PES))\n")
f.write("\t\t\t\tmy_mult_gen (\n")
f.write("\t\t\t\t.clk(clk),\n")
f.write("\t\t\t\t.rst(rst),\n")
f.write("\t\t\t\t.i_valid(r_data_valid_ff2[i]),\n")
f.write("\t\t\t\t.i_data_bus(w_dist_bus[(i+1)*NUM_PES*IN_DATA_TYPE-1:i*NUM_PES*IN_DATA_TYPE]),\n")
f.write("\t\t\t\t.i_stationary(r_stationary_ff2[i]),\n")
f.write("\t\t\t\t.o_valid(w_mult_valid[i]),\n")
f.write("\t\t\t\t.o_data_bus(r_mult[(i+1)*NUM_PES*OUT_DATA_TYPE-1:i*NUM_PES*OUT_DATA_TYPE])\n")
f.write("\t\t\t);\n\n")
	
f.write("\t\t\t// instantiate fan reduction topology\n")
f.write("\t\t\tfan_network #(\n")
f.write("\t\t\t\t.DATA_TYPE(OUT_DATA_TYPE),\n")
f.write("\t\t\t\t.NUM_PES(NUM_PES),\n")
f.write("\t\t\t\t.LOG2_PES(LOG2_PES))\n")
f.write("\t\t\t\tmy_fan_network (\n")
f.write("\t\t\t\t.clk(clk),\n")
f.write("\t\t\t\t.rst(rst),\n")
f.write("\t\t\t\t.i_valid(w_reduction_valid[i]),\n")
f.write("\t\t\t\t.i_data_bus(r_mult[(i+1)*NUM_PES*OUT_DATA_TYPE-1:i*NUM_PES*OUT_DATA_TYPE]),\n")
f.write("\t\t\t\t.i_add_en_bus(w_reduction_add[(i+1)*(NUM_PES-1)-1:i*(NUM_PES-1)]),\n")
f.write("\t\t\t\t.i_cmd_bus(w_reduction_cmd[3*(i+1)*(NUM_PES-1)-1:3*i*(NUM_PES-1)]),\n")
f.write("\t\t\t\t.i_sel_bus(w_reduction_sel[(i+1)*"+str(NUM_SEL_BITS)+"-1:i*"+str(NUM_SEL_BITS)+"]),\n")
f.write("\t\t\t\t.o_valid(o_data_valid[(i+1)*NUM_PES-1:i*NUM_PES]),\n")
f.write("\t\t\t\t.o_data_bus(o_data_bus[(i+1)*NUM_PES*OUT_DATA_TYPE-1:i*NUM_PES*OUT_DATA_TYPE])\n")
f.write("\t\t\t);\n\n")

f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

f.write("endmodule\n")



