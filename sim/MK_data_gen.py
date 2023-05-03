
'''
# ==================== coarse grained blocks ===================
# dived the matrix into cgbs
# ==============================================================
cgb_size = 1024*1024
max_n = 256

M = [768, 3072, 768, 128, 320, 1632, 2048, 256, 169343, 169343]
K = [768, 768, 3072, 4096, 4096, 1024, 128, 2048, 256, 256]
N = [128, 128, 128, 2048, 3072, 36548, 1, 256, 168, 256]

for i in range(len(M)):  
    x1 = 1
    m1 = M[i]
    x2 = 0
    m2 = 0
    if(cgb_size < M[i]*K[i]):
        x1 = math.ceil(M[i]*K[i]/cgb_size)
        m1 = M[i] / x1
        while(m1 % 32 != 0):
            x1 += 1
            m1 = M[i] / x1
        x2 = 0
        if(M[i] % x1 != 0):
            m1 = math.floor(cgb_size/K[i])
            x1 = math.floor(M[i]/m1)
            x2 = 1
            m2 = M[i] - m1*x1
    y1 = 1
    n1 = N[i]
    y2 = 0
    n2 = 0
    if(cgb_size < K[i]*N[i]):
        y1 = math.ceil(N[i]/max_n)
        n1 = max_n
        if(N[i] % y1 != 0):
            y2 = 1
            n2 = N[i] - n1*y1 
    print("%d x [%d, %d, %d] x %d" % (x1, m1, K[i], n1, y1))
    if(x2 != 0):
        print("%d x [%d, %d, %d] x %d" % (x2, m2, K[i], n1, y1))
        print("%d x [%d, %d, %d] x %d" % (x2, m2, K[i], n2, y2))
    if(y2 != 0):
        print("%d x [%d, %d, %d] x %d" % (x1, m1, K[i], n2, y2))
        print("%d x [%d, %d, %d] x %d" % (x2, m2, K[i], n2, y2))
    print()
# ==============================================================
# ==============================================================
'''

import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


if not os.path.exists(root_path + "\sim\data"):
    os.makedirs(root_path + "\sim\data")

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
if(k % NUM_PES):
    k_pad = NUM_PES * math.ceil(k/NUM_PES)
else:
    k_pad = k


# int8: [-128, 127]
MK = np.random.randint(-10, 10, (m, k_pad))
KN = np.random.randint(-10, 10, (k_pad, n))

true_sp = 0
# 2. turn the dense matrxi to the sparsity format
for i in range(m):
    for j in range(k_pad):
        if(k <= j):
            MK[i][j] = 0
        else:
            rand_num = random.random()  # generate num in [0, 1]
            if(rand_num < sparsity):
                MK[i][j] = 0
                true_sp += 1
s = true_sp/(m*k_pad)
# print(s)

for i in range(k_pad):
    for j in range(n):
        if(k <= i):
            KN[i][j] = 0
        else:
            rand_num = random.random()  # generate num in [0, 1]
            if(rand_num < sparsity):
                KN[i][j] = 0



np.savetxt(root_path + "\sim\data\MK_s%d.txt" % (int(sparsity*10)), MK, fmt='%d', delimiter=',')

print("1. finish mat_gen")



# ====================== file gen ===================

# 0. store the raw data
# f = open("MK_%dx%dx%d.txt" % (LOG2_MEMD, NUM_PEGS, NUM_PES), "w")
# for i in range(m):
#     f.write(','.join(MK[i]) + "\n")
# f.close()
MK = np.loadtxt(root_path + "\sim\data\MK_s%d.txt" % (int(sparsity*10)), dtype=int, delimiter=',')

# f = open("KN_%dx%dx%d.txt" % (LOG2_MEMD, NUM_PEGS, NUM_PES), "w")
# for i in range(k_pad):
#     f.write(','.join(KN[i]) + "\n")
# f.close()
# np.savetxt("KN_%dx%d.txt" % (NUM_PEGS, NUM_PES), KN, fmt='%d', delimiter=',')


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



# MK matrix in sparse format
# for row in range(cgb_row_num):

# f_bitmap = open("MK_bitmap_%dx%dx%d_%d.coe" % (NUM_PEGS, NUM_PES, LOG2_MEMD, row), "w")
f_bitmap = open(root_path + "\sim\data\MK_bitmap_s%d.coe" % (int(sparsity*10)), "w")
f_bitmap.write("memory_initialization_radix = 2;\n")
f_bitmap.write("memory_initialization_vector =\n")
MK_bitmap = ""

# f_pointer = open("MK_pointer_%dx%dx%d_%d.coe" % (NUM_PEGS, NUM_PES, LOG2_MEMD, row), "w")
f_pointer = open(root_path + "\sim\data\MK_pointer_s%d.coe" % (int(sparsity*10)), "w")
f_pointer.write("memory_initialization_radix = 2;\n")
f_pointer.write("memory_initialization_vector =\n")
f_pointer.write(unsigned_dec2bin(0, pointer_write_width))

# f_data = open("MK_data_%dx%dx%d_%d.coe" % (NUM_PEGS, NUM_PES, LOG2_MEMD, row), "w")
f_data = open(root_path + "\sim\data\MK_data_s%d.coe" % (int(sparsity*10)), "w")
f_data.write("memory_initialization_radix = 2;\n")
f_data.write("memory_initialization_vector =\n")
MK_data = ""

counter = 0

for i in range(cgb_row_size):
    # x = row * cgb_row_size + i
    x = 0 * cgb_row_size + i
    if(m <= x):
        break
    for j in range(k_pad):
        y = j
        # print(x,y)

        if(MK[x][y] == 0):
            MK_bitmap = "0" + MK_bitmap
        else:
            MK_bitmap = "1" + MK_bitmap

            MK_data = signed_dec2bin(MK[x][y], IN_DATA_TYPE)[2:] + MK_data
            counter += 1
        
        if(i == cgb_row_size - 1 and j == k_pad - 1):
            f_bitmap.write(MK_bitmap + ";")
            f_pointer.write(";")
            f_data.write(MK_data + ";")
        else:
            if((i * k_pad + j + 1) % bit_wirte_width == 0):
                f_bitmap.write(MK_bitmap + ",\n")
                f_pointer.write(",\n" + unsigned_dec2bin(counter, pointer_write_width))
                MK_bitmap = ""

            if(counter % data_write_width == 0 and len(MK_data) != 0):
                f_data.write(MK_data + ",\n")
                MK_data = ""

f_bitmap.close()
f_pointer.close()
f_data.close()



print("2. finish MK_file_gen")


# # KN matrix

# data_write_width = PARA_BLOCKS*NUM_PES

# # for col in range(cgb_col_num):

# # f_data = open("KN_data_%dx%dx%d_%d.coe" % (NUM_PEGS, NUM_PES, LOG2_MEMD, col), "w")
# f_data = open("KN_data_%dx%d.coe" % (NUM_PEGS, NUM_PES), "w")
# f_data.write("memory_initialization_radix = 2;\n")
# f_data.write("memory_initialization_vector =\n")
# KN_data = ""

# counter = 0

# for i in range(cgb_col_size):
#     # x = col * cgb_col_size + i
#     x = 0 * cgb_col_size + i
#     if(n <= x):
#         break
#     for j in range(k_pad):
#         y = j
#         # print(y,x)
#         KN_data = signed_dec2bin(KN[y][x], IN_DATA_TYPE)[2:] + KN_data
#         counter += 1

#         if(i == cgb_col_size - 1 and j == k_pad - 1):
#             f_data.write(KN_data + ";")
#         else:
#             if((i * k_pad + j + 1) % bit_wirte_width == 0):
#                 KN_bitmap = ""

#             if(counter % data_write_width == 0 and len(KN_data) != 0):
#                 f_data.write(KN_data + ",\n")
#                 KN_data = ""

# f_data.close()



# print("2.2 finish KN_file_gen")

