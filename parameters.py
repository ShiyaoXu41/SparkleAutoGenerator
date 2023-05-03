import math

# =============== Main Parameters ===============
NUM_PEGS = 8
LOG2_PEGS = math.ceil(math.log(NUM_PEGS, 2)) if math.ceil(math.log(NUM_PEGS, 2)) > 0 else 1

NUM_PES = 8
LOG2_PES = math.ceil(math.log(NUM_PES, 2)) if math.ceil(math.log(NUM_PES, 2)) > 0 else 1

# =============== Minor Parameters ===============
IN_DATA_TYPE = 8
OUT_DATA_TYPE = 16

PARA_BLOCKS = 5
LOG2_PARA_BLOCKS = math.ceil(math.log(PARA_BLOCKS, 2)) if math.ceil(math.log(PARA_BLOCKS, 2)) > 0 else 1

POINTER_WIDTH = 20
# the MEM SIZE is 2^20(POINTER_WIDTH)
LOG2_MEMD = POINTER_WIDTH - LOG2_PES

MAX_N_DIM = 256

# =============== Inputs Parameters (in tb & sim) ===============
M_DIM = 768
K_DIM = 768
K_PAD = PARA_BLOCKS * NUM_PES * math.ceil(K_DIM/(PARA_BLOCKS*NUM_PES))
N_DIM = 128

SPARSITY = 0

# =============== Path & Folder Name ===============
import os
name = "Sparkle_%dx%d_p%dd%dw%dn%d" % (NUM_PEGS, NUM_PES, PARA_BLOCKS, IN_DATA_TYPE, POINTER_WIDTH, MAX_N_DIM)
# in vmod & tb
root_path = os.path.dirname(os.getcwd()) + "\\" + name
# in sim
data_path = os.getcwd() + "\sim\data\\"
# print(data_path)
f_path = os.getcwd()  + "_project\\" + name + "_project.sim\sim_1\\behav\\xsim\\"
# print(f_path)