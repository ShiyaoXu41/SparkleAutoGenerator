import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


import numpy as np
import math
import random



# the dimension of the matrix
m = M_DIM
k = K_DIM
n = N_DIM

# the sparsity of weight mat (MK)
sparsity = SPARSITY


# the size of the coarse_grained block
cgb_size = (pow(2, LOG2_MEMD))*NUM_PES


# ===================== mat_gen ========================

# 1. generate dense matrix
# K dimension need zeros padding
if(k % (PARA_BLOCKS*NUM_PES)):
    k_pad = PARA_BLOCKS * NUM_PES * math.ceil(k/(PARA_BLOCKS*NUM_PES))
else:
    k_pad = k

print("K_PAD is %d, K is %d" % (k_pad, k))


# int8: [-128, 127]
KN = np.random.randint(-10, 10, (k_pad, n))

for i in range(k_pad):
    for j in range(n):
        if(k <= i):
            KN[i][j] = 0
        else:
            rand_num = random.random()  # generate num in [0, 1]
            # if(rand_num < sparsity):
            #     KN[i][j] = 0



np.savetxt(root_path + "\sim\data\KN.txt", KN, fmt='%d', delimiter=',')

print("1. finish KN mat_gen")



# ====================== file gen ===================

# 0. store the raw data

# f = open("KN_%dx%dx%d.txt" % (LOG2_MEMD, NUM_PEGS, NUM_PES), "w")
# for i in range(k_pad):
#     f.write(','.join(KN[i]) + "\n")
# f.close()
KN = np.loadtxt(root_path + "\sim\data\KN.txt", dtype=int, delimiter=',')
print(KN)


# 1. divide the whole matrix into coarse_grained blocks (cgb)
# row_dim aims MK mat
cgb_row_size = NUM_PEGS * math.floor( cgb_size / (NUM_PEGS*k_pad) )
cgb_row_num = math.ceil( m / cgb_row_size )

# col_dim aims KN mat
cgb_col_size = math.floor( cgb_size / k_pad )
cgb_col_num = math.ceil( n / cgb_col_size )

cgb_row_size = min(m, cgb_row_size)
cgb_col_size = min(n, cgb_col_size)


# 2. generate data files(.coe)
bit_wirte_width = NUM_PES
pointer_write_width = POINTER_WIDTH
data_write_width = 2*NUM_PES


# KN matrix

data_write_width = PARA_BLOCKS*NUM_PES

# for col in range(cgb_col_num):

# f_data = open("KN_data_%dx%dx%d_%d.coe" % (NUM_PEGS, NUM_PES, LOG2_MEMD, col), "w")
f_data = open(root_path + "\sim\data\KN_data.coe", "w")
f_data.write("memory_initialization_radix = 2;\n")
f_data.write("memory_initialization_vector =\n")
KN_data = ""

counter = 0

# print(cgb_col_size, k_pad)
for i in range(cgb_col_size):
    # x = col * cgb_col_size + i
    x = 0 * cgb_col_size + i
    if(n <= x):
        break
    for j in range(k_pad):
        y = j
        # print(y,x)
        KN_data = signed_dec2bin(KN[y][x], IN_DATA_TYPE)[2:] + KN_data
        counter += 1

        if(i == cgb_col_size - 1 and j == k_pad - 1):
            f_data.write(KN_data + ";")
        else:
            if(counter % data_write_width == 0 and len(KN_data) != 0):
                f_data.write(KN_data + ",\n")
                KN_data = ""

f_data.close()



print("2. finish KN_file_gen")



