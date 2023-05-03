# ================== 2. generate vmod ==================
# ======================================================
from fan_network_func import *

target_path = root_path + "\\vmod\\"

f = open(target_path + "fan_network.v", mode = 'w')


##########################################################
f.write("//##########################################################\n")
f.write("// Generated Fowarding Adder Network (FAN topology)\n")
f.write("//##########################################################\n\n\n")
##########################################################


##########################################################
# Generating module initization and input/output ports
##########################################################

DATA_TYPE = OUT_DATA_TYPE # true for reduction network (reduce with FP32)

f.write("module fan_network # (\n")
f.write("\tparameter DATA_TYPE =  " + str(OUT_DATA_TYPE) + " ,\n")
f.write("\tparameter NUM_PES =  " + str(NUM_PES) + " ,\n")
f.write("\tparameter LOG2_PES =  " + str(LOG2_PES) + " ) (\n")
f.write("\tclk,\n")
f.write("\trst,\n")
f.write("\ti_valid,\n") # valid input data bus signal
f.write("\ti_data_bus,\n") # input data bus from multipliers
f.write("\ti_add_en_bus,\n") # adder enable bus
f.write("\ti_cmd_bus,\n") # cmd for all of the adders
f.write("\ti_sel_bus,\n") # mux select to the inputs of the adders
f.write("\to_valid,\n") # output valid signal bus
f.write("\to_data_bus\n") # output data bus
f.write(");\n") 

f.write("\tinput clk;\n")
f.write("\tinput rst;\n")
f.write("\tinput i_valid; // valid input data bus\n")
f.write("\tinput [NUM_PES*DATA_TYPE-1 : 0] i_data_bus; // input data bus\n")
f.write("\tinput [(NUM_PES-1)-1 : 0] i_add_en_bus; // adder enable bus\n")
f.write("\tinput [3*(NUM_PES-1)-1 : 0] i_cmd_bus; // command bits for each adder\n")
NUM_SEL_BITS = get_sel_bits()
f.write("\tinput [" +  str(int(NUM_SEL_BITS- 1)) + " : 0] i_sel_bus; // select bits for FAN topolgy\n")
f.write("\toutput reg [NUM_PES-1 : 0] o_valid; // output valid signal\n")
f.write("\toutput reg [NUM_PES*DATA_TYPE-1 : 0] o_data_bus; // output data bus\n\n")

##########################################################
# Generate wire and reg declarations 
##########################################################

# tree wires (includes binary and forwarding wires)
f.write("\t// tree wires (includes binary and forwarding wires)\n")
for i in range(LOG2_PES):
	TREE_WIRE = get_binary_fwd_wires(i)
	f.write("\twire [" + str(int(TREE_WIRE * DATA_TYPE - 1)) + " : 0] w_fan_lvl_" + str(i) + ";\n")
f.write("\n\n")


# flop fowarding levels across levels to maintain timing
f.write("\t// flop forwarding levels across levels to maintain pipeline timing\n")
for i in range(LOG2_PES - 2): # reg data type for FF
	for j in range(LOG2_PES - 2 - i):
		lvl_src = i
		lvl_dest = LOG2_PES-1-j
		fwd_width = get_fwd_links_width(lvl_src, lvl_dest)
		f.write("\treg [" + str(fwd_width -1 ) + " : 0] r_fan_ff_lvl_" + str(lvl_src) + "_to_" + str(lvl_dest) +  ";\n") 
f.write("\n\n")


# output virtual neuron (completed partial sums) wires for each level and valid bits
f.write("\t// output virtual neuron (completed partial sums) wires for each level and valid bits\n")
for i in range(LOG2_PES):
	upper_bound = (NUM_PES >> i )
	f.write("\twire [" + str(upper_bound*DATA_TYPE -1) + " : 0] w_vn_lvl_" + str(i) + ";\n")
	f.write("\twire [" + str(upper_bound -1) + " : 0] w_vn_lvl_" + str(i) + "_valid;\n")
f.write("\n\n")


# output ff within each level of adder tree to maintain pipeline behavior
f.write("\t// output ff within each level of adder tree to maintain pipeline behavior\n")
f.write("\treg [" + str(NUM_PES * LOG2_PES * DATA_TYPE - 1) + " : 0] r_lvl_output_ff;\n")
f.write("\treg [" + str(NUM_PES * LOG2_PES -1) + " : 0] r_lvl_output_ff_valid;\n") 
f.write("\n\n")


# valid FFs for each level of the adder tree
f.write("\t// valid FFs for each level of the adder tree\n")
f.write("\treg [" + str(LOG2_PES + 1) + " : 0] r_valid;\n") # system delay

# flop final adder output cmd and values for timing alignment
f.write("\t// flop final adder output cmd and values\n")
f.write("\treg [DATA_TYPE-1:0] r_final_sum;\n")
f.write("\treg r_final_add;\n")
f.write("\treg r_final_add2;\n")

##########################################################
# Generate Flip Flops for fowarding levels to maintain timing (FAN Toplogy fwd link timing)
##########################################################

# Flip flops for forwarding levels to maintain pipeline timing
f.write("\t// FAN topology flip flops between forwarding levels to maintain pipeline timing\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b1) begin\n") # set FFs to zero when reset is 1'b1
for i in range(LOG2_PES - 2):
	for j in range(LOG2_PES - 2 - i):
		lvl_src = i
		lvl_dest = LOG2_PES-1-j
		f.write("\t\t\tr_fan_ff_lvl_" + str(lvl_src) + "_to_" + str(lvl_dest) +  " = 'd0;\n") 
f.write("\t\tend else begin\n") # set FFs to corresponding inputs
for i in range(LOG2_PES - 2):
	new_i = 0
	for j in range(LOG2_PES - 2 - i):
		lvl_src = i
		lvl_dest = LOG2_PES-1-j
		num_links = get_num_fwd_links(lvl_src, lvl_dest)
	
		if (new_i == LOG2_PES - 2 - i - 1): # Input of fowarding link FF comes directly from adder
			for n in range(num_links):
				f.write("\t\t\tr_fan_ff_lvl_" + str(lvl_src) + "_to_" + str(lvl_dest) + "[" + str(int((n+1)*DATA_TYPE-1)) + ":" + str(n*int(DATA_TYPE)) + "] = w_fan_lvl_" + str(lvl_src) + get_ff_adder_index(lvl_src, lvl_dest, n) + "\n")
				
		else: # Input of forwarding link FF comes from a previous FF
			for n in range(num_links):
				f.write("\t\t\tr_fan_ff_lvl_" + str(lvl_src) + "_to_" + str(lvl_dest) + "[" + str(int((n+1)*DATA_TYPE-1)) + ":" + str(n*int(DATA_TYPE)) + "] = r_fan_ff_lvl_" + str(lvl_src) + "_to_" + str(lvl_dest-1) + get_ff_fwd_index(lvl_src, lvl_dest, n) + "\n")
			new_i = new_i + 1
			
f.write("\t\tend\n")
f.write("\tend\n")
f.write("\n\n")

##########################################################
# Generate Output Buffers and Muxes across all levels to pipeline finished VNs (complete Psums)
##########################################################

f.write("\t// Output Buffers and Muxes across all levels to pipeline finished VNs (complete Psums)\n")
for i in range(LOG2_PES):
	max_range = (i+1)*NUM_PES*DATA_TYPE-1 
	min_range = i*NUM_PES*DATA_TYPE 
	max_range_v = (i+1)*NUM_PES-1
	min_range_v = i*NUM_PES
	adder_vn = []
	f.write("\talways @ (posedge clk) begin\n")
	f.write("\t\tif (rst == 1'b1) begin\n") # set output VN FFs to zero when reset is 1'b1
	f.write("\t\t\tr_lvl_output_ff[" + str(max_range) + ":" + str(min_range) + "] <= 'd0;\n")
	f.write("\t\t\tr_lvl_output_ff_valid[" + str(max_range_v) + ":" + str(min_range_v) + "] <= 'd0;\n")
	f.write("\t\tend else begin\n") # set output VN FFs to previous level
	if (i == 0): # level 0
		for s in range(NUM_PES >> (i+1)):
			f.write("\t\t\tif (w_vn_lvl_" + str(i) + "_valid[" + str(s*2+1) + ":" + str(s*2) + "] == 2'b11) begin // both VN complete\n") 
			f.write("\t\t\t\tr_lvl_output_ff[" + str(2*(s+1)*DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "] <= w_vn_lvl_0[" + str(2*(s+1)*DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "];\n")
			f.write("\t\t\t\tr_lvl_output_ff_valid[" + str(2*(s+1)-1) + ":" + str(2*s) + "] <= 2'b11;\n")
			f.write("\t\t\tend else if (w_vn_lvl_" + str(i) + "_valid[" + str(s*2+1) + ":" + str(s*2) + "] == 2'b10) begin // right VN complete\n")
			f.write("\t\t\t\tr_lvl_output_ff[" + str(2*(s+1)*DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE+DATA_TYPE) + "] <= w_vn_lvl_0[" + str(2*(s+1)*DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE+DATA_TYPE) + "];\n")
			f.write("\t\t\t\tr_lvl_output_ff[" + str(2*s*DATA_TYPE+DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "] <= 'd0;\n")
			f.write("\t\t\t\tr_lvl_output_ff_valid[" + str(2*(s+1)-1) + ":" + str(2*s) + "] <= 2'b10;\n")
			f.write("\t\t\tend else if (w_vn_lvl_" + str(i) + "_valid[" + str(s*2+1) + ":" + str(s*2) + "] == 2'b01) begin // left VN complete\n")
			f.write("\t\t\t\tr_lvl_output_ff[" + str(2*(s+1)*DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "] <= 'd0;\n")
			f.write("\t\t\t\tr_lvl_output_ff[" + str(2*s*DATA_TYPE+DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "] <= w_vn_lvl_0[" +  str(2*s*DATA_TYPE+DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "];\n")
			f.write("\t\t\t\tr_lvl_output_ff_valid[" + str(2*(s+1)-1) + ":" + str(2*s) + "] <= 2'b01;\n")
			f.write("\t\t\tend else begin // no VN complete\n")
			f.write("\t\t\t\tr_lvl_output_ff[" + str(2*(s+1)*DATA_TYPE-1) + ":" + str(2*s*DATA_TYPE) + "] <= 'd0; \n")
			f.write("\t\t\t\tr_lvl_output_ff_valid[" + str(2*(s+1)-1) + ":" + str(2*s) + "] <= 2'b00;\n")
			f.write("\t\t\tend\n")
			f.write("\n\n")
	else:
		# for n in range(NUM_PES >> (i+1)): # find adder_ids in the lvl that can output to vn
		# 	adder_vn.append(int(2**(i+1)*n+ 2**(i-1)))
		# 	adder_vn.append(int(2**(i+1)*n+ 2**(i-1)*3-1))
		for n in range(NUM_PES >> (i)):
			adder_vn.append(int(2**(i)*n + 2**(i-1) - 1))
		count = 0
		for s in range(NUM_PES):
			if (s not in adder_vn):
				f.write("\t\t\tr_lvl_output_ff[" + str((i*DATA_TYPE*NUM_PES)+(s+1)*DATA_TYPE-1) + ":" + str((i*DATA_TYPE*NUM_PES)+s*DATA_TYPE) + "] <= r_lvl_output_ff[" + str(((i-1)*DATA_TYPE*NUM_PES)+(s+1)*DATA_TYPE-1) + ":" + str(((i-1)*DATA_TYPE*NUM_PES)+s*DATA_TYPE) + "];\n")
				f.write("\t\t\tr_lvl_output_ff_valid[" + str((i*NUM_PES)+s) + "] <= r_lvl_output_ff_valid[" + str((i-1)*NUM_PES+s) + "];\n")
			else:
				f.write("\t\t\tif (w_vn_lvl_" + str(i) + "_valid[" + str(count) + "] == 1'b1) begin\n")
				f.write("\t\t\t\tr_lvl_output_ff[" + str((i*DATA_TYPE*NUM_PES)+(s+1)*DATA_TYPE-1) + ":" + str((i*DATA_TYPE*NUM_PES)+s*DATA_TYPE) + "] <= w_vn_lvl_" + str(i) + "[" + str(DATA_TYPE * (count+1) -1) + ":" + str(DATA_TYPE * count) + "];\n")
				f.write("\t\t\t\tr_lvl_output_ff_valid[" + str((i*NUM_PES)+s) + "] <= 1'b1;\n")
				f.write("\t\t\tend else begin\n")
				f.write("\t\t\t\tr_lvl_output_ff[" + str((i*DATA_TYPE*NUM_PES)+(s+1)*DATA_TYPE-1) + ":" + str((i*DATA_TYPE*NUM_PES)+s*DATA_TYPE) + "] <= r_lvl_output_ff[" + str(((i-1)*DATA_TYPE*NUM_PES)+(s+1)*DATA_TYPE-1) + ":" + str(((i-1)*DATA_TYPE*NUM_PES)+s*DATA_TYPE) + "];\n")
				f.write("\t\t\t\tr_lvl_output_ff_valid[" + str((i*NUM_PES)+s) + "] <= r_lvl_output_ff_valid[" + str((i-1)*NUM_PES+s) + "];\n")
				f.write("\t\t\tend\n")
				count = count + 1
			f.write("\n\n")

	f.write("\t\tend\n")
	f.write("\tend\n")
	f.write("\n\n")

	
##########################################################
# Flop input valid for different level of the adder tree
##########################################################
f.write("\t// Flop input valid for different level of the adder tree\n")
f.write("\talways @ (*) begin\n")
f.write("\t\tif (i_valid == 1'b1) begin\n")
f.write("\t\t\tr_valid[0] <= 1'b1;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_valid[0] <= 1'b0;\n")
f.write("\t\tend\n")
f.write("\tend\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor (i=0; i < " + str(LOG2_PES + 1) + "; i=i+1) begin\n")
f.write("\t\t\talways @ (posedge clk) begin\n")
f.write("\t\t\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\t\t\tr_valid[i+1] <= 1'b0;\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tr_valid[i+1] <= r_valid[i];\n")
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n\n")


##########################################################
# Instantiate Adder Switches 
##########################################################

f.write("\t// Instantiating Adder Switches\n")
for adderID in range(NUM_PES - 1):
	lvl = get_lvl(adderID)
	WIRE_IN = get_wire_in(adderID)
	SEL_IN = get_sel_in(adderID)
	
	if (is_edge(adderID) == "true"): # edge adder (1 output)
		f.write("\n\tedge_adder_switch #(\n")
	else : # regular adder (2 outputs)
		f.write("\n\tadder_switch #(\n")
		
	f.write("\t\t.DATA_TYPE( " + str(DATA_TYPE) + " ),\n")
	f.write("\t\t.NUM_IN( " + str(WIRE_IN) + " ),\n")
	
	if (SEL_IN == 0) : # Switch needs to be hardcoded
		f.write("\t\t.SEL_IN( 2 )) my_adder_" + str(adderID) + " (\n")
	else:
		f.write("\t\t.SEL_IN( " + str(SEL_IN) + " )) my_adder_" + str(adderID) + " (\n")	
		
	f.write("\t\t.clk(clk),\n")
	f.write("\t\t.rst(rst),\n")
	f.write("\t\t.i_valid(r_valid[" + str(lvl) +"]),\n")

	if (lvl == 0): # first level adders, get inputs from multipliers (i_data_bus)
		f.write("\t\t.i_data_bus(i_data_bus[" + str((adderID + 2)*DATA_TYPE -1) + " : " + str((adderID)*DATA_TYPE) + "]),\n")
	else: # following level adders, get inputs from previous adder outputs
		FAN_WIRE_IN = get_fan_wire_in(adderID)
		f.write("\t\t.i_data_bus(" + str(FAN_WIRE_IN)  + "),\n")

	f.write("\t\t.i_add_en(i_add_en_bus" + get_adder_en_id(adderID) + "),\n")
	f.write("\t\t.i_cmd(i_cmd_bus" + get_cmd_range(adderID) + "),\n")

	if (lvl <= 1):
		f.write("\t\t.i_sel(2'b00),\n")
	else:
		f.write("\t\t.i_sel(i_sel_bus" + get_sel_region(adderID) + "),\n")

	f.write("\t\t.o_vn(" +  get_vn_out(adderID) + "),\n")
	f.write("\t\t.o_vn_valid(" + get_vn_out_valid(adderID) + "),\n")
	f.write("\t\t.o_adder(" + get_fan_out(adderID) + ")\n")
	f.write("\t);\n")	

f.write("\n\n")
	
##########################################################
# Assigning output bus (with correct timing and final adder mux)
##########################################################
# Flop last level adder cmd for timing matching
f.write("\t// Flop last level adder cmd for timing matching\n")
f.write("\talways @ (posedge clk) begin\n")
f.write("\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\tr_final_add <= 'd0;\n")
f.write("\t\t\tr_final_add2 <= 'd0;\n")
f.write("\t\t\tr_final_sum <= 'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\tr_final_add <= i_add_en_bus[" + str((NUM_PES-1)-1) + "];\n")
f.write("\t\t\tr_final_add2 <= r_final_add;\n")
f.write("\t\t\tr_final_sum <= w_fan_lvl_" + str(LOG2_PES-1) + ";\n")
f.write("\t\t\tend\n")
f.write("\tend\n")
f.write("\n\n")



f.write("\t// Assigning output bus (with correct timing and final adder mux)\n")
f.write("\talways @ (*) begin\n")
f.write("\t\tif (rst == 1'b1) begin\n")
f.write("\t\t\to_data_bus <= 'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_data_bus[" + str(int(NUM_PES/2*DATA_TYPE-DATA_TYPE-1)) + ":0] <= r_lvl_output_ff[" + str(int(NUM_PES*DATA_TYPE*(LOG2_PES-1)+NUM_PES/2*DATA_TYPE-DATA_TYPE-1)) + ":" + str(int(NUM_PES*DATA_TYPE*(LOG2_PES-1))) + "];\n")
f.write("\t\t\tif (r_final_add2 == 1'b1) begin\n") # adding
f.write("\t\t\t\to_data_bus[" + str(int(NUM_PES/2*DATA_TYPE-1)) + ":" + str(int(NUM_PES/2*DATA_TYPE-DATA_TYPE)) + "] <= r_final_sum;\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\to_data_bus[" + str(int(NUM_PES/2*DATA_TYPE-1)) + ":" + str(int(NUM_PES/2*DATA_TYPE-DATA_TYPE)) + "] <= r_lvl_output_ff[" + str(int(NUM_PES*DATA_TYPE*(LOG2_PES-1)+NUM_PES/2*DATA_TYPE-1)) + ":" + str(int(NUM_PES*DATA_TYPE*(LOG2_PES-1)+NUM_PES/2*DATA_TYPE-DATA_TYPE)) + "];\n")
f.write("\t\t\tend\n")
f.write("\t\t\to_data_bus[" + str(int(NUM_PES*DATA_TYPE-1)) + ":" + str(int(NUM_PES/2*DATA_TYPE)) + "] <= r_lvl_output_ff[" + str(int(NUM_PES*DATA_TYPE*LOG2_PES-1)) + ":" + str(int(NUM_PES*DATA_TYPE*(LOG2_PES-1)+NUM_PES/2*DATA_TYPE)) + "];\n") 
f.write("\t\tend\n")
f.write("\tend\n")
f.write("\n\n")

##########################################################
# Assigning output valid (with correct timing and final adder mux)
##########################################################

# Assignment
f.write("\t// Assigning output valid (with correct timing and final adder mux)\n")
f.write("\talways @ (*) begin\n")
f.write("\t\tif (rst == 1'b1 || r_valid[" + str(LOG2_PES + 1) + "] == 1'b0) begin\n")
f.write("\t\t\to_valid <= 'd0;\n")
f.write("\t\tend else begin\n")
f.write("\t\t\to_valid[" + str(int(NUM_PES/2-2)) + ":0] <= r_lvl_output_ff_valid[" + str(int(NUM_PES*(LOG2_PES-1)+NUM_PES/2-1)) + ":" + str(int(NUM_PES*(LOG2_PES-1))) + "];\n")
f.write("\t\t\tif (r_final_add2 == 1'b1) begin\n") # adding
f.write("\t\t\t\to_valid[" + str(int(NUM_PES/2-1)) + "] <= 1'b1 ;\n")
f.write("\t\t\tend else begin\n")
f.write("\t\t\t\to_valid[" + str(int(NUM_PES/2-1)) + "] <= r_lvl_output_ff_valid[" + str(int(NUM_PES*(LOG2_PES-1)+NUM_PES/2-1)) + "];\n")
f.write("\t\t\tend\n")
f.write("\t\t\to_valid[" + str(int(NUM_PES-1)) + ":" + str(int(NUM_PES/2)) + "] <= r_lvl_output_ff_valid[" + str(int(NUM_PES*LOG2_PES-1)) + ":" + str(int(NUM_PES*(LOG2_PES-1)+NUM_PES/2)) + "];\n") 
f.write("\t\tend\n")
f.write("\tend\n")
f.write("\n\n")

	
f.write("endmodule\n")



