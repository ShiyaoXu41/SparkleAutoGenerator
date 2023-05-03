# ================ 0. import parameters ================
import sys 
sys.path.append(".") 
from parameters import *


# ============== 1. get lcl&tgt vmod path ==============
source_path = os.getcwd() + "\\vmod\\"
target_path = root_path + "\\vmod\\"


# ================ 2. list replaced str ================
# ======================================================
file_name = "mult_switch.v"

old_str = [
            # IP Core
            "Mult ",
            # parameter
            "parameter IN_DATA_TYPE  ,",
	        "parameter OUT_DATA_TYPE )("
           ]

new_str = [
            # IP Core
            "Mult_%d " % (IN_DATA_TYPE),
            # parameter
            "parameter IN_DATA_TYPE  = %d,"  % (IN_DATA_TYPE),
	        "parameter OUT_DATA_TYPE = %d)(" % (OUT_DATA_TYPE)
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