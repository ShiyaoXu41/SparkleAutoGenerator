# ================== 2. generate vmod ==================
# ======================================================
from fan_ctrl_func import *

target_path = root_path + "\\vmod\\"

f = open(target_path + "fan_ctrl.v", mode = 'w')

##########################################################
f.write("//##########################################################\n")
f.write("// Generated Fowarding Adder Network Controller (FAN topology routing)\n")
f.write("//##########################################################\n\n\n")
##########################################################


##########################################################
# Generating module initization and input/output ports
##########################################################

f.write("module fan_ctrl # (\n")
f.write("\tparameter DATA_TYPE = " + str(OUT_DATA_TYPE) + ",\n")
f.write("\tparameter NUM_PES = " + str(NUM_PES) + ",\n")
f.write("\tparameter LOG2_PES = " + str(LOG2_PES) + ") (\n")
f.write("\tclk,\n")
f.write("\trst,\n")
f.write("\ti_vn,\n") # different partial sum bit seperator
f.write("\ti_stationary,\n") # determine if input is for stationary or streaming 
f.write("\ti_data_valid,\n") # if input data is valid or not
f.write("\to_reduction_add,\n") # if adder needs to add
f.write("\to_reduction_cmd,\n") # reduction command (VN outputs)
f.write("\to_reduction_sel,\n") # reduction select for the N-2 muxes
f.write("\to_reduction_valid\n") # if reduction output from FAN is valid or not
f.write(");\n") 

f.write("\tinput clk;\n")
f.write("\tinput rst;\n")
f.write("\tinput [NUM_PES*LOG2_PES-1: 0] i_vn; // different partial sum bit seperator\n")
f.write("\tinput i_stationary; // if input data is for stationary or streaming\n")
f.write("\tinput i_data_valid; // if input data is valid or not\n")
f.write("\toutput reg [(NUM_PES-1)-1:0] o_reduction_add; // determine to add or not\n")
f.write("\toutput reg [3*(NUM_PES-1)-1:0] o_reduction_cmd; // reduction command (for VN commands)\n")
NUM_SEL_BITS = get_sel_bits()
f.write("\toutput reg [" + str(int(NUM_SEL_BITS- 1)) + " : 0] o_reduction_sel; // select bits for FAN topology\n")
f.write("\toutput reg o_reduction_valid; // if reduction output from FAN is valid or not\n\n")


##########################################################
# Generate wire and reg declarations 
##########################################################

# not flopped cmd and sel signals
f.write("\t// reduction cmd and sel control bits (not flopped for timing yet)\n")
f.write("\treg [(NUM_PES-1)-1:0] r_reduction_add;\n")
f.write("\treg [3*(NUM_PES-1)-1:0] r_reduction_cmd;\n")
f.write("\treg [" + str(int(NUM_SEL_BITS - 1)) + " : 0] r_reduction_sel;\n")
f.write("\n\n")


# diagonal flops for timing leveling (adder en signal)
f.write("\t// diagonal flops for timing fix across different levels in tree (add_en signal)\n")
for i in range(LOG2_PES):
	add_max_range = get_adder_lvl(i)
	f.write("\treg [" + str(add_max_range) + " : 0] r_add_lvl_" +  str(i) + ";\n")
f.write("\n\n")


# diagonal flops for timing leveling (cmd signal)
f.write("\t// diagonal flops for timing fix across different levels in tree (cmd signal)\n")
for i in range(LOG2_PES):
	max_range = get_cmd_lvl(i)
	f.write("\treg [" + str(max_range) + " : 0] r_cmd_lvl_" +  str(i) + ";\n")
f.write("\n\n")

	
# diagonal flops for timing leveling (sel signal)
f.write("\t// diagonal flops for timing fix across different levels in tree (sel signal)\n")
for i in range(LOG2_PES-2):
	max_range = get_sel_lvl(i+2) # plus two as first two levels do not need sel
	f.write("\treg [" + str(max_range) + " : 0] r_sel_lvl_" +  str(i+2) + ";\n")
f.write("\n\n")


# timing alignment signals for i_vn delay and for output valid
VALID_DELAY = 4 # test which value works for timing alignment
CMD_SEL_DELAY = 2 # test which value works for timing alignment
f.write("\t// timing alignment for i_vn delay and for output valid\n")
f.write("\treg [" + str(CMD_SEL_DELAY) + "*NUM_PES*LOG2_PES-1:0] r_vn;\n")
f.write("\treg [NUM_PES*LOG2_PES-1:0] w_vn;\n")
f.write("\treg [" + str(int(VALID_DELAY-1)) + " : 0 ] r_valid;\n")
f.write("\n\n")


##########################################################
# Generate FF for i_vn cycle delays
##########################################################

f.write("\tgenvar i, x;\n")
# add flip flops to delay i_vn
f.write("\t// add flip flops to delay i_vn\n")
f.write("\tgenerate\n")
f.write("\t\tfor (i=0; i < " + str(CMD_SEL_DELAY) + "; i=i+1) begin : vn_ff\n")
f.write("\t\t\tif (i == 0) begin: pass\n")
f.write("\t\t\t\talways @ (posedge clk) begin\n")
f.write("\t\t\t\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\t\t\t\tr_vn[(i+1)*NUM_PES*LOG2_PES-1:i*NUM_PES*LOG2_PES] <= 'd0;\n")
f.write("\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\tr_vn[(i+1)*NUM_PES*LOG2_PES-1:i*NUM_PES*LOG2_PES] <= i_vn;\n")
f.write("\t\t\t\t\tend\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend else begin: flop\n")
f.write("\t\t\t\talways @ (posedge clk) begin\n")
f.write("\t\t\t\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\t\t\t\tr_vn[(i+1)*NUM_PES*LOG2_PES-1:i*NUM_PES*LOG2_PES] <= 'd0;\n")
f.write("\t\t\t\t\tend else begin\n")
f.write("\t\t\t\t\t\tr_vn[(i+1)*NUM_PES*LOG2_PES-1:i*NUM_PES*LOG2_PES] <= r_vn[i*NUM_PES*LOG2_PES-1:(i-1)*NUM_PES*LOG2_PES];\n")
f.write("\t\t\t\t\tend\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")

# assign last flop to w_vn
f.write("\t// assign last flop to w_vn\n")
f.write("\talways @(*) begin\n")
f.write("\t\tw_vn = r_vn[" + str(CMD_SEL_DELAY) + "*NUM_PES*LOG2_PES-1:" + str(CMD_SEL_DELAY-1) + "*NUM_PES*LOG2_PES];\n")
f.write("\tend\n")
f.write("\n\n")


##########################################################

##########################################################



##########################################################
# Controller Logic to Compute CMD and SEL bits for each adder
##########################################################

for i in range(LOG2_PES):
	f.write("\t// generating control bits for lvl: " + str(i) + "\n")
	if ( i < LOG2_PES -1): 
		f.write("\t// Note: lvl 0 and 1 do not require sel bits\n")
		f.write("\tgenerate\n")
		f.write("\t\tfor (x=0; x < " + str(NUM_PES >> (i+1)) + "; x=x+1) begin: adders_lvl_" + str(i) + "\n")
		############################################### LEFT CASE ###########################################
		f.write("\t\t\tif (x == 0) begin: l_edge_case\n")
		f.write("\t\t\t\talways @ (posedge clk) begin\n")
		f.write("\t\t\t\t\tif (rst == 1'b1) begin\n")
		f.write("\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 'd0;\n")
		f.write("\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 'd0;\n")
		if (i > 1): # need select logic for level 2 and over
			f.write("\t\t\t\t\t\t"  + generate_sel_range(i, "full") + " <= 'd0;\n")
		f.write("\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t// generate cmd logic\n")
		f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "add", "left") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b1; // add enable\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tend\n")
		f.write("\n\n")

		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "bothpass", "left") +  ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b101; // both vn done\n")
		if (i > 0):
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "rightpass", "middle") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b100; // right vn done\n")
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "leftpass", "left") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b011; // left vn done\n")				
		else:	
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "leftpass", "left") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b011; // left vn done\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\t\tend\n")
		f.write("\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\tend\n\n")

		if (i > 1): # need select logic
			f.write("\t\t\t\t\t\t// generate left select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "left", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "left", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

			f.write("\n\t\t\t\t\t\t// generate right select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "right", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "right", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\tend\n")
		f.write("\t\t\t\tend\n")
		############################################### RIGHT CASE ###########################################
		f.write("\t\t\tend else if (x == " + str((NUM_PES >> (i+1)) -1 )  + ") begin: r_edge_case\n")
		f.write("\t\t\t\talways @ (posedge clk) begin\n")
		f.write("\t\t\t\t\tif (rst == 1'b1) begin\n")
		f.write("\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) +  "+x] <= 'd0;\n")
		f.write("\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 'd0;\n")
		if (i > 1): # need select logic for level 2 and over
			f.write("\t\t\t\t\t\t" + generate_sel_range(i, "full") + " <= 'd0;\n")	
		f.write("\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t// generate cmd logic\n")
		f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "add", "right") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b1; // add enable\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tend\n")
		f.write("\n\n")

		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "bothpass", "right") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b101; // both vn done\n")
		if (i > 0):
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "leftpass", "middle") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b011; // left vn done\n")
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "rightpass", "right") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b100; // right vn done\n")				
		else:	
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "rightpass", "right") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b100; // right vn done\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\tend\n\n")

		if (i > 1): # need select logic
			f.write("\t\t\t\t\t\t// generate left select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "left", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "left", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

			f.write("\n\t\t\t\t\t\t// generate right select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "right", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "right", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\tend\n")
		f.write("\t\t\t\tend\n")
		############################################### NORMAL ###########################################
		f.write("\t\t\tend else begin: normal\n")
		f.write("\t\t\t\talways @ (posedge clk) begin\n")
		f.write("\t\t\t\t\tif (rst == 1'b1) begin\n")
		f.write("\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) +  "+x] <= 'd0;\n")
		f.write("\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 'd0;\n")
		if (i > 1): # need select logic for level 2 and over
			f.write("\t\t\t\t\t\t"  + generate_sel_range(i, "full") + " <= 'd0;\n")
		f.write("\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t// generate cmd logic\n")
		f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "add", "middle") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b1; // add enable\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tend\n")
		f.write("\n\n")

		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "bothpass", "middle") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b101; // both vn done\n")
		if (i > 0):
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "rightpass", "middle") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b100; // right vn done\n")
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "leftpass", "middle") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b011; // left vn done\n")				
		else:
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "rightpass", "middle") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b100; // right vn done\n")
			f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "leftpass", "middle") + ") begin\n")
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b011; // left vn done\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		if (i == 0): # bypass
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b001; // bypass\n")
		else: # no bypass needed
			f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\tend\n\n")

		if (i > 1): # need select logic
			f.write("\t\t\t\t\t\t// generate left select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "left", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "left", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

			f.write("\n\t\t\t\t\t\t// generate right select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "right", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "right", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\tend\n")
		f.write("\t\t\t\tend\n")	
		f.write("\t\t\tend\n")
		f.write("\t\tend\n")
		f.write("\tendgenerate\n\n")

	############################################### LAST LEVEL ###########################################
	else: # last level
		f.write("\tgenerate\n")
		f.write("\t\tfor (x=0; x < " + str(NUM_PES >> (i+1)) + "; x=x+1) begin: adders_lvl_" + str(i) + "\n")
		f.write("\t\t\tif (x == 0) begin: middle_case\n")
		f.write("\t\t\t\talways @ (posedge clk) begin\n")
		f.write("\t\t\t\t\tif (rst == 1'b1) begin\n")
		f.write("\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) +  "+x] <= 'd0;\n")
		f.write("\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 'd0;\n")
		if (i > 1): # need select logic for level 2 and over
			f.write("\t\t\t\t\t\t"  + generate_sel_range(i, "full") + " <= 'd0;\n")
		f.write("\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t// generate cmd logic\n")
		f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "add", "last") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b1; // add enable\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tend\n")
		f.write("\n\n")

		f.write("\t\t\t\t\t\t\tif (" + generate_lvl_wn_range(i, "bothpass", "last") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b101; // both vn done\n")
		f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "rightpass", "last") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b100; // right vn done\n")
		f.write("\t\t\t\t\t\t\tend else if (" + generate_lvl_wn_range(i, "leftpass", "last") + ") begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b011; // left vn done\n")
		f.write("\t\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\t\tend else begin\n")
		f.write("\t\t\t\t\t\t\tr_reduction_add[" + get_cmd_shift_accum(i) + "+x] <= 1'b0;\n")
		f.write("\t\t\t\t\t\t\tr_reduction_cmd[3*" + get_cmd_shift_accum(i) +  "+3*x+:3] <= 3'b000; // nothing\n")
		f.write("\t\t\t\t\t\tend\n\n")

		if (i > 1): # need select logic
			f.write("\t\t\t\t\t\t// generate left select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "left", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "left", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

			f.write("\n\t\t\t\t\t\t// generate right select logic\n")
			f.write("\t\t\t\t\t\tif (r_valid[" + str(CMD_SEL_DELAY-1) + "] == 1'b1) begin\n")
			f.write(generate_sel_statement(i, "right", "no") + "\n")
			f.write("\t\t\t\t\t\tend else begin\n")
			f.write(generate_sel_statement(i, "right", "yes") + "\n")
			f.write("\t\t\t\t\t\tend\n\n")

		f.write("\t\t\t\t\tend\n")
		f.write("\t\t\t\tend\n")
		f.write("\t\t\tend\n")
		f.write("\t\tend\n")
		f.write("\tendgenerate\n\n")


f.write("\n\n")


##########################################################
# Generate diagonal flops cmd/sel timing alignment
##########################################################

# flops to adjust for timing
f.write("\t// generate diagonal flops for cmd and sel timing alignment\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b1) begin\n")
for i in range(LOG2_PES):
	f.write("\t\t\tr_add_lvl_" +  str(i) + " <= 'd0;\n")
f.write("\n\n")

for i in range(LOG2_PES):
	f.write("\t\t\tr_cmd_lvl_" +  str(i) + " <= 'd0;\n")
f.write("\n\n")

for i in range(LOG2_PES-2):
	f.write("\t\t\tr_sel_lvl_" + str(i+2) + " <= 'd0;\n")
f.write("\t\tend else begin\n")
for i in range(LOG2_PES):
	num_adder = num_adders_in_lvl(i)
	for j in range(i+1):
		if (j == 0):
			f.write("\t\t\tr_add_lvl_" + str(i) + "[" + str(num_adder-1) + ":0] <= r_reduction_add" + get_lvl_add_range(i) + ";\n")
		else:
			f.write("\t\t\tr_add_lvl_" + str(i) + "[" + str((j+1)*num_adder-1) + ":" + str(j*num_adder) + "] <= r_add_lvl_" + str(i) + "[" + str(j*num_adder-1) + ":" + str((j-1)*num_adder) + "];\n")
f.write("\n\n")

for i in range(LOG2_PES):
	num_adder = num_adders_in_lvl(i)
	for j in range(i+1):
		if (j == 0):
			f.write("\t\t\tr_cmd_lvl_" + str(i) + "[" + str(3*num_adder-1) + ":0] <= r_reduction_cmd" + get_lvl_cmd_range(i) + ";\n")
		else:
			f.write("\t\t\tr_cmd_lvl_" + str(i) + "[" + str((j+1)*3*num_adder-1) + ":" + str(j*3*num_adder) + "] <= r_cmd_lvl_" + str(i) + "[" + str(j*3*num_adder-1) + ":" + str((j-1)*3*num_adder) + "];\n")
f.write("\n\n")

for i in range(LOG2_PES-2):
	num_sel = num_sel_bits_in_lvl(i+2)
	for j in range(i+3):
		if (j == 0):
			f.write("\t\t\tr_sel_lvl_" + str(i+2) + "[" + str(num_sel-1) + ":0] <= r_reduction_sel" + get_lvl_sel_range(i+2) + ";\n")
		else:
			f.write("\t\t\tr_sel_lvl_" + str(i+2) + "[" + str((j+1)*num_sel-1) + ":" + str(j*num_sel) + "] <= r_sel_lvl_" + str(i+2) + "[" + str(j*num_sel-1) + ":" + str((j-1)*num_sel) + "];\n")

f.write("\t\tend\n")
f.write("\tend\n")

f.write("\n\n")


##########################################################
# Assigning final outputs
##########################################################

# Adjust output valid timing and logic..
f.write("\t// Adjust output valid timing and logic\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (i_stationary == 1'b0 && i_data_valid == 1'b1) begin\n")
f.write("\t\t\tr_valid[0] <= 1'b1;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_valid[0] <= 1'b0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")


f.write("\tgenerate\n")
f.write("\t\tfor (i=0; i < " + str(int(VALID_DELAY-1)) + "; i=i+1) begin\n")
f.write("\t\t\talways @ (posedge clk) begin\n")
f.write("\t\t\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\t\t\tr_valid[i+1] <= 1'b0;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_valid[i+1] <= r_valid[i];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")


f.write("\talways @ (*) begin\n")
f.write("\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\to_reduction_valid <= 1'b0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_reduction_valid <= r_valid[" + str(int(VALID_DELAY-1)) + "];\n")
f.write("\t\tend\n")
f.write("\tend\n\n")


# Assigning final outputs for both diagonal flopped cmd and sel
f.write("\t// assigning diagonally flopped cmd and sel\n")
f.write("\talways @ (*) begin\n")
f.write("\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\to_reduction_add <= 'd0;\n")
f.write("\t\t\to_reduction_cmd <= 'd0;\n")
f.write("\t\t\to_reduction_sel <= 'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_reduction_add <= " + gen_o_reduction_add(LOG2_PES, NUM_PES) + "\n")
f.write("\t\t\to_reduction_cmd <= " + gen_o_reduction_cmd(LOG2_PES, NUM_PES) + "\n")
f.write("\t\t\to_reduction_sel <= " + gen_o_reduction_sel(LOG2_PES, NUM_PES) + "\n")
f.write("\t\tend\n")
f.write("\tend\n\n")


f.write("endmodule\n")






