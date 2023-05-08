
import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


import numpy as np
import math


# the dimension of the matrix
m = M_DIM
k = K_DIM
n = N_DIM


#################################################
# 1.1 - generate correct results
#################################################

MK = np.loadtxt(data_path + "MK_s%d.txt" % (int(SPARSITY*10)), dtype='int', delimiter=',')
KN = np.loadtxt(data_path + "KN.txt", dtype='int', delimiter=',')
KN = KN[:K_DIM,]

# print(type(MK), type(KN))
MN = MK @ KN
# MN = np.dot(MK, KN)
# print(MN)

'''
# ====================== read valid and arrange the results format =================
data_py = []
row_cnt = 0
col_cnt = 0
with open(f_path + "tb_top_valid_%dx%d.txt" % (NUM_PEGS, NUM_PES)) as f:

    line = f.readline()
    while line:

        num = signed_hex2dec(line)

        x = row_cnt
        y = col_cnt % n

        data_temp = MN[x*NUM_PEGS : (x+num)*NUM_PEGS, y]
        data_str = ""
        for d in data_temp:
            data_str = signed_dec2hex(d, int(OUT_DATA_TYPE/4))[2:] + data_str
        data_py.append(data_str)

        if(col_cnt == n-1):
            row_cnt += num
            col_cnt = 0
        else:
            # row_cnt = row_cnt
            col_cnt += 1

        if(row_cnt < math.ceil(m/NUM_PEGS)):
            line = f.readline()
        else:
            break
'''

data_py = []
for x in range(math.ceil(m/NUM_PEGS)):
    for y in range(n):
        data_temp = MN[x*NUM_PEGS : (x+1)*NUM_PEGS, y]
        data_str = ""
        for d in data_temp:
            data_str = signed_dec2hex(d, int(OUT_DATA_TYPE/4))[2:] + data_str
        data_py.append(data_str)


###########################################
# 1.2 - keep py results in files
###########################################

f_data = open(f_path + "tb_top_s%d_py.txt" % (int(SPARSITY*10)), mode='w')

for i in range(len(data_py)):
    f_data.write(data_py[i] + "\n") 

f_data.close()





###########################################
# 2.1 - read results from vmod
###########################################
time_v = []
data_v = []
cnt = 0
with open(f_path + "tb_top_s%d.txt" % (int(SPARSITY*10))) as f:
    line = f.readline()
    while cnt < len(data_py):
        cnt += 1
    # while line:
        # data_v.append(line.replace("\n", ""))
        line = line.replace("\n", "")
        line = line.split(", ")
        if(len(line)>1):
            time_v.append(line[0])
            data_v.append(line[1])
        line = f.readline()
time_v.append("")
data_v.append("")




###########################################
# 2.2 - compare 2 results to verify
###########################################
print("item lens: %d" % len(data_py))

error_flag = False
for i in range(len(data_py)):
    if(data_v[i] != data_py[i]):
        error_flag = True
        print("[top_data - DATA ERROR]")
        print("top_data_py[%d]: " % i, data_py[i])
        print("top_data_v[%d]: " % i, data_v[i])
        break

if(error_flag == False):
    print("[top - CORRECT]")
    print(time_v[len(data_py)-1] + ", " + data_py[len(data_py)-1])