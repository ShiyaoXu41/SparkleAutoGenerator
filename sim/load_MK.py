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

# the sparsity of weight mat (MK)
sparsity = SPARSITY


#################################################
# 1st - generate correct results
#################################################

# ====================== read data ===================
MK = np.loadtxt(data_path + "MK_%d.txt" % (int(sparsity*10)), dtype='int', delimiter=',')


# K dimension need zeros padding
if(k % NUM_PES):
    k_pad = NUM_PES * math.ceil(k/NUM_PES)
else:
    k_pad = k

# ====================== load data ===================

# output      [DATA_TYPE * NUM_PES - 1 : 0]       o_fifo_MK_data_out
# output      [LOG2_PES * NUM_PES - 1 : 0]        o_fifo_dest_out
# output      [LOG2_PES * NUM_PES - 1 : 0]        o_fifo_vn_out
# output      [1 : 0]                             o_fifo_flag_out

load_MK_data_py = []
load_dest_py = []
load_vn_py = []
load_flag_py = []

MK_data = ""
dest = ""
vn = ""
flag = ""

counter = 0
# iterate fine-grained blocks
for i0 in range(math.floor(M_DIM/NUM_PEGS)):
    for j0 in range(int(k_pad/NUM_PES)):
        # 1. during fine-grained blocks
        for i1 in range(NUM_PEGS):
            for j1 in range(NUM_PES):

                i = i0*NUM_PEGS+i1
                j = j0*NUM_PES+j1

                # MK_data, dest, vn
                if(MK[i][j] != 0):
                    # print(MK[i][j])
                    MK_data = signed_dec2hex(MK[i][j], int(IN_DATA_TYPE/4))[2:] + MK_data
                    dest = unsigned_dec2bin(j1, LOG2_PES) + dest
                    vn = unsigned_dec2bin(i1, LOG2_PEGS) + vn
                    counter += 1
                
                # flag
                if(counter == NUM_PES):
                    # iterate the remaining data in the row
                    last_flag = True
                    for j2 in range(j1+1, NUM_PES):
                        if(MK[i][j0*NUM_PES+j2] != 0):
                            last_flag = False
                    if(last_flag):
                        if(i1 == NUM_PEGS-1):
                            if(j0 == int(K_DIM/NUM_PES)-1):
                                flag = "11"
                            else:
                                flag = "10"
                        else:
                            flag = "00"
                    else:
                        flag = "01"
                    
                    # append and clear
                    load_MK_data_py.append(MK_data)
                    load_dest_py.append(unsigned_bin2hex(dest, int(NUM_PES*LOG2_PES/4)))
                    load_vn_py.append(unsigned_bin2hex(vn, int(NUM_PES*LOG2_PEGS/4)))
                    load_flag_py.append(flag)
                    MK_data = ""
                    dest = ""
                    vn = ""
                    flag = ""
                    counter = 0
                            
        # 2. at the end of a fine-grained block, padding
        if(counter != 0):
            for i1 in range(NUM_PES-counter):
                MK_data = signed_dec2hex(0, int(IN_DATA_TYPE/4))[2:] + MK_data
                dest = unsigned_dec2bin(NUM_PES-1, LOG2_PES) + dest
                vn = unsigned_dec2bin(NUM_PEGS-1, LOG2_PEGS) + vn
            if(j0 == int(K_DIM/NUM_PES)-1):
                flag = "11"
            else:
                flag = "10"
            # append and clear
            load_MK_data_py.append(MK_data)
            load_dest_py.append(unsigned_bin2hex(dest, int(NUM_PES*LOG2_PES/4)))
            load_vn_py.append(unsigned_bin2hex(vn, int(NUM_PES*LOG2_PEGS/4)))
            load_flag_py.append(flag)
            MK_data = ""
            dest = ""
            vn = ""
            flag = ""
            counter = 0

# print(len(load_MK_data_py))



###########################################
# 2nd - read results from vmod
###########################################

cnt = 0
load_MK_data_v = []
with open(f_path + "tb_load_MK_data.txt" ) as f:
    line = f.readline()
    while cnt < len(load_MK_data_py):
        cnt += 1
    # while line:
        load_MK_data_v.append(line.replace("\n", ""))
        line = f.readline()

cnt = 0
load_dest_v = []
with open(f_path + "tb_load_dest.txt" ) as f:
    line = f.readline()
    while cnt < len(load_dest_py):
        cnt += 1
    # while line:
        load_dest_v.append(line.replace("\n", ""))
        line = f.readline()

cnt = 0
load_vn_v = []
with open(f_path + "tb_load_vn.txt" ) as f:
    line = f.readline()
    while cnt < len(load_vn_py):
        cnt += 1
    # while line:
        load_vn_v.append(line.replace("\n", ""))
        line = f.readline()

cnt = 0
load_flag_v = []
with open(f_path + "tb_load_flag.txt" ) as f:
    line = f.readline()
    while cnt < len(load_flag_py):
        cnt += 1
    # while line:
        load_flag_v.append(line.replace("\n", ""))
        line = f.readline()





###########################################
# 3rd - compare 2 results to verify
###########################################
print("item lens: %d" % len(load_MK_data_py))

error_flag = False
for i in range(len(load_MK_data_py)):
    if(load_MK_data_v[i] != load_MK_data_py[i]):
        error_flag = True
        print("[load_MK_data - MK DATA ERROR]" )
        print("load_MK_data_py[%d]: " % i, load_MK_data_py[i])
        print("load_MK_data_v[%d]: " % i, load_MK_data_v[i])
        break
    if(load_dest_v[i] != load_dest_py[i]):
        error_flag = True
        print("[load_dest - DEST ERROR]" )
        print("load_dest_py[%d]: " % i, load_dest_py[i])
        print("load_dest_v[%d]: " % i, load_dest_v[i])
        break
    if(load_vn_v[i] != load_vn_py[i]):
        error_flag = True
        print("[load_vn - VN ERROR]" )
        print("load_vn_py[%d]: " % i, load_vn_py[i])
        print("load_vn_v[%d]: " % i, load_vn_v[i])
        break
    if(load_flag_v[i] != load_flag_py[i]):
        error_flag = True
        print("[load_flag - FLAG ERROR]" )
        print("load_flag_py[%d]: " % i, load_flag_py[i])
        print("load_flag_v[%d]: " % i, load_flag_v[i])
        break

if(error_flag == False):
    print("[load_MK - CORRECT]" )





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



