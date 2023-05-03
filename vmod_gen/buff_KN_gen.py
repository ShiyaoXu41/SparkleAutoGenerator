# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
source_path = os.getcwd() + "\\vmod\\"
target_path = root_path + "\\vmod\\"

# ================ 2. list replaced str ================
# ======================================================
file_name = "buff_KN.v"

old_str = [
            # IP Core
            "fifo_KN_data_backup ",
            # parameters
            "parameter                                                       NUM_PEGS        ,",
            "parameter                                                       LOG2_PEGS       ,",
            "parameter                                                       NUM_PES         ,",
            "parameter                                                       DATA_TYPE       ,",
            "parameter                                                       PARA_BLOCKS     ,",
            "parameter                                                       LOG2_PARA_BLOCKS"
           ]

new_str = [
            # IP Core
            "fifo_KN_data_backup_%dx%d " % (NUM_PES*IN_DATA_TYPE, MAX_N_DIM),
            # parameters
            "parameter                                                       NUM_PEGS        = %d," % (NUM_PEGS),
            "parameter                                                       LOG2_PEGS       = %d," % (LOG2_PEGS),
            "parameter                                                       NUM_PES         = %d," % (NUM_PES),
            "parameter                                                       DATA_TYPE       = %d," % (IN_DATA_TYPE),
            "parameter                                                       PARA_BLOCKS     = %d," % (PARA_BLOCKS),
            "parameter                                                       LOG2_PARA_BLOCKS= %d"  % (LOG2_PARA_BLOCKS)
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