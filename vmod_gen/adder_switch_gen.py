# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
target_path = root_path + "\\vmod\\"


# ================== 2. generate vmod ==================
# ======================================================
prefx_f = ["", "edge_", "reduct_", "reduct_edge_"]

for pf in prefx_f:

    f = open(target_path + pf + "adder_switch.v", mode = 'w')

    f.write("/////////////////////////////////////////////////////////////////////////\n")
    f.write("// Design: " + pf + "adder_switch.v\n")
    f.write("// Description: INTx Adder with Forwarding functionality\n")
    if("edge" in pf):
        f.write("// for edge adders\n")
    f.write("/////////////////////////////////////////////////////////////////////////\n\n")

    f.write("module " + pf + "adder_switch # (\n")
    if("reduct" in pf):
        f.write("\tparameter NUM_PEGS = " + str(NUM_PEGS) + ",\n")
    f.write("\tparameter DATA_TYPE = " + str(OUT_DATA_TYPE) + ",\n")
    f.write("\tparameter NUM_IN = 4,\n")
    f.write("\tparameter SEL_IN = 2) (\n")
    f.write("\tclk,\n")
    f.write("\trst,\n\n")
        
    f.write("\ti_valid, // valid data signal\n")
    f.write("\ti_data_bus, // input data bus coming into adder switch\n\n")
        
    f.write("\t// reconfigurable control signal\n")
    f.write("\ti_add_en, // add enable\n")
    f.write("\ti_cmd, // command to add or forward\n")
    f.write("\ti_sel, // reduction mux select bits\n\n")
        
    f.write("\to_vn, // vn output\n")
    f.write("\to_vn_valid, // vn output valid\n\n")
        
    f.write("\to_adder // output of the adders (can be sum or forwarding)\n")
    f.write(");\n\n")

    if("edge" in pf):
        f.write("\tparameter NUM_OUT = 1;\n\n")
    else:
        f.write("\tparameter NUM_OUT = 2;\n\n")

    f.write("\tinput clk;\n")
    f.write("\tinput rst;\n\n")
        
    f.write("\tinput i_valid; // input data valid\n")
    if("reduct" in pf):
        f.write("\tinput [(NUM_PEGS*DATA_TYPE*NUM_IN)-1:0] i_data_bus; // input data bus to select from\n\n")
    else:
        f.write("\tinput [(DATA_TYPE*NUM_IN)-1:0] i_data_bus; // input data bus to select from\n\n")
        
    f.write("\tinput i_add_en;\n")
    f.write("\tinput [2:0] i_cmd; // Adder functionality bits\n")
    f.write("\t\t// 000 --> NA\n")
    if("edge" in pf):
        f.write("\t\t// 001 --> NA\n")
        f.write("\t\t// 010 --> add data and forward to one path\n")
    else:
        f.write("\t\t// 001 --> forward both original data (left to left, right to right) -  REMOVED bypass regardless\n")
        f.write("\t\t// 010 --> add data and forward to both paths\n")
    f.write("\t\t// 011 --> send left input as VN output and forward right input\n")
    f.write("\t\t// 100 --> send right input as VN output and forward left input\n")
    f.write("\t\t// 101 --> send both inputs as VN outputs\n\n")
    
    f.write("\tinput [SEL_IN-1:0] i_sel; // select bits for the reduction mux\n\n")
    
    if("reduct" in pf):
        f.write("\toutput reg [(2*NUM_PEGS*DATA_TYPE)-1:0] o_vn; // vn output\n")
    else:
        f.write("\toutput reg [(2*DATA_TYPE)-1:0] o_vn; // vn output\n")
    f.write("\toutput reg [1:0] o_vn_valid; // vn output valid\n\n")

    str0 = "\toutput reg [("
    if("reduct" in pf):
        str0 += "NUM_PEGS*"
    str0 += "DATA_TYPE*NUM_OUT)-1:0] o_adder; // output of the adders "
    if("edge" in pf):
        str0 += "(only one for edge adder)\n\n"
    else:
        str0 += "(can be sum or forwarding), upper half --> left, lower half --> right\n\n"
    f.write(str0)
    
    if("edge" in pf):
        f.write("\t// reg r_valid;\n\n")

    if("reduct" in pf):
        f.write("\twire [(2 * NUM_PEGS*DATA_TYPE)-1:0] w_sel_data; // selected data from reduction mux\n\n")
    else:
        f.write("\twire [(2 * DATA_TYPE)-1:0] w_sel_data; // selected data from reduction mux\n\n")
    
    if("reduct" in pf):
        f.write("\twire [NUM_PEGS*DATA_TYPE-1:0] w_O; // output of adder\n\n")
    else:
        f.write("\twire [DATA_TYPE-1:0] w_O; // output of adder\n\n")
        
    if("reduct" in pf):
        f.write("\treg [(NUM_PEGS*DATA_TYPE*NUM_OUT)-1:0] r_adder;\n\n")
    else:
        f.write("\treg [(DATA_TYPE*NUM_OUT)-1:0] r_adder;\n\n")
        
    f.write("\treg r_add_en;\n")
    if("reduct" in pf):
        f.write("\treg [(2*NUM_PEGS*DATA_TYPE)-1:0] r_vn;\n")
    else:
        f.write("\treg [(2*DATA_TYPE)-1:0] r_vn;\n")
    f.write("\treg [1:0] r_vn_valid;\n\n")
        
        
    f.write("\t// generate mux logic to select input data bus values to the two inputs of the adder\n")
    f.write("\treduction_mux # (\n")
    if("reduct" in pf):
        f.write("\t\t.W(NUM_PEGS*DATA_TYPE),\n")
    else:
        f.write("\t\t.W(DATA_TYPE),\n")
    f.write("\t\t.NUM_IN(NUM_IN),\n")
    f.write("\t\t.SEL_IN(SEL_IN),\n")
    if("edge" in pf):
        f.write("\t\t.NUM_OUT(2)) my_reduction_mux (\n")
    else:
        f.write("\t\t.NUM_OUT(NUM_OUT)) my_reduction_mux (\n")
    f.write("\t\t.i_data(i_data_bus),\n")
    f.write("\t\t.i_sel(i_sel),\n")
    f.write("\t\t.o_data(w_sel_data)\n")
    f.write("\t);\n\n")
        
    f.write("\t// Reconfigurable control logic select\n")
    f.write("\talways @ (posedge clk) begin\n")
    f.write("\t\tif (rst == 1'b1) begin\n")
    f.write("\t\t\tr_adder <= 'b0;\n")
    f.write("\t\t\tr_vn <= 'b0;\n")
    f.write("\t\t\tr_vn_valid <= 'b0;\n")
    f.write("\t\tend else begin\n")
    f.write("\t\t\tif (i_valid == 1'b1) begin\n")
    f.write("\t\t\t\tcase (i_cmd)\n")
    f.write("\t\t\t\t\t3'b000 : begin\n")
    f.write("\t\t\t\t\t\t// NA\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b00;\n")
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\t\t3'b001 : begin\n")
    if("edge" in pf):
        f.write("\t\t\t\t\t\t// NA\n")
    else:
        f.write("\t\t\t\t\t\t//forward both original data (left to left, right to right)\n")
        f.write("\t\t\t\t\t\tr_adder <= w_sel_data;\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b00;\n")
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\t\t3'b010 : begin\n")
    f.write("\t\t\t\t\t\t// NA\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b00;\n")
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\t\t3'b011 : begin\n")
    f.write("\t\t\t\t\t\t// send left input as VN output and forward right input\n")
    ###
    if("reduct_edge_" in pf):
        f.write("\t\t\t\t\t\tr_adder <= w_sel_data[2*NUM_PEGS*DATA_TYPE-1:NUM_PEGS*DATA_TYPE];\n")
    elif("reduct_" in pf):
        f.write("\t\t\t\t\t\tr_adder[2*NUM_PEGS*DATA_TYPE-1:NUM_PEGS*DATA_TYPE] <= w_sel_data[2*NUM_PEGS*DATA_TYPE-1:NUM_PEGS*DATA_TYPE];\n")
    elif("edge_" in pf):
        f.write("\t\t\t\t\t\tr_adder <= w_sel_data[2*DATA_TYPE-1:DATA_TYPE];\n")
    else:
        f.write("\t\t\t\t\t\tr_adder[2*DATA_TYPE-1:DATA_TYPE] <= w_sel_data[2*DATA_TYPE-1:DATA_TYPE];\n")
    ###
    if("reduct" in pf):
        f.write("\t\t\t\t\t\tr_vn[NUM_PEGS*DATA_TYPE-1:0] <= i_data_bus[NUM_PEGS*DATA_TYPE-1:0];\n")
    else:
        f.write("\t\t\t\t\t\tr_vn[DATA_TYPE-1:0] <= i_data_bus[DATA_TYPE-1:0];\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b01;\n")
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\t\t3'b100 : begin\n")
    f.write("\t\t\t\t\t\t// send right input as VN output and forward left input\n")
    ###
    if("reduct_edge_" in pf):
        f.write("\t\t\t\t\t\tr_adder <= w_sel_data[NUM_PEGS*DATA_TYPE-1:0];\n")
    elif("reduct_" in pf):
        f.write("\t\t\t\t\t\tr_adder[NUM_PEGS*DATA_TYPE-1:0] <= w_sel_data[NUM_PEGS*DATA_TYPE-1:0];\n")
    elif("edge_" in pf):
        f.write("\t\t\t\t\t\tr_adder <= w_sel_data[DATA_TYPE-1:0];\n")
    else:
        f.write("\t\t\t\t\t\tr_adder[DATA_TYPE-1:0] <= w_sel_data[DATA_TYPE-1:0];\n")
    ###
    if("reduct" in pf):
        f.write("\t\t\t\t\t\tr_vn[2*NUM_PEGS*DATA_TYPE-1:NUM_PEGS*DATA_TYPE] <= i_data_bus[(NUM_PEGS*DATA_TYPE*NUM_IN)-1:NUM_PEGS*DATA_TYPE*(NUM_IN-1)];\n")
    else:
        f.write("\t\t\t\t\t\tr_vn[2*DATA_TYPE-1:DATA_TYPE] <= i_data_bus[(DATA_TYPE*NUM_IN)-1:DATA_TYPE*(NUM_IN-1)];\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b10;\n")
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\t\t3'b101: begin\n")
    f.write("\t\t\t\t\t\t// send both inputs as VN outputs\n")
    f.write("\t\t\t\t\t\t// r_vn <= w_sel_data;\n")
    if("reduct" in pf):
        f.write("\t\t\t\t\t\tr_vn[NUM_PEGS*DATA_TYPE-1:0] <= i_data_bus[NUM_PEGS*DATA_TYPE-1:0];\n")
        f.write("\t\t\t\t\t\tr_vn[2*NUM_PEGS*DATA_TYPE-1:NUM_PEGS*DATA_TYPE] <= i_data_bus[(NUM_PEGS*DATA_TYPE*NUM_IN)-1:NUM_PEGS*DATA_TYPE*(NUM_IN-1)];\n")
    else:
        f.write("\t\t\t\t\t\tr_vn[DATA_TYPE-1:0] <= i_data_bus[DATA_TYPE-1:0];\n")
        f.write("\t\t\t\t\t\tr_vn[2*DATA_TYPE-1:DATA_TYPE] <= i_data_bus[(DATA_TYPE*NUM_IN)-1:DATA_TYPE*(NUM_IN-1)];\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b11;\n")			
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\t\tdefault: begin\n")
    f.write("\t\t\t\t\t\t// nothing happens, adder inactive\n")
    f.write("\t\t\t\t\t\tr_vn_valid <= 2'b00;\n")
    f.write("\t\t\t\t\tend\n")
    f.write("\t\t\t\tendcase\n")
    f.write("\t\t\tend\n")
    f.write("\t\tend\n")
    f.write("\tend\n\n")
        
    f.write("\t// flop i_cmd for timing logic\n")
    f.write("\talways @ (posedge clk) begin\n")
    f.write("\t\tif (rst == 1'b1) begin\n")
    f.write("\t\t\tr_add_en <= 'b0;\n")
    f.write("\t\tend else begin\n")
    f.write("\t\t\tr_add_en <= i_add_en;\n")
    f.write("\t\tend\n")
    f.write("\tend\n\n")
        
        
    f.write("\t// Flop forwarding values for timing consistency with o_adder timing logic\n")
    f.write("\talways @ (*) begin\n")
    f.write("\t\tif (rst == 1'b1) begin\n")
    f.write("\t\t\to_adder <= 'd0;\n")
    f.write("\t\t\to_vn <= 'd0;\n")
    f.write("\t\t\to_vn_valid <= 'd0;\n")
    f.write("\t\tend else begin\n")
    f.write("\t\t\tif (r_add_en == 1'b0) begin\n")
    f.write("\t\t\t\to_adder <= r_adder;\n")
    f.write("\t\t\tend else begin\n")
    f.write("\t\t\t\to_adder <= {(NUM_OUT){w_O}};\n")
    f.write("\t\t\tend\n")
    f.write("\t\t\to_vn <= r_vn;\n")
    f.write("\t\t\to_vn_valid <= r_vn_valid;\n")
    f.write("\t\tend\n")
    f.write("\tend\n\n")
    

    str0 = ""
    if("reduct" in pf):
        f.write("\tgenvar i;\n")
        f.write("\tgenerate\n")
        f.write("\t\tfor(i = 0; i < NUM_PEGS; i = i + 1) begin\n\n")
        str0 += "\t\t"

    f.write(str0 + "\t// instantiate INTx adder\n")
    f.write(str0 + "\t// IP CORE\n")
    f.write(str0 + "\tAdder_" + str(OUT_DATA_TYPE) + " my_Adder_" + str(OUT_DATA_TYPE) + " (\n")
    if("reduct" in pf):
        f.write(str0 + "\t\t.A(w_sel_data[(NUM_PEGS*DATA_TYPE+i*DATA_TYPE) +: DATA_TYPE]),\n")
        f.write(str0 + "\t\t.B(w_sel_data[i*DATA_TYPE +: DATA_TYPE]),\n")
    else:
        f.write(str0 + "\t\t.A(w_sel_data[DATA_TYPE+:DATA_TYPE]),\n")
        f.write(str0 + "\t\t.B(w_sel_data[0+:DATA_TYPE]),\n")
    f.write(str0 + "\t\t.CLK(clk),\n")
    if("reduct" in pf):
        f.write(str0 + "\t\t.S(w_O[i*DATA_TYPE +: DATA_TYPE])\n")
    else:
        f.write(str0 + "\t\t.S(w_O)\n")
    f.write(str0 + "\t);\n\n")

    f.write(str0 + "\t// adder_n # (\n")
    f.write(str0 + "\t//     .IN_DATA_TYPE(DATA_TYPE),\n")
    f.write(str0 + "\t//     .OUT_DATA_TYPE(DATA_TYPE))\n")
    f.write(str0 + "\t//     my_adder_n (\n")
    f.write(str0 + "\t// 	.clk(clk),\n")
    f.write(str0 + "\t// 	.rst(rst),\n")
    if("reduct" in pf):
        f.write(str0 + "\t// 	.A(w_sel_data[(NUM_PEGS*DATA_TYPE+i*DATA_TYPE) +: DATA_TYPE]),\n")
        f.write(str0 + "\t// 	.B(w_sel_data[i*DATA_TYPE +: DATA_TYPE]),\n")
        f.write(str0 + "\t// 	.O(w_O[i*DATA_TYPE +: DATA_TYPE])\n")
    else:
        f.write(str0 + "\t// 	.A(w_sel_data[DATA_TYPE+:DATA_TYPE]),\n")
        f.write(str0 + "\t// 	.B(w_sel_data[0+:DATA_TYPE]),\n")
        f.write(str0 + "\t// 	.O(w_O)\n")
    f.write(str0 + "\t// );\n\n")

    if("reduct" in pf):
        f.write("\t\tend\n")
        f.write("\tendgenerate\n")

    f.write("endmodule\n\n")