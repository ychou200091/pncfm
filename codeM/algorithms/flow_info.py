

iperf_flow_info_big = {
    ("h1","h3"): {  "bw": "9m", "start_time": 5, "period": 300, "priority":4,"profit":80,
                    "src_ip": "10.0.0.1", "dst_ip": "10.0.0.3"  },
    ("h2","h4"): {  "bw": "6m", "start_time": 50, "period": 255,"priority":3,"profit":30,
                    "src_ip": "10.0.0.2", "dst_ip": "10.0.0.4", },
    ("h9","h10"): { "bw": "9m", "start_time": 10, "period": 295,"priority":5,"profit":50,
                    "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10" },
    ("h7","h8"): {  "bw": "6m", "start_time": 100, "period": 205,"priority":3, "profit":80,
                    "src_ip": "10.0.0.7", "dst_ip": "10.0.0.8"  },
    ("h5","h6"): {  "bw": "3m", "start_time": 160, "period": 145,"priority":3, "profit":20,
                    "src_ip": "10.0.0.5", "dst_ip": "10.0.0.6"  },
}

iperf_flow_info_quick = {
    ("h1","h3"): {  "bw": "9m", "start_time": 5, "period": 120, "priority":4,"profit":80,
                    "src_ip": "10.0.0.1", "dst_ip": "10.0.0.3"  },
    ("h2","h4"): {  "bw": "6m", "start_time": 25, "period": 100,"priority":3,"profit":30,
                    "src_ip": "10.0.0.2", "dst_ip": "10.0.0.4", },
    ("h9","h10"): { "bw": "9m", "start_time": 10, "period": 100,"priority":5,"profit":50,
                    "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10" },
    ("h7","h8"): {  "bw": "6m", "start_time": 45, "period": 80,"priority":3, "profit":80,
                    "src_ip": "10.0.0.7", "dst_ip": "10.0.0.8"  },
    ("h5","h6"): {  "bw": "3m", "start_time": 75, "period": 80,"priority":3, "profit":20,
                    "src_ip": "10.0.0.5", "dst_ip": "10.0.0.6"  },

}


# region ======================Test 1 ==========================
# only transmission no congestion
test_1_4stages_1 = {
    ("h7", "h5"):  {"bw": "5m", "start_time": 5, "period": 245, "priority": 3, "profit": 50,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.11"},
    ("h8", "h12"): {"bw": "6m", "start_time": 5, "period": 235, "priority": 2, "profit": 25,  "src_ip": "10.0.0.10", "dst_ip": "10.0.0.12"},
    ("h10", "h13"):   {"bw": "5m", "start_time": 15, "period": 210, "priority": 4, "profit": 100, "src_ip": "10.0.0.10", "dst_ip": "10.0.0.13"},
    ("h6","h11"):  {"bw": "9m", "start_time": 25, "period": 225, "priority": 2, "profit": 30,  "src_ip": "10.0.0.6", "dst_ip": "10.0.0.11"},
    ("h3", "h9"):   {"bw": "6m", "start_time": 35, "period": 200, "priority": 2, "profit": 30,  "src_ip": "10.0.0.3", "dst_ip": "10.0.0.9"},
}
# help domain not congested, can help
test_1_4stages_2 = {
    ("h4", "h2"):   {"bw": "9m", "start_time": 10,  "period": 200, "priority": 3, "profit": 50,  "src_ip": "10.0.0.4", "dst_ip": "10.0.0.2"},
    ("h3", "h1"):   {"bw": "9m", "start_time": 35,  "period": 215, "priority": 4, "profit": 100, "src_ip": "10.0.0.3", "dst_ip": "10.0.0.1"},
    ("h7", "h8"):   {"bw": "7m", "start_time": 50,  "period": 200,  "priority": 2, "profit": 30,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.8"},
    ("h10", "h12"): {"bw": "3m", "start_time": 20,  "period": 150, "priority": 2, "profit": 60,  "src_ip": "10.0.0.10", "dst_ip": "10.0.0.12"},

}
#  help domain congested, cannot help
test_1_4stages_3 = {
    ("h7", "h8"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 3, "profit": 30,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.8"},
    ("h10", "h9"):  {"bw": "9m", "start_time": 10, "period": 235, "priority": 2, "profit": 20,  "src_ip": "10.0.0.10", "dst_ip": "10.0.0.9"},
    ("h5", "h6"):   {"bw": "8m", "start_time": 20, "period": 230, "priority": 3, "profit": 120,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.6"},
    ("h2", "h3"):   {"bw": "9m", "start_time": 70, "period": 180, "priority": 2, "profit": 60,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h4", "h12"):  {"bw": "3m", "start_time": 100, "period": 150, "priority": 2, "profit": 30,  "src_ip": "10.0.0.4", "dst_ip": "10.0.0.12"},
}
# help domain can help, congestion happened in help domain, then happen in org domain
# test_1_4stages_4 = {
#     ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 70, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
#     ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 120,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
#     ("h2", "h3"):   {"bw": "6m", "start_time": 25, "period": 220, "priority": 3, "profit": 50,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
#     ("h7", "h13"):  {"bw": "6m", "start_time":80, "period": 160, "priority": 3, "profit": 55,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
#     ("h5", "h4"):   {"bw": "3m", "start_time": 110, "period": 130, "priority": 2, "profit":10,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
#     ("h14", "h3"):   {"bw": "5m", "start_time": 130, "period": 115, "priority": 2, "profit":90,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.15"},
# }
test_1_4stages_4 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 4, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 3,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "6m", "start_time": 15, "period": 220, "priority": 3, "profit": 2,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time":20, "period": 230, "priority": 3, "profit": 6,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 30, "period": 215, "priority": 2, "profit":2,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 2, "profit":10,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}
for flow in test_1_4stages_4.keys():
    test_1_4stages_4[flow]["profit"] = test_1_4stages_4[flow]["profit"] * float(test_1_4stages_4[flow]["bw"][:-1])

test_1_4stages_5 = {
    ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 4, "profit": 100, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 90,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 3, "profit": 25,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):   {"bw": "8m", "start_time": 85, "period": 150, "priority": 3, "profit": 55,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
}



# test_1_4stages_4 = {
#     ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 100, "priority": 4, "profit": 120, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
#     ("h9", "h10"):  {"bw": "9m", "start_time": 7, "period": 100, "priority": 4, "profit": 30,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
#     ("h2", "h3"):   {"bw": "8m", "start_time": 15, "period": 85, "priority": 3, "profit": 30,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
#     ("h7", "h13"):   {"bw": "8m", "start_time": 35, "period": 65, "priority": 3, "profit": 30,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
#     ("h5", "h4"):   {"bw": "4m", "start_time": 60, "period": 40, "priority": 2, "profit":70,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
#     # ("h14", "h15"):   {"bw": "2m", "start_time": 170, "period": 80, "priority": 2, "profit":20,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.15"},
# }
# for f in test_1_4stages_4.keys():
#     if test_1_4stages_4[f]["start_time"] > 40:
#         test_1_4stages_4[f]["start_time"] = int (test_1_4stages_4[f]["start_time"]  / 2)
        

# endregion === test 1====

# region ======================Test 2 ==========================
# case 1 positive correlation

test_2_4cases_1 = {
    ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 4, "profit": 100, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 100,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "7m", "start_time": 40, "period": 210, "priority": 3, "profit": 70,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):   {"bw": "8m", "start_time": 85, "period": 150, "priority": 3, "profit": 80,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 150, "period": 100, "priority": 2, "profit": 30,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
}

# case 2 negative correlation
test_2_4cases_2 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 30, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 20,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "9m", "start_time": 40, "period": 210, "priority": 3, "profit": 20,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):   {"bw": "7m", "start_time": 85, "period": 150, "priority": 3, "profit": 50,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 150, "period": 100, "priority": 2, "profit": 100,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
}

# case 3 mix correlation
test_2_4cases_3 = {
    ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 4, "profit": 100, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 90,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "8m", "start_time": 40, "period": 210, "priority": 3, "profit": 30,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):   {"bw": "7m", "start_time": 85, "period": 150, "priority": 3, "profit": 60,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "4m", "start_time": 150, "period": 100, "priority": 2, "profit": 70,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
}

# case 4 same profit 
# test_2_4cases_4 = {
#     ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 4, "profit": 51, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
#     ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 50,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
#     ("h2", "h3"):   {"bw": "7m", "start_time": 40, "period": 210, "priority": 3, "profit": 50,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
#     ("h7", "h13"):   {"bw": "6m", "start_time": 85, "period": 150, "priority": 3, "profit": 50,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
#     ("h5", "h4"):   {"bw": "3m", "start_time": 150, "period": 100, "priority": 2, "profit": 50,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
# }
test_2_4cases_4 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 51, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 20, "period": 230, "priority": 4, "profit": 50,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "6m", "start_time": 25, "period": 210, "priority": 3, "profit": 50,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time":45, "period": 150, "priority": 3, "profit": 50,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 150, "period": 100, "priority": 2, "profit":50,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 170, "period": 65, "priority": 2, "profit":50,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.15"},
}
# endregion  Test2
#================== Test 2 END ======================
# region ========--------- test 2 second try ---------===========

# case 1 positive correlation

test_2_4cases_1 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 9, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 10,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "6m", "start_time": 15, "period": 220, "priority": 3, "profit": 6,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time":25, "period": 230, "priority": 3, "profit": 6.5,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 30, "period": 215, "priority": 2, "profit":2,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 2, "profit":5.5,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}

for flow in test_2_4cases_1.keys():
    test_2_4cases_1[flow]["profit"] = test_2_4cases_1[flow]["profit"] * float(test_2_4cases_1[flow]["bw"][:-1])

# case 2 negative correlation

test_2_4cases_2 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 3, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 1,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "9m", "start_time": 15, "period": 220, "priority": 3, "profit": 1,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time":25, "period": 230, "priority": 3, "profit": 4,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "5m", "start_time": 30, "period": 215, "priority": 2, "profit":5,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "2m", "start_time": 40, "period": 210, "priority": 2, "profit": 12,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}

for flow in test_2_4cases_2.keys():
    test_2_4cases_2[flow]["profit"] = test_2_4cases_2[flow]["profit"] * float(test_2_4cases_2[flow]["bw"][:-1])

# case 3 mix correlation
test_2_4cases_3 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 5, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 3,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "7m", "start_time": 15, "period": 220, "priority": 3, "profit": 3,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time": 25, "period": 225, "priority": 3, "profit": 8,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 30, "period": 215, "priority": 2, "profit":2,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 2, "profit":10,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}

for flow in test_2_4cases_3.keys():
    test_2_4cases_3[flow]["profit"] = test_2_4cases_3[flow]["profit"] * float(test_2_4cases_3[flow]["bw"][:-1])

# endregion
# log_root = "ProfitNBS"# ProfitNBS  # MRCM # CFM
# file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"+"stage1/"

CURRENT_MODE = 3 # 0:PNCFM, 1:MCRM, 2: CFM, 3:Nothing
running_test_num = 2 # 1:general #2:profit correlation 
case_num = 3 # start at 1
stage = "stage"+str(case_num)
case  = "case"+str(case_num)

mode_text = ["PNCFM", "MCRM" ,"CFM","Nothing"]
test_1_4stages = [test_1_4stages_1,test_1_4stages_2,test_1_4stages_3,test_1_4stages_4,test_1_4stages_5]
test_2_4cases  = [test_2_4cases_1,test_2_4cases_2,test_2_4cases_3,test_2_4cases_4]
if running_test_num == 1:
    if CURRENT_MODE == 0:
        log_root = "ProfitNBS/"+stage      # ProfitNBS  # MRCM # CFM
    elif CURRENT_MODE == 1:
        log_root = "MCRM/"+stage           # ProfitNBS  # MRCM # CFM
    elif CURRENT_MODE == 2:
        log_root = "CFM/"+stage 
    elif CURRENT_MODE == 3: # Nothing
        log_root = "Nothing/"+stage 
    iperf_flow_info = test_1_4stages[case_num-1]

    file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"
    # log_root = "MCRM/stage1"
    # file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"
    # file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/CFM/"
    real_bw_log_file_path = "/home/admin123/Desktop/project/grad/env/codeM/log/real_bw_log_"+stage+".csv"
    CSV_FILE = 'log/real_bw_log_'+stage+'.csv'
elif running_test_num == 2:
    if CURRENT_MODE == 0:
        log_root = "ProfitNBS/test2/"+case      # ProfitNBS  # MRCM # CFM
    elif CURRENT_MODE == 1:
        log_root = "MCRM/test2/"+case           # ProfitNBS  # MRCM # CFM
    elif CURRENT_MODE == 2:
        log_root = "CFM/test2/"+case 
    elif CURRENT_MODE == 3: # Nothing
        log_root = "Nothing/test2/"+case 
    
    iperf_flow_info = test_2_4cases[case_num-1]
    file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"
    real_bw_log_file_path = "/home/admin123/Desktop/project/grad/env/codeM/log/real_bw_log_t2_"+case+".csv"
    CSV_FILE = 'log/real_bw_log_t2_'+case+'.csv'


# iperf_flow_info = iperf_flow_info_quick

ip_domain={'10.0.0.1':1,'10.0.0.2':1,'10.0.0.3':1,'10.0.0.4':1,
            '10.0.0.5':1,'10.0.0.6':1,'10.0.0.7':2,'10.0.0.8':2,'10.0.0.13':2 ,
            '10.0.0.9':2,'10.0.0.10':2,'10.0.0.11':3, '10.0.0.12':3,
            '10.0.0.14':1,'10.0.0.15':1, }

# Calculate simulation end time
simulation_end_time = max(
    flow["start_time"] + flow["period"]
    for flow in iperf_flow_info.values()
)+15

flow_priority = {}
flow_bw = {}
flow_profit= {}
flow_times = {}
for hosts in iperf_flow_info.keys():
    (src_ip,dst_ip) = iperf_flow_info[hosts]["src_ip"], iperf_flow_info[hosts]["dst_ip"]
    flow_priority[(src_ip,dst_ip)] = iperf_flow_info[hosts]["priority"]
    flow_bw[(src_ip,dst_ip)] =int( iperf_flow_info[hosts]["bw"][:-1])
    flow_profit[(src_ip,dst_ip)] = iperf_flow_info[hosts]["profit"]

    flow_times[(src_ip,dst_ip)] = {
        "idle_duration" : None,
        "congestion_timestamp" : None
    }
flow_ips = [(iperf_flow_info[hosts]["src_ip"], iperf_flow_info[hosts]["dst_ip"]) for hosts in iperf_flow_info.keys()]