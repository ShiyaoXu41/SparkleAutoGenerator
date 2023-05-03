# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
target_path = root_path + "\\vmod\\"


# ================== 3. generate vmod ==================
# ======================================================

f = open(target_path + "prefixsum.v", mode = 'w')

########################################################

NUM = NUM_PEGS
LOG2_NUM = LOG2_PEGS

# module presum
f.write("module presum_" + str(NUM) + " (\n")
f.write("\tinput       [%d-1:0]               din,\n" % NUM)
f.write("\toutput      [%d*(%d+1)-1:0]  dout\n" % (NUM, LOG2_NUM))
f.write(");\n\n")

# wire [x:x] lvlx
for i in range(LOG2_NUM):
    f.write("\twire\t[%d*(%d+1)-1:0]\tlvl%d;\n" % ((NUM/pow(2,i+1)), LOG2_NUM, i))


f.write("\n\tgenvar i;\n\n")

# assign lvlx
for i in range(LOG2_NUM):
    f.write("\t// lvl%d\n" % i)
    f.write("\tgenerate\n")
    f.write("\t\tfor(i = 0; i < %d; i = i + 1) begin: lvl%d_gen\n" % (NUM/pow(2,i+1), i))
    if(i == 0):
        f.write("\t\t\tassign lvl0[i*(%d+1) +: (%d+1)] = din[2*i] + din[2*i+1];\n" % (LOG2_NUM, LOG2_NUM))
    else:
        f.write("\t\t\tassign lvl%d[i*(%d+1) +: (%d+1)] = lvl%d[(2*i)*(%d+1) +: (%d+1)] + lvl%d[(2*i+1)*(%d+1) +: (%d+1)];\n" %(i, LOG2_NUM, LOG2_NUM, i-1, LOG2_NUM, LOG2_NUM, i-1, LOG2_NUM, LOG2_NUM))
    f.write("\t\tend\n")
    f.write("\tendgenerate\n\n")

# assign dout
f.write("\t// dout\n")
f.write("\t// from lvlx directly\n")
f.write("\tassign dout[0 +: (%d+1)] = din[0];\n" % (LOG2_NUM))
for i in range(LOG2_NUM):
    f.write("\tassign dout[%d*(%d+1) +: (%d+1)] = lvl%d[%d : 0];\n" % (pow(2,i+1)-1, LOG2_NUM, LOG2_NUM, i, LOG2_NUM))

f.write("\n\t// from lvlx and dout to add\n")
for i in range(LOG2_NUM-1):
    for j in range(pow(2,i+1)-1):
        if(i == LOG2_NUM-2):
            f.write("\tassign dout[%d*(%d+1) +: (%d+1)]\t=\tdout[%d*(%d+1) +: (%d+1)] + din[%d];\n" %( (2*(j+1)+1)*NUM/pow(2,i+2)-1, LOG2_NUM, LOG2_NUM, (j+1)*NUM/pow(2,i+1)-1, LOG2_NUM, LOG2_NUM, 2*(j+1)))
        else:
            f.write("\tassign dout[%d*(%d+1) +: (%d+1)]\t=\tdout[%d*(%d+1) +: (%d+1)] + lvl%d[%d*(%d+1) +: (%d+1)];\n" %( (2*(j+1)+1)*NUM/pow(2,i+2)-1, LOG2_NUM, LOG2_NUM, (j+1)*NUM/pow(2,i+1)-1, LOG2_NUM, LOG2_NUM, LOG2_NUM-3-i,  2*(j+1), LOG2_NUM, LOG2_NUM))
    f.write("\n")
    
f.write("endmodule\n\n\n\n\n")


########################################################

if(NUM_PES != NUM_PEGS):
    NUM = NUM_PES
    LOG2_NUM = LOG2_PES

    # module presum
    f.write("module presum_" + str(NUM) + " (\n")
    f.write("\tinput       [%d-1:0]               din,\n" % NUM)
    f.write("\toutput      [%d*(%d+1)-1:0]  dout\n" % (NUM, LOG2_NUM))
    f.write(");\n\n")

    # wire [x:x] lvlx
    for i in range(LOG2_NUM):
        f.write("\twire\t[%d*(%d+1)-1:0]\tlvl%d;\n" % ((NUM/pow(2,i+1)), LOG2_NUM, i))


    f.write("\n\tgenvar i;\n\n")

    # assign lvlx
    for i in range(LOG2_NUM):
        f.write("\t// lvl%d\n" % i)
        f.write("\tgenerate\n")
        f.write("\t\tfor(i = 0; i < %d; i = i + 1) begin: lvl%d_gen\n" % (NUM/pow(2,i+1), i))
        if(i == 0):
            f.write("\t\t\tassign lvl0[i*(%d+1) +: (%d+1)] = din[2*i] + din[2*i+1];\n" % (LOG2_NUM, LOG2_NUM))
        else:
            f.write("\t\t\tassign lvl%d[i*(%d+1) +: (%d+1)] = lvl%d[(2*i)*(%d+1) +: (%d+1)] + lvl%d[(2*i+1)*(%d+1) +: (%d+1)];\n" %(i, LOG2_NUM, LOG2_NUM, i-1, LOG2_NUM, LOG2_NUM, i-1, LOG2_NUM, LOG2_NUM))
        f.write("\t\tend\n")
        f.write("\tendgenerate\n\n")

    # assign dout
    f.write("\t// dout\n")
    f.write("\t// from lvlx directly\n")
    f.write("\tassign dout[0 +: (%d+1)] = din[0];\n" % (LOG2_NUM))
    for i in range(LOG2_NUM):
        f.write("\tassign dout[%d*(%d+1) +: (%d+1)] = lvl%d[%d : 0];\n" % (pow(2,i+1)-1, LOG2_NUM, LOG2_NUM, i, LOG2_NUM))

    f.write("\n\t// from lvlx and dout to add\n")
    for i in range(LOG2_NUM-1):
        for j in range(pow(2,i+1)-1):
            if(i == LOG2_NUM-2):
                f.write("\tassign dout[%d*(%d+1) +: (%d+1)]\t=\tdout[%d*(%d+1) +: (%d+1)] + din[%d];\n" %( (2*(j+1)+1)*NUM/pow(2,i+2)-1, LOG2_NUM, LOG2_NUM, (j+1)*NUM/pow(2,i+1)-1, LOG2_NUM, LOG2_NUM, 2*(j+1)))
            else:
                f.write("\tassign dout[%d*(%d+1) +: (%d+1)]\t=\tdout[%d*(%d+1) +: (%d+1)] + lvl%d[%d*(%d+1) +: (%d+1)];\n" %( (2*(j+1)+1)*NUM/pow(2,i+2)-1, LOG2_NUM, LOG2_NUM, (j+1)*NUM/pow(2,i+1)-1, LOG2_NUM, LOG2_NUM, LOG2_NUM-3-i,  2*(j+1), LOG2_NUM, LOG2_NUM))
        f.write("\n")
        
    f.write("endmodule\n\n\n\n\n")


########################################################


# module presum_dense
f.write("module pfxdense_" + str(NUM) + " (\n")
f.write("\tinput       [%d*(%d+1)-1:0]  pfx, \n" % (NUM, LOG2_NUM))
f.write("\toutput  reg [%d*%d-1:0]      pfx_dense\n" % (NUM, LOG2_NUM))
f.write(");\n\n")

f.write("\tgenvar i;\n")
f.write("\tgenerate\n")
f.write("\t\tfor(i = 0; i < %d; i = i + 1) begin: pfxdense_gen\n" % (NUM))
f.write("\t\t\talways @(*) begin\n")
f.write("\t\t\t\tif(i < pfx[%d*(%d+1)-1 -: (%d+1)]) begin\n" % (NUM, LOG2_NUM, LOG2_NUM))
f.write("\t\t\t\t\tcase(i+1)\n")
for i in range(NUM):
    f.write("\t\t\t\t\t\tpfx[%d*(%d+1) +: (%d+1)]:\tpfx_dense[i*%d +: %d] = 'd%d;\n" % (i, LOG2_NUM, LOG2_NUM, LOG2_NUM, LOG2_NUM, i))
f.write("\t\t\t\t\t\tdefault:\tpfx_dense[i*%d +: %d] = 'd0;\n" % (LOG2_NUM, LOG2_NUM))
f.write("\t\t\t\t\tendcase\n")
f.write("\t\t\t\tend else begin\n")
f.write("\t\t\t\t\tpfx_dense[i*%d +: %d] = 'd0;\n" % (LOG2_NUM, LOG2_NUM))
f.write("\t\t\t\tend\n")
f.write("\t\t\tend\n")
f.write("\t\tend\n")
f.write("\tendgenerate\n")
f.write("endmodule\n")

f.close()