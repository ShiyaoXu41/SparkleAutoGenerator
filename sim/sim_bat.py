# remove sim py files into new folders

import sys 
sys.path.append(".") 
from parameters import *


if not os.path.exists(root_path + "\\sim"):
    os.makedirs(root_path + "\\sim")

source_path = os.getcwd() + "\\sim\\"
target_path = root_path + "\\sim\\"


from shutil import copyfile
copyfile(source_path + "top.py", target_path + "top.py")
copyfile(source_path + "MK_data_gen.py", target_path + "MK_data_gen.py")
copyfile(source_path + "KN_data_gen.py", target_path + "KN_data_gen.py")
copyfile(source_path + "load_MK.py", target_path + "load_MK.py")
copyfile(source_path + "load_KN.py", target_path + "load_KN.py")
copyfile(source_path + "buff_res.py", target_path + "buff_res.py")
copyfile(source_path + "peg_res.py", target_path + "peg_res.py")
copyfile(source_path + "mid_res.py", target_path + "mid_res.py")
copyfile(source_path + "fin_res.py", target_path + "fin_res.py")
copyfile(source_path + "accum_res.py", target_path + "accum_res.py")

