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
# 1st - generate correct results
#################################################

# ====================== read data ======================
KN = np.loadtxt(data_path + "KN.txt", dtype='int', delimiter=',')
# print(len(KN), len(KN[0]), KN[0,32], KN[32,32])

# K dimension need zeros padding
if(k % NUM_PES):
    k_pad = NUM_PES * math.ceil(k/NUM_PES)
else:
    k_pad = k

# ====================== load data ======================

# divide KN mat into PARA_BLOCKS FIFOs
temp = []
for i in range(PARA_BLOCKS):
    temp.append([])

for i0 in range(int(K_DIM/(PARA_BLOCKS*NUM_PES))):
    for j in range(N_DIM):
        for i1 in range(PARA_BLOCKS):
            start = i0*(PARA_BLOCKS*NUM_PES) + i1*NUM_PES
            stop = start + NUM_PES
            temp[i1].append(KN[start:stop,j])
# print(len(temp), len(temp[0]))

# iterate rd_en cases
# 4'b0001, 4'b0010, 4'b0100, 4'b1000
# 4'b0011, 4'b0110, 4'b1100, 4'b1001
# 4'b0111, 4'b1110, 4'b1101, 4'b1011
# 4'b1111
cnt = []
for i in range(PARA_BLOCKS):
    cnt.append(0)

load_KN_data_py = []
# i0 nums (except all ones)
for i0 in range(PARA_BLOCKS-1):
    # for each num
    for i1 in range(PARA_BLOCKS):
        start = i1
        stop = (start + i0) % PARA_BLOCKS
        for j in range(N_DIM):
            load_KN_data = ""
            for i2 in range(PARA_BLOCKS):
                KN_data = ""
                for it in temp[i2][(cnt[i2])%len(temp[i2])][::-1]:
                    KN_data += signed_dec2hex(it, int(IN_DATA_TYPE/4))[2:]
                load_KN_data = KN_data + load_KN_data
                if( (start <= i2 and i2 <= stop) or ((stop < start) and (i2 <= stop or start <= i2)) ):
                    cnt[i2] += 1
            load_KN_data_py.append(load_KN_data)


# the rest output together
while (cnt[0] < len(temp[0])):
    load_KN_data = ""
    for i in range(PARA_BLOCKS):
        KN_data = ""
        for it in temp[i][cnt[i]][::-1]:
            KN_data += signed_dec2hex(it, int(IN_DATA_TYPE/4))[2:]
        load_KN_data = KN_data + load_KN_data
        cnt[i] += 1
    load_KN_data_py.append(load_KN_data)





###########################################
# 2nd - read results from vmod
###########################################

cnt = 0
load_KN_data_v = []
with open(f_path + "tb_load_KN.txt") as f:
    line = f.readline()
    while cnt < len(load_KN_data_py):
        cnt += 1
    # while line:
        load_KN_data_v.append(line.replace("\n", ""))
        line = f.readline()





###########################################
# 3rd - compare 2 results to verify
###########################################
print("item lens: %d" % len(load_KN_data_py))

error_flag = False
for i in range(len(load_KN_data_py)):
    if(load_KN_data_v[i] != load_KN_data_py[i]):
        error_flag = True
        print("[load_KN_data - KN DATA ERROR]")
        print("load_KN_data_py[%d]: " % i, load_KN_data_py[i])
        print("load_KN_data_v[%d]: " % i, load_KN_data_v[i])
        break

if(error_flag == False):
    print("[load_KN - CORRECT]")


print(load_KN_data_py[1])
print(load_KN_data_py[2])

# # =============== final results in [complement] format ===============

# for row in range(cgb_row_num):
#     for col in range(cgb_col_num):
        
#         data_file = open("results_m%d_k%d_n%d_s%.1f_%d%d_py.txt" % (m, k, n, sparsity, row, col), "w")

#         for mm in range(math.ceil(cgb_row_size / 32)):
#             x = row * cgb_row_size + 32*mm
#             for nn in range(cgb_col_size):
#                 y = col * cgb_col_size + nn
#                 if(n <= y):
#                     break
                
#                 # get right vector
#                 data_2 = []
#                 for kk in range(k_pad):
#                     data_2.append(KN[kk][y])
                
#                 if(row == cgb_row_num - 1 and mm == math.ceil(cgb_row_size / 32) - 1):
#                     for i in range(m-1, x-1, -1):
#                         # get left vector
#                         data_1 = []
#                         for kk in range(k_pad):
#                             data_1.append(MK[i][kk])

#                         # get a result
#                         summ = 0
#                         for kk in range(k_pad):
#                             summ += data_1[kk] * data_2[kk]
                        
#                         data_file.write(signed_dec2hex(summ, 4))
#                 else:
#                     for i in range(31, -1, -1):
#                         # get left vector
#                         data_1 = []
#                         for kk in range(k_pad):
#                             data_1.append(MK[x+i][kk])

#                         # get a result
#                         summ = 0
#                         for kk in range(k_pad):
#                             summ += data_1[kk] * data_2[kk]
                        
#                         data_file.write(signed_dec2hex(summ, 4))
#                         # print(summ)
                
#                 data_file.write("\n")

#         data_file.close()

