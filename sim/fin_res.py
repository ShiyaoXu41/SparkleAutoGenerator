import sys 
sys.path.append(".") 
from parameters import *
from dec_conv_func import *


DATA_TYPE = OUT_DATA_TYPE

##############################################
# 1st - generate correct results [fin_res_py] 
##############################################

# nums0 = [0, 1, ..., NUM_PEGS-2, NUM_PEGS-1]
nums0 = []
for i in range(NUM_PEGS):
    nums0.append(i)
# nums1 = [0, -1, ..., -(NUM_PEGS-2), -(NUM_PEGS-1)]
nums1 = []
for i in range(NUM_PEGS):
    nums1.append(-1*i)

# the whole results
fin_res_py = []
# 'NUM_PEGS' case
for i in range(NUM_PEGS):
    # each case
    for j in range(1, NUM_PEGS - i + 1):
        temp = []
        if(i > 0):
            if(i % 2 == 0):
                temp.append([0 for x in range(NUM_PEGS)])    # [0, 0, ..., 0, 0]
            else:
                temp.append([x for x in range(NUM_PEGS)])    # [0, 1, ..., NUM_PEGS-2, NUM_PEGS-1]
        for k in range(i, NUM_PEGS, j):
            if(k + j > NUM_PEGS - 1):
                # temp.append(sum(nums[k:]))
                if((NUM_PEGS - k) % 2 == 0):
                    temp.append([0 for x in range(NUM_PEGS)])
                else:
                    if(k % 2 == 0):
                        temp.append([x for x in range(NUM_PEGS)])
                    else:
                        temp.append([-1*x for x in range(NUM_PEGS)])
            else:
                # temp.append(sum(nums[k:k+j]))
                if(j % 2 == 0):
                    temp.append([0 for x in range(NUM_PEGS)])
                else:
                    if(k % 2 == 0):
                        temp.append([x for x in range(NUM_PEGS)])
                    else:
                        temp.append([-1*x for x in range(NUM_PEGS)])            
        fin_res_py.append(temp)

# print(len(fin_res_py), fin_res_py)






###########################################
# 2nd - read results from vmod [fin_res_v]
###########################################

fin_res_v = []
with open(f_path + "tb_fin.txt") as f:
    line = f.readline()
    while line:

        # split [valid, data]
        line_list = line.split(", ")

        # trasfer valid in binary format
        valid = unsigned_hex2bin(line_list[0], NUM_PEGS)    
        # print(valid,len(valid))

        # get data
        data = []
        line_list[1] = line_list[1].replace("\n", "")
        for i in range(len(valid)-1, -1, -1):
            if(valid[i] != '0'):
                temp = line_list[1][i*int(NUM_PEGS*DATA_TYPE/4) : (i+1)*int(NUM_PEGS*DATA_TYPE/4)]
                num = []
                for j in range(NUM_PEGS-1, -1, -1):
                    num.append(signed_hex2dec(temp[j*int(DATA_TYPE/4) : (j+1)*int(DATA_TYPE/4)])[2:])
                data.append(num)
        fin_res_v.append(data)

        line = f.readline()






###########################################
# 3rd - compare 2 results to verify
###########################################
error_flag = False
for i in range(len(fin_res_py)):
    if(fin_res_v[i] != fin_res_py[i]):
        error_flag = True
        print("[ERROR]")
        print("fin_res_py[%d]: " % i, fin_res_py[i])
        print("fin_res_v[%d]: " % i, fin_res_v[i])
        break

if(error_flag == False):
    print("[CORRECT]\n")


