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

# ====================== read data ===================
# MK = np.loadtxt("MK_%d.txt" % NUM_PES, dtype='int', delimiter=',')
# KN = np.loadtxt("KN_%d.txt" % (NUM_PES), dtype='int', delimiter=',')
MK = np.loadtxt(data_path + "MK_s%d.txt" % (int(SPARSITY*10)), dtype='int', delimiter=',')
KN = np.loadtxt(data_path + "KN.txt", dtype='int', delimiter=',')

# K dimension need zeros padding
if(k % (PARA_BLOCKS*NUM_PES)):
    k_pad = PARA_BLOCKS * NUM_PES * math.ceil(k/(PARA_BLOCKS*NUM_PES))
else:
    k_pad = k

# ====================== buff schedule ===================

# (1) data
data_py = []
# (2) stationary
stationary_py = []
# (3) dest
dest_py = []
# (4) row_vn
row_vn_py = []
# (5) add
add_py = []
# (6) block_vn
block_vn_py = []

# (1) data
MK_data = ""
KN_data = ""
# (2) stationary
stationary = ""
# (3) dest
dest = ""
# (4) row_vn
row_vn = ""
# (5) add
add = ""
# (6) block_vn
block_vn = ""

counter_pe = 0
counter_peg = 0
counter_xpeg = 0
blk_col = []
zero_pad = False
# iterate fine-grained blocks
for i0 in range(math.floor(M_DIM/NUM_PEGS)):
    for j0 in range(int(k/NUM_PES)):
        # 1. during fine-grained blocks
        for i1 in range(NUM_PEGS):
            for j1 in range(NUM_PES):

                i = i0*NUM_PEGS+i1
                j = j0*NUM_PES+j1
                # print(i, j)

                if(MK[i][j] != 0):
                    # (1) data
                    MK_data = signed_dec2hex(MK[i][j], int(IN_DATA_TYPE/4))[2:] + MK_data
                    # (3) dest
                    dest = unsigned_dec2bin(j1, LOG2_PES) + dest
                    # (4) row_vn
                    row_vn = unsigned_dec2bin(i1, LOG2_PEGS) + row_vn
                    # counter
                    counter_pe += 1
                    if(i1 == NUM_PEGS-1):
                        zero_pad = False
                    else:
                        zero_pad = True
                

                if(counter_pe == NUM_PES):
                    # (2) stationary
                    stationary = "1" + stationary
                    # (5) add
                    last_flag = True
                    for j2 in range(j1+1, NUM_PES):
                        if(MK[i][j0*NUM_PES+j2] != 0):
                            last_flag = False
                    if(last_flag or counter_peg == NUM_PEGS-1):
                        add = "0" + add
                    else:
                        add = "1" + add
                    # (6) block_vn
                    block_vn = unsigned_dec2bin(i0%NUM_PEGS, LOG2_PEGS) + block_vn
                    # counter
                    counter_pe = 0
                    counter_peg += 1
                    blk_col.append(j0)


                if(counter_peg == NUM_PEGS):
                    # 1st first for MK
                    # (1) data
                    data_py.append(MK_data)
                    MK_data = ""
                    # (2) stationary
                    stationary_py.append(unsigned_bin2hex(stationary, int(NUM_PEGS/4)))
                    stationary = ""
                    # (3) dest
                    dest_py.append(unsigned_bin2hex(dest, int(NUM_PEGS*NUM_PES*LOG2_PES/4)))
                    # (4) vn
                    row_vn_py.append(unsigned_bin2hex(row_vn, int(NUM_PEGS*NUM_PES*LOG2_PEGS/4)))
                    # (5) add
                    add_py.append(unsigned_bin2hex(add, int(NUM_PEGS/4)))
                    # (6) block_vn
                    block_vn_py.append(unsigned_bin2hex(block_vn, int(NUM_PEGS*LOG2_PEGS/4)))
                    # counter
                    counter_peg = 0
                    # backup_fifo equals -1 (if the fgb is finished)
                    counter_xpeg = -1

                    # 2nd second for KN
                    for j2 in range(N_DIM):
                        # for each peg
                        for it in blk_col:
                            # (1) data
                            for i2 in range(NUM_PES):
                                KN_data = signed_dec2hex(KN[it*NUM_PES+i2][j2], int(IN_DATA_TYPE/4))[2:] + KN_data
                        data_py.append(KN_data)
                        KN_data = ""
                        # (2) stationary
                        for i2 in range(NUM_PES):
                            stationary = "0" + stationary
                        stationary_py.append(unsigned_bin2hex(stationary, int(NUM_PEGS/4)))
                        stationary = ""
                        # (3) dest
                        dest_py.append(unsigned_bin2hex(dest, int(NUM_PEGS*NUM_PES*LOG2_PES/4)))
                        # (4) vn
                        row_vn_py.append(unsigned_bin2hex(row_vn, int(NUM_PEGS*NUM_PES*LOG2_PEGS/4)))
                        # (5) add
                        add_py.append(unsigned_bin2hex(add, int(NUM_PEGS/4)))
                        # (6) block_vn
                        block_vn_py.append(unsigned_bin2hex(block_vn, int(NUM_PEGS*LOG2_PEGS/4)))
                    dest = ""
                    row_vn = ""
                    add = ""
                    block_vn = ""
                    blk_col = []

        # 2. at the end of a fine-grained block, padding
        if(counter_pe != 0 or (counter_pe == 0 and zero_pad)):
            for i1 in range(NUM_PES-counter_pe):
                MK_data = signed_dec2hex(0, int(IN_DATA_TYPE/4))[2:] + MK_data
                dest = unsigned_dec2bin(NUM_PES-1, LOG2_PES) + dest
                row_vn = unsigned_dec2bin(NUM_PEGS-1, LOG2_PEGS) + row_vn
            stationary = "1" + stationary
            add = "0" + add
            block_vn = unsigned_dec2bin(i0%NUM_PEGS, LOG2_PEGS) + block_vn
            counter_pe = 0
            counter_peg += 1
            blk_col.append(j0)
            
        counter_xpeg += 1
        # if(len(data_py) == 38055):
        #     print("here x", counter_xpeg, counter_peg, counter_pe)
        
        if(counter_xpeg == PARA_BLOCKS):
            # padding for NUM_PEGS
            while(counter_peg != 0 and counter_peg < NUM_PEGS):
                for i2 in range(NUM_PES):
                    MK_data = signed_dec2hex(0, int(IN_DATA_TYPE/4))[2:] + MK_data
                    dest = unsigned_dec2bin(0, LOG2_PES) + dest
                    row_vn = unsigned_dec2bin(0, LOG2_PEGS) + row_vn
                stationary = "1" + stationary
                add = "0" + add
                block_vn = unsigned_dec2bin(i0%NUM_PEGS, LOG2_PEGS) + block_vn
                counter_peg += 1
                blk_col.append(j0)

        if(counter_peg == NUM_PEGS):
            # 1st first for MK
            # (1) data
            data_py.append(MK_data)
            MK_data = ""
            # (2) stationary
            stationary_py.append(unsigned_bin2hex(stationary, int(NUM_PEGS/4)))
            stationary = ""
            # (3) dest
            dest_py.append(unsigned_bin2hex(dest, int(NUM_PEGS*NUM_PES*LOG2_PES/4)))
            # (4) vn
            row_vn_py.append(unsigned_bin2hex(row_vn, int(NUM_PEGS*NUM_PES*LOG2_PEGS/4)))
            # (5) add
            add_py.append(unsigned_bin2hex(add, int(NUM_PEGS/4)))
            # (6) block_vn
            block_vn_py.append(unsigned_bin2hex(block_vn, int(NUM_PEGS*LOG2_PEGS/4)))
            # counter
            counter_peg = 0
            counter_xpeg = 0

            # 2nd second for KN
            for j2 in range(N_DIM):
                # for each peg
                for it in blk_col:
                    # (1) data
                    for i2 in range(NUM_PES):
                        KN_data = signed_dec2hex(KN[it*NUM_PES+i2][j2], int(IN_DATA_TYPE/4))[2:] + KN_data
                data_py.append(KN_data)
                KN_data = ""
                # (2) stationary
                for i2 in range(NUM_PES):
                    stationary = "0" + stationary
                stationary_py.append(unsigned_bin2hex(stationary, int(NUM_PEGS/4)))
                stationary = ""
                # (3) dest
                dest_py.append(unsigned_bin2hex(dest, int(NUM_PEGS*NUM_PES*LOG2_PES/4)))
                # (4) vn
                row_vn_py.append(unsigned_bin2hex(row_vn, int(NUM_PEGS*NUM_PES*LOG2_PEGS/4)))
                # (5) add
                add_py.append(unsigned_bin2hex(add, int(NUM_PEGS/4)))
                # (6) block_vn
                block_vn_py.append(unsigned_bin2hex(block_vn, int(NUM_PEGS*LOG2_PEGS/4)))
            dest = ""
            row_vn = ""
            add = ""
            block_vn = ""
            blk_col = []






###########################################
# 1.2 - keep py results in files
###########################################

f_data = open(f_path + "tb_buff_data_py.txt", mode='w')
f_stationary = open(f_path + "tb_buff_stationary_py.txt", mode='w')
f_dest = open(f_path + "tb_buff_dest_py.txt", mode='w')
f_row_vn = open(f_path + "tb_buff_row_vn_py.txt", mode='w')
f_add = open(f_path + "tb_buff_add_py.txt", mode='w')
f_block_vn = open(f_path + "tb_buff_block_vn_py.txt", mode='w')

for i in range(len(data_py)):
    # (1) data
    f_data.write(data_py[i] + "\n") 
    # (2) stationary
    f_stationary.write(stationary_py[i] + "\n")
    # (3) dest
    f_dest.write(dest_py[i] + "\n")
    # (4) row_vn
    f_row_vn.write(row_vn_py[i] + "\n")
    # (5) add
    f_add.write(add_py[i] + "\n")
    # (6) block_vn
    f_block_vn.write(block_vn_py[i] + "\n")

# 3 关闭文件
f_data.close()
f_stationary.close()
f_dest.close()
f_row_vn.close()
f_add.close()
f_block_vn.close()






###########################################
# 2.1 - read results from vmod & py_files
###########################################

# (1) data
data_py = []
with open(f_path + "tb_buff_data_py.txt") as f:
    line = f.readline()
    while line:
        data_py.append(line.replace("\n", ""))
        line = f.readline()

data_v = []
cnt = 0
with open(f_path + "tb_buff_data.txt") as f:
    line = f.readline()
    while cnt < len(data_py):
        cnt += 1
    # while line:
        data_v.append(line.replace("\n", ""))
        line = f.readline()


# (2) stationary
stationary_py = []
with open(f_path + "tb_buff_stationary_py.txt") as f:
    line = f.readline()
    while line:
        stationary_py.append(line.replace("\n", ""))
        line = f.readline()

stationary_v = []
cnt = 0
with open(f_path + "tb_buff_stationary.txt") as f:
    line = f.readline()
    while cnt < len(stationary_py):
        cnt += 1
    # while line:
        stationary_v.append(line.replace("\n", ""))
        line = f.readline()


# (3) dest
dest_py = []
with open(f_path + "tb_buff_dest_py.txt") as f:
    line = f.readline()
    while line:
        dest_py.append(line.replace("\n", ""))
        line = f.readline()

dest_v = []
cnt = 0
with open(f_path + "tb_buff_dest.txt") as f:
    line = f.readline()
    while cnt < len(dest_py):
        cnt += 1
    # while line:
        dest_v.append(line.replace("\n", ""))
        line = f.readline()


# (4) row_vn
row_vn_py = []
with open(f_path + "tb_buff_row_vn_py.txt") as f:
    line = f.readline()
    while line:
        row_vn_py.append(line.replace("\n", ""))
        line = f.readline()

row_vn_v = []
cnt = 0
with open(f_path + "tb_buff_row_vn.txt") as f:
    line = f.readline()
    while cnt < len(row_vn_py):
        cnt += 1
    # while line:
        row_vn_v.append(line.replace("\n", ""))
        line = f.readline()


# (5) add
add_py = []
with open(f_path + "tb_buff_add_py.txt") as f:
    line = f.readline()
    while line:
        add_py.append(line.replace("\n", ""))
        line = f.readline()

add_v = []
cnt = 0
with open(f_path + "tb_buff_add.txt") as f:
    line = f.readline()
    while cnt < len(add_py):
        cnt += 1
    # while line:
        add_v.append(line.replace("\n", ""))
        line = f.readline()


# (6) block_vn
block_vn_py = []
with open(f_path + "tb_buff_block_vn_py.txt") as f:
    line = f.readline()
    while line:
        block_vn_py.append(line.replace("\n", ""))
        line = f.readline()

block_vn_v = []
cnt = 0
with open(f_path + "tb_buff_block_vn.txt") as f:
    line = f.readline()
    while cnt < len(block_vn_py):
        cnt += 1
    # while line:
        block_vn_v.append(line.replace("\n", ""))
        line = f.readline()






###########################################
# 2.2 - compare 2 results to verify
###########################################
print("item lens: %d" % len(data_py))

error_flag = False
for i in range(len(data_py)):
    # (1) data
    if(data_v[i] != data_py[i]):
        error_flag = True
        print("[buff_data - DATA ERROR]")
        print("buff_data_py[%d]: " % i, data_py[i])
        print("buff_data_v[%d]: " % i, data_v[i])
        break
    # (2) stationary
    if(stationary_v[i] != stationary_py[i]):
        error_flag = True
        print("[buff_stationary - STATIONARY ERROR]")
        print("buff_stationary_py[%d]: " % i, stationary_py[i])
        print("buff_stationary_v[%d]: " % i, stationary_v[i])
        break
    # (3) dest
    if(dest_v[i] != dest_py[i]):
        error_flag = True
        print("[buff_dest - DEST ERROR]")
        print("buff_dest_py[%d]: " % i, dest_py[i])
        print("buff_dest_v[%d]: " % i, dest_v[i])
        break
    # (4) row_vn
    if(row_vn_v[i] != row_vn_py[i]):
        error_flag = True
        print("[buff_row_vn - ROW_VN ERROR]")
        print("buff_row_vn_py[%d]: " % i, row_vn_py[i])
        print("buff_row_vn_v[%d]: " % i, row_vn_v[i])
        break
    # (5) add
    if(add_v[i] != add_py[i]):
        error_flag = True
        print("[buff_add - ADD ERROR]")
        print("buff_add_py[%d]: " % i, add_py[i])
        print("buff_add_v[%d]: " % i, add_v[i])
        break
    # (6) block_vn
    if(block_vn_v[i] != block_vn_py[i]):
        error_flag = True
        print("[buff_block_vn - BLOCK VN ERROR]")
        print("buff_block_vn_py[%d]: " % i, block_vn_py[i])
        print("buff_block_vn_v[%d]: " % i, block_vn_v[i])
        break

if(error_flag == False):
    print("[buff - CORRECT]")
