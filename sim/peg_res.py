import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


import os
f_path = os.path.dirname(os.getcwd()) + "\Sparkle_%dx%d_proj\Sparkle_%dx%d_proj.sim" % (NUM_PEGS, NUM_PES, NUM_PEGS, NUM_PES) + "\sim_1\\behav\xsim\\"



##############################################
# 1st - generate correct results [peg_res_py] 
##############################################

nums = []
for i in range(NUM_PES):
    nums.append(i)

# the whole results
peg_res_py = []
# 'NUM_PES' case
for i in range(NUM_PES):
    # each case
    for j in range(1, NUM_PES - i + 1):
        temp = []
        if(i > 0):
            temp.append(sum(nums[0:i]))
        for k in range(i, NUM_PES, j):
            if(k + j > NUM_PES - 1):
                temp.append(sum(nums[k:]))
            else:
                temp.append(sum(nums[k:k+j]))
        # 'NUM_PEG' in parallel
        temp = temp * NUM_PEGS
        peg_res_py.append(temp)

# print(len(peg_res_py), peg_res_py)






###########################################
# 2nd - read results from vmod [peg_res_v]
###########################################

peg_res_v = []
with open(f_path + "tb_peg.txt") as f:
    line = f.readline()
    while line:

        # split [valid, data]
        line_list = line.split(", ")

        # trasfer valid in binary format
        valid = unsigned_hex2bin(line_list[0], NUM_PEGS*NUM_PES)    
        # print(valid,len(valid))

        # get data
        data = []
        line_list[1] = line_list[1].replace("\n", "")
        for i in range(len(valid)-1, -1, -1):
            if(valid[i] != '0'):
                num = line_list[1][4*i:4*(i+1)]
                data.append(int(num,16))
        peg_res_v.append(data)

        line = f.readline()






###########################################
# 3rd - compare 2 results to verify
###########################################
error_flag = False
for i in range(len(peg_res_py)):
    if(peg_res_v[i] != peg_res_py[i]):
        error_flag = True
        print("[ERROR]")
        print("peg_res_py[%d]: " % i, peg_res_py[i])
        print("peg_res_v[%d]: " % i, peg_res_v[i])
        break

if(error_flag == False):
    print("[CORRECT]\n")

