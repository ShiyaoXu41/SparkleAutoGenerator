# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
source_path = os.getcwd() + "\\vmod\\"
target_path = root_path + "\\vmod\\"


# ================ 2. list replaced str ================
# ======================================================
file_name = "load_MK.v"

old_str = [
            # IP Core
            "bram_MK_bitmap ",
            "bram_MK_pointer ",
            "bram_MK_data ",
            "fifo_MK_data ",
            "fifo_dest ",
            "fifo_vn ",
            "fifo_flag ",
            # vmod gen
            "presum ",
            "pfxdense ",
            # parameter
            "parameter   DATA_TYPE   ,",
            "parameter   NUM_PEGS    ,",
            "parameter   LOG2_PEGS   ,",
            "parameter   NUM_PES     ,",
            "parameter   LOG2_PES    ,",
            "parameter   LOG2_MEMD   ,",
            "parameter   POINTER_WIDTH)"
           ]

new_str = [
            # IP Core
            "bram_MK_bitmap_%dx%d " % (NUM_PES, 2**LOG2_MEMD),
            "bram_MK_pointer_%dx%d " % (POINTER_WIDTH, 2**LOG2_MEMD),
            "bram_MK_data_%dx%d " % (2*NUM_PES*IN_DATA_TYPE, 2**(LOG2_MEMD-1)),
            "fifo_MK_data_%dx%d " % (IN_DATA_TYPE*NUM_PES, 2*NUM_PEGS),
            "fifo_dest_%dx%d " % (LOG2_PES*NUM_PES, 2*NUM_PEGS),
            "fifo_vn_%dx%d " % (LOG2_PEGS*NUM_PES, 2*NUM_PEGS),
            "fifo_flag_%dx%d " % (2, 2*NUM_PEGS),
            # vmod gen
            "presum_%d " %(NUM_PES),
            "pfxdense_%d " %(NUM_PES),
            # parameter
            "parameter   DATA_TYPE   = %d," % (IN_DATA_TYPE),
            "parameter   NUM_PEGS    = %d," % (NUM_PEGS),
            "parameter   LOG2_PEGS   = %d," % (LOG2_PEGS),
            "parameter   NUM_PES     = %d," % (NUM_PES),
            "parameter   LOG2_PES    = %d," % (LOG2_PES),
            "parameter   LOG2_MEMD   = %d," % (LOG2_MEMD),
            "parameter   POINTER_WIDTH=%d)" % (POINTER_WIDTH)
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