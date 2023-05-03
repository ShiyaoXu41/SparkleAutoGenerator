# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
source_path = os.getcwd() + "\\vmod\\"
target_path = root_path + "\\vmod\\"


# ================ 2. list replaced str ================
# ======================================================
import math

file_name = "load_KN.v"

old_str = [
            # IP Core
            "bram_KN_data ",
            "fifo_KN_data ",
            # parameter
            "parameter   DATA_TYPE       ,",
	        "parameter   NUM_PES         ,",
	        "parameter   LOG2_PES        ,",
	        "parameter   PARA_BLOCKS     ,",
	        "parameter   LOG2_PARA_BLOCKS"
           ]

new_str = [
            # IP Core
            "bram_KN_data_%dx%d " % (IN_DATA_TYPE*NUM_PES*PARA_BLOCKS, 2**(POINTER_WIDTH-math.floor(math.log(NUM_PES, 2))-math.floor(math.log(PARA_BLOCKS, 2)))),
            "fifo_KN_data_%dx%d " % (NUM_PES*IN_DATA_TYPE, MAX_N_DIM),
            # parameter
            "parameter   DATA_TYPE       = %d," % (IN_DATA_TYPE),
	        "parameter   NUM_PES         = %d," % (NUM_PES),
	        "parameter   LOG2_PES        = %d," % (LOG2_PEGS),
	        "parameter   PARA_BLOCKS     = %d," % (PARA_BLOCKS),
	        "parameter   LOG2_PARA_BLOCKS= %d"  % (LOG2_PARA_BLOCKS)
           ]
# ======================================================

# ================ 3. rewrite vmod file ================
# replace old_str
file_data = ""
with open(source_path + file_name, "r", encoding="utf-8") as f1:
    for line in f1:
        for i in range(len(old_str)):
            if(old_str[i] in line):
                line = line.replace(old_str[i], new_str[i])
        file_data += line
# overwrite new_str
with open(target_path + file_name, "w", encoding="utf-8") as f2:
    f2.write(file_data)