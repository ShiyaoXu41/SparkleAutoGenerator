# remove dec & parameters py files into new folders

import sys 
sys.path.append(".") 
from parameters import *


source_path = os.getcwd() + "\\"
target_path = root_path + "\\"


from shutil import copyfile
copyfile(source_path + "parameters.py", target_path + "parameters.py")
copyfile(source_path + "dec_conv_func.py", target_path + "dec_conv_func.py")
