import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


import math


DATA_TYPE = OUT_DATA_TYPE

N_DIM = 5
# ena_num = 4 # 00, 01, 11, 10
ena_num = 5 # 00, 01, 11, 11, 10


#################################################
# 1st - generate correct results [valid0_py, data0_py, valid1_py, data1_py] 
#################################################

valid0_py = []
data0_py = []
for i in range(PARA_BLOCKS+1, 0, -1):
    for j in range(N_DIM*ena_num):
        num = int(NUM_PEGS / math.ceil(NUM_PEGS/i))
        # valid0_py.append(unsigned_bin2hex(i*"1",math.ceil((PARA_BLOCKS+1)/4)))
        valid0_py.append(unsigned_bin2hex(num*"1",math.ceil((PARA_BLOCKS+1)/4)))
        temp = ""
        for k in range(NUM_PEGS):
            temp = unsigned_dec2bin(i, DATA_TYPE) + temp
        # temp = temp*i
        # temp = ((PARA_BLOCKS+1-i)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
        temp = temp*num
        temp = ((PARA_BLOCKS+1-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
        data0_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))
# print(valid0_py)
# print(data0_py)



valid1_py = []
data1_py = []
for i in range(PARA_BLOCKS+1, 0, -1):
    num = int(NUM_PEGS / math.ceil(NUM_PEGS/i))
    # acum_en = 00
    for j in range(N_DIM):
        valid1_py.append(unsigned_bin2hex(num*"1",math.ceil((PARA_BLOCKS+1)/4)))
        temp = ""
        for k in range(NUM_PEGS):
            temp = unsigned_dec2bin(i, DATA_TYPE) + temp
        temp = temp*num
        temp = ((PARA_BLOCKS+1-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
        data1_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))
    if(i > 1):
        # acum_en = 10
        for j in range(N_DIM):
            valid1_py.append(unsigned_bin2hex((num-1)*"1",math.ceil((PARA_BLOCKS+1)/4)))
            temp = ""
            for k in range(NUM_PEGS):
                temp = unsigned_dec2bin(i, DATA_TYPE) + temp
            temp = temp*(num-1)
            temp = ((PARA_BLOCKS+2-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
            data1_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))
        # acum_en = 11
        for j in range(N_DIM):
            valid1_py.append(unsigned_bin2hex((num-1)*"1",math.ceil((PARA_BLOCKS+1)/4)))
            temp = ""
            for k in range(NUM_PEGS):
                temp = unsigned_dec2bin(i, DATA_TYPE) + temp
            temp = temp*(num-2)
            for k in range(NUM_PEGS):
                temp += unsigned_dec2bin(2*i, DATA_TYPE)
            temp = ((PARA_BLOCKS+2-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
            data1_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))
        # acum_en = 11
        for j in range(N_DIM):
            valid1_py.append(unsigned_bin2hex((num-1)*"1",math.ceil((PARA_BLOCKS+1)/4)))
            temp = ""
            for k in range(NUM_PEGS):
                temp = unsigned_dec2bin(i, DATA_TYPE) + temp
            temp = temp*(num-2)
            for k in range(NUM_PEGS):
                temp += unsigned_dec2bin(2*i, DATA_TYPE)
            temp = ((PARA_BLOCKS+2-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
            data1_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))
        # acum_en = 01
        for j in range(N_DIM):
            valid1_py.append(unsigned_bin2hex(num*"1",math.ceil((PARA_BLOCKS+1)/4)))
            temp = ""
            for k in range(NUM_PEGS):
                temp = unsigned_dec2bin(i, DATA_TYPE) + temp
            temp = temp*(num-1)
            for k in range(NUM_PEGS):
                temp += unsigned_dec2bin(2*i, DATA_TYPE)
            temp = ((PARA_BLOCKS+2-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
            data1_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))
    else:
        # acum_en = 01 11 11 10
        valid1_py.append(unsigned_bin2hex(num*"1",math.ceil((PARA_BLOCKS+1)/4)))
        temp = ""
        for k in range(NUM_PEGS):
            temp = unsigned_dec2bin(4*i, DATA_TYPE) + temp
        temp = ((PARA_BLOCKS+1-num)*(NUM_PEGS*DATA_TYPE))*"0"+ temp
        data1_py.append(unsigned_bin2hex(temp, (PARA_BLOCKS+1)*NUM_PEGS*DATA_TYPE/4))



###########################################
# 2nd - read results from vmod [valid0_v, data0_v, valid1_v, data1_v] 
###########################################

valid0_v = []
data0_v = []
with open(f_path + "tb_res0.txt") as f:
    line = f.readline()
    while line:

        # split [valid, data]
        line_list = line.split(", ")

        # trasfer valid in binary format 
        valid0_v.append(line_list[0])
        # print(valid,len(valid))

        # get data
        data0_v.append(line_list[1].replace("\n", ""))

        line = f.readline()



valid1_v = []
data1_v = []
with open(f_path + "tb_res1.txt") as f:
    line = f.readline()
    while line:

        # split [valid, data]
        line_list = line.split(", ")

        # trasfer valid in binary format 
        valid1_v.append(line_list[0])
        # print(valid,len(valid))

        # get data
        data1_v.append(line_list[1].replace("\n", ""))

        line = f.readline()



###########################################
# 3rd - compare 2 results to verify
###########################################
error_flag = False
for i in range(len(data0_py)):
    if(valid0_v[i] != valid0_py[i]):
        error_flag = True
        print("[res0 - VALID ERROR]")
        print("valid0_py[%d]: " % i, valid0_py[i])
        print("valid0_v[%d]: " % i, valid0_v[i])
        break
    if(data0_v[i] != data0_py[i]):
        error_flag = True
        print("[res0 - DATA ERROR]")
        print("data0_py[%d]: " % i, data0_py[i])
        # print(len(data0_py[i]))
        print("data0_v[%d]: " % i, data0_v[i])
        # print(len(data0_v[i]))
        break

if(error_flag == False):
    print("[res0 - CORRECT]")


error_flag = False
for i in range(len(data1_py)):
    if(valid1_v[i] != valid1_py[i]):
        error_flag = True
        print("[res1 - VALID ERROR]")
        print("valid1_py[%d]: " % i, valid1_py[i])
        print("valid1_v[%d]: " % i, valid1_v[i])
        break
    if(data1_v[i] != data1_py[i]):
        error_flag = True
        print("[res1 - DATA ERROR]")
        print("data1_py[%d]: " % i, data1_py[i])
        print("data1_v[%d]: " % i, data1_v[i])
        break

if(error_flag == False):
    print("[res1 - CORRECT]")