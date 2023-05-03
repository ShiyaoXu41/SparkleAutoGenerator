import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


#################################################
# 1st - generate correct results [valid0_py, data0_py, valid1_py, data1_py] 
#################################################

sep = int(NUM_PES*0.2)
tms = [0, 1, 2, 3, 4]

valid0_py = []
data0_py = []
temp = 0
for i in tms:
    # intervals simulate the valid data
    itv = NUM_PES-i*sep
    valid0 = ""
    data0 = []
    # allocate as more [NUM_PEGS*itv] nums to [NUM_PEGS*NUM_PES] PES
    d_sum = temp
    for j in range(NUM_PEGS):
        for k in range(NUM_PES):
            d_sum += 1
            if( ((j*NUM_PES+k+1) % itv == 0)):
                valid0 = "1" + valid0
                data0.append(d_sum)
                d_sum = 0
            else:
                valid0 = "0" + valid0
    valid0_py.append(valid0)
    data0_py.append(data0)
    if(NUM_PES % itv != 0):
        temp = d_sum



valid1_py = []
data1_py = []
temp = 0
for i in tms:
    # intervals simulate the valid data
    itv = NUM_PES-i*sep
    valid1 = [str(0) for v in range(NUM_PEGS*NUM_PEGS)]
    data1 = [0 for v in range(NUM_PEGS*NUM_PEGS)]
    d_sum = temp
    for j in range(NUM_PEGS):
        for k in range(NUM_PES):
            d_sum += 1
            if( ((j*NUM_PES+k+1) % itv == 0)):
                valid1[j*NUM_PEGS + (int((j*NUM_PES+k)/itv) % NUM_PEGS)] = "1"
                data1[j*NUM_PEGS + (int((j*NUM_PES+k)/itv) % NUM_PEGS)] = d_sum
                d_sum = 0
    valid1_py.append(''.join(valid1[::-1]))
    data1_py.append(data1)
    if(NUM_PES % itv != 0):
        temp = d_sum


###########################################
# 2nd - read results from vmod [valid0_v, data0_v, valid1_v, data1_v] 
###########################################

valid0_v = []
data0_v = []
with open(f_path + "tb_mid0.txt") as f:
    line = f.readline()
    while line:

        # split [valid, data]
        line_list = line.split(", ")

        # trasfer valid in binary format
        valid0 = unsigned_hex2bin(line_list[0], NUM_PEGS*NUM_PES)    
        valid0_v.append(valid0)
        # print(valid,len(valid))

        # get data
        data0 = []
        line_list[1] = line_list[1].replace("\n", "")
        for i in range(len(valid0)-1, -1, -1):
            if(valid0[i] != '0'):
                num = line_list[1][4*i:4*(i+1)]
                data0.append(int(num,16))
        data0_v.append(data0)

        line = f.readline()



valid1_v = []
data1_v = []
with open(f_path + "tb_mid1.txt") as f:
    line = f.readline()
    while line:

        # split [valid, data]
        line_list = line.split(", ")

        # get valid & data
        valid1 = ""
        data1 = []
        temp = line_list[1].replace("\n", "")
        for i in range(len(temp), 0, -4):
            if(temp[i-4:i] != '0000'):
                valid1 = "1" + valid1
                num = temp[i-4:i]
                data1.append(int(num,16))
            else:
                valid1 = "0" + valid1
                data1.append(0)
        valid1_v.append(valid1)
        data1_v.append(data1)

        line = f.readline()



###########################################
# 3rd - compare 2 results to verify
###########################################
error_flag = False
for i in range(len(data0_py)):
    if(valid0_v[i] != valid0_py[i]):
        error_flag = True
        print("[mid0 - VALID ERROR]")
        print("valid0_py[%d]: " % i, valid0_py[i])
        print("valid0_v[%d]: " % i, valid0_v[i])
        break
    if(data0_v[i] != data0_py[i]):
        error_flag = True
        print("[mid0 - DATA ERROR]")
        print("data0_py[%d]: " % i, data0_py[i])
        print("data0_v[%d]: " % i, data0_v[i])
        break

if(error_flag == False):
    print("[mid0 - CORRECT]")


error_flag = False
for i in range(len(data1_py)):
    if(valid1_v[i] != valid1_py[i]):
        error_flag = True
        print("[mid1 - VALID ERROR]")
        print("valid1_py[%d]: " % i, valid1_py[i])
        print("valid1_v[%d]: " % i, valid1_v[i])
        break
    if(data1_v[i] != data1_py[i]):
        error_flag = True
        print("[mid1 - DATA ERROR]")
        print("data1_py[%d]: " % i, data1_py[i])
        print("data1_v[%d]: " % i, data1_v[i])
        break

if(error_flag == False):
    print("[mid1 - CORRECT]")