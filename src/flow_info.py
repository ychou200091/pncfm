


"""
flow_info.py - Network Simulation Configuration Module

OVERVIEW
--------
This module defines simulation parameters and test cases for SDN (Software-Defined Networking)
experiments involving Ryu controllers and Mininet network topology. It serves as the central
configuration source accessed by both the Ryu controller and Mininet during runtime.

PURPOSE
-------
Configure and manage network flow test cases to evaluate different load-balancing algorithms
across multi-domain network topologies. Each test case specifies traffic flows with parameters
including bandwidth requirements, priorities, profit metrics, and timing constraints.

CONFIGURATION PARAMETERS
------------------------
CURRENT_MODE : int
    Selects the load-balancing algorithm to execute:
    - 0: PNCFM (Profit negotiation collaborative flow management)
    - 1: MCRM (Multi-Controller Resource Management)
    - 2: CFM (Centralized Flow Management)
    - 3: Baseline (Standard routing without optimization)

running_test_num : int
    Specifies which test suite to run:
    - 1: General performance test (test_1_4stages)
    - 2: Profit correlation analysis (test_2_4cases)

case_num : int
    Selects the specific case within the chosen test suite (1-indexed).
    Valid range depends on the test suite:
    - Test 1: cases 1-4
    - Test 2: cases 1-3

TEST CASE STRUCTURE
-------------------
Each test case is a dictionary mapping host pairs to flow specifications:
{
    ("source_host", "destination_host"): {
        "bw": str,          # Bandwidth requirement (e.g., "9m" for 9 Mbps)
        "start_time": int,  # Flow start time in seconds
        "period": int,      # Flow duration in seconds
        "priority": int,    # QoS priority level (higher = more important)
        "profit": float,    # Calculated as profit_per_mbps * bandwidth
        "src_ip": str,      # Source IP address
        "dst_ip": str       # Destination IP address
    },
    ...
}

TEST SUITES
-----------
These test cases describe the scenarios PNCFM is designed to address:
Test 1 (test_1_4stages): Four scenarios examining domain congestion behavior
    - Stage 1: Helper domain not congested, can offload traffic
    - Stage 2: Helper domain congested, cannot accept additional flows
    - Stage 3: Helper domain accepts traffic, then becomes congested
    - Stage 4: Congestion propagates from helper to origin domain

Test 2 (test_2_4cases): Three scenarios examining profit-bandwidth correlation
    - Case 1: Positive correlation (higher bandwidth = higher profit)
    - Case 2: Negative correlation (lower bandwidth = higher profit)
    - Case 3: Mixed correlation (no clear pattern)

OUTPUT AND LOGGING
------------------
- Log files are stored in domain-specific directories under the configured algorithm
- Real-time bandwidth logs are written to CSV files for analysis
- The module automatically calculates simulation end time based on flow schedules

USAGE
-----
1. Set CURRENT_MODE to select the load-balancing algorithm
2. Set running_test_num to choose the test suite
3. Set case_num to select the specific test case
4. Verify absolute directory paths match your system configuration
5. Run the Ryu controller and Mininet topology script

DEPENDENCIES
------------
- Ryu SDN controller framework
- Mininet network emulator
- Python 2.7+ (uses legacy dict.iteritems() in CSV export)

NOTES
-----
- All profit values are automatically scaled by bandwidth during initialization
- IP-to-domain mappings are defined in the ip_domain dictionary
- Simulation end time is dynamically calculated from flow schedules
- This module uses absolute paths; update file_root paths before deployment

AUTHOR
------
Taylor Chou
Last Modified: 2025
"""

# region ====================== Configuration Module for Network Simulation ======================
CURRENT_MODE = 0 # 0:PNCFM, 1:MCRM, 2: CFM, 3:Baseline
running_test_num = 1 # 1:general # 2:profit correlation 
case_num = 2 # start at 1
stage = "stage"+str(case_num)
case  = "case"+str(case_num)

# endregion

# region ======================Test 1 ==========================

# help domain not congested, can help
test_1_4stages_1 = {
    ("h4", "h2"):   {"bw": "9m", "start_time": 10,  "period": 200, "priority": 3, "profit": 7,  "src_ip": "10.0.0.4", "dst_ip": "10.0.0.2"},
    ("h3", "h1"):   {"bw": "9m", "start_time": 35,  "period": 215, "priority": 4, "profit": 2, "src_ip": "10.0.0.3", "dst_ip": "10.0.0.1"},
    ("h7", "h8"):   {"bw": "7m", "start_time": 50,  "period": 200,  "priority": 2, "profit": 3,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.8"},
    ("h10", "h12"): {"bw": "3m", "start_time": 20,  "period": 150, "priority": 2, "profit": 10,  "src_ip": "10.0.0.10", "dst_ip": "10.0.0.12"},
}
for flow in test_1_4stages_1.keys():
    test_1_4stages_1[flow]["profit"] = test_1_4stages_1[flow]["profit"] * float(test_1_4stages_1[flow]["bw"][:-1])

#  help domain congested, cannot help 
test_1_4stages_2= {
    ("h7", "h8"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 3, "profit": 5,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.8"},
    ("h10", "h9"):  {"bw": "9m", "start_time": 10, "period": 235, "priority": 2, "profit": 2,  "src_ip": "10.0.0.10", "dst_ip": "10.0.0.9"},
    ("h5", "h6"):   {"bw": "6m", "start_time": 20, "period": 230, "priority": 3, "profit": 4,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.6"},
    ("h2", "h3"):   {"bw": "7m", "start_time": 40, "period": 200, "priority": 2, "profit": 2,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h4", "h12"):  {"bw": "3m", "start_time": 70, "period": 175, "priority": 2, "profit": 3,  "src_ip": "10.0.0.4", "dst_ip": "10.0.0.12"},
    ("h14", "h3"):   {"bw": "3m", "start_time": 50, "period": 210, "priority": 2, "profit":10,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}
for flow in test_1_4stages_2.keys():
    test_1_4stages_2[flow]["profit"] = test_1_4stages_2[flow]["profit"] * float(test_1_4stages_2[flow]["bw"][:-1])

# help domain can help, congestion happened in help domain
test_1_4stages_3 = {
    ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 230, "priority": 4, "profit": 8, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 15, "period": 230, "priority": 4, "profit": 5,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "5m", "start_time": 25, "period": 220, "priority": 3, "profit": 2,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):   {"bw": "7m", "start_time": 50, "period": 180, "priority": 3, "profit": 5,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
} 
for flow in test_1_4stages_3.keys():
    test_1_4stages_3[flow]["profit"] = test_1_4stages_3[flow]["profit"] * float(test_1_4stages_3[flow]["bw"][:-1])

# help domain can help, congestion happened in help domain, then happen in org domain
test_1_4stages_4 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 7, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 3,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "6m", "start_time": 15, "period": 220, "priority": 3, "profit": 2,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "7m", "start_time":25, "period": 230, "priority": 3, "profit": 7,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 35, "period": 215, "priority": 2, "profit":2,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 2, "profit":10,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}
for flow in test_1_4stages_4.keys():
    test_1_4stages_4[flow]["profit"] = test_1_4stages_4[flow]["profit"] * float(test_1_4stages_4[flow]["bw"][:-1])

# endregion === test 1====


# region ========--------- test 2 second try ---------===========

# case 1 positive correlation
test_2_4cases_1 = {
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 9, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 10,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "5m", "start_time": 15, "period": 220, "priority": 3, "profit": 6,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time":25, "period": 225, "priority": 3, "profit": 7,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "3m", "start_time": 30, "period": 215, "priority": 2, "profit":2,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 2, "profit":5,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}
test_2_4cases_1 = { # 2-3 6m 5m p6
    ("h1", "h6"):   {"bw": "8m", "start_time": 5, "period": 230, "priority": 4, "profit": 11, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "8m", "start_time": 10, "period": 230, "priority": 4, "profit": 11,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "7m", "start_time": 15, "period": 220, "priority": 3, "profit": 8,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time":25, "period": 225, "priority": 3, "profit": 8,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "4m", "start_time": 30, "period": 215, "priority": 2, "profit":5,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "3m", "start_time": 40, "period": 210, "priority": 2, "profit":3,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}
for flow in test_2_4cases_1.keys():
    test_2_4cases_1[flow]["profit"] = test_2_4cases_1[flow]["profit"] * float(test_2_4cases_1[flow]["bw"][:-1])

# case 2 negative correlation

test_2_4cases_2 = {
    ("h1", "h6"):   {"bw": "6m", "start_time": 5, "period": 230, "priority": 4, "profit": 4, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "9m", "start_time": 10, "period": 230, "priority": 4, "profit": 1,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "7m", "start_time": 15, "period": 220, "priority": 3, "profit": 3,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "8m", "start_time":25, "period": 230, "priority": 3, "profit": 2,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "5m", "start_time": 30, "period": 215, "priority": 2, "profit":6,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "3m", "start_time": 40, "period": 210, "priority": 2, "profit": 13,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}

for flow in test_2_4cases_2.keys():
    test_2_4cases_2[flow]["profit"] = test_2_4cases_2[flow]["profit"] * float(test_2_4cases_2[flow]["bw"][:-1])

# case 3 mix correlation
test_2_4cases_3 = {
    ("h1", "h6"):   {"bw": "9m", "start_time": 5, "period": 240, "priority": 4, "profit": 12, "src_ip": "10.0.0.1", "dst_ip": "10.0.0.6"},
    ("h9", "h10"):  {"bw": "8m", "start_time": 10, "period": 235, "priority": 4, "profit": 3,  "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10"},
    ("h2", "h3"):   {"bw": "7m", "start_time": 15, "period": 220, "priority": 3, "profit": 4,  "src_ip": "10.0.0.2", "dst_ip": "10.0.0.3"},
    ("h7", "h13"):  {"bw": "6m", "start_time": 25, "period": 225, "priority": 3, "profit": 9,  "src_ip": "10.0.0.7", "dst_ip": "10.0.0.13"},
    ("h5", "h4"):   {"bw": "4m", "start_time": 30, "period": 215, "priority": 2, "profit":2,  "src_ip": "10.0.0.5", "dst_ip": "10.0.0.4"},
    ("h14", "h3"):   {"bw": "5m", "start_time": 40, "period": 210, "priority": 2, "profit":12,  "src_ip": "10.0.0.14", "dst_ip": "10.0.0.3"},
}

for flow in test_2_4cases_3.keys():
    test_2_4cases_3[flow]["profit"] = test_2_4cases_3[flow]["profit"] * float(test_2_4cases_3[flow]["bw"][:-1])

# endregion

mode_text = ["PNCFM", "MCRM" ,"CFM","Baseline"]
test_1_4stages = [test_1_4stages_1,test_1_4stages_2,test_1_4stages_3,test_1_4stages_4]
test_2_4cases  = [test_2_4cases_1,test_2_4cases_2,test_2_4cases_3]
if running_test_num == 1:
    if CURRENT_MODE == 0:
        log_root = "ProfitNBS/"+stage      # ProfitNBS  # MRCM # CFM
    elif CURRENT_MODE == 1:
        log_root = "MCRM/"+stage           # ProfitNBS  # MRCM # CFM
    elif CURRENT_MODE == 2:
        log_root = "CFM/"+stage 
    elif CURRENT_MODE == 3: # Baseline
        log_root = "Baseline/"+stage 
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
    elif CURRENT_MODE == 3: # Baseline
        log_root = "Baseline/test2/"+case 
    
    iperf_flow_info = test_2_4cases[case_num-1]
    file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"
    real_bw_log_file_path = "/home/admin123/Desktop/project/grad/env/codeM/log/real_bw_log_t2_"+case+".csv"
    CSV_FILE = 'log/real_bw_log_t2_'+case+'.csv'

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

import csv

def extract_case_name(prefix, index):
    return "%s%d" % (prefix, index + 1)

def parse_test_case(test_dict, case_name):
    rows = []
    for flow, data in test_dict.iteritems():
        src, dst = flow
        flow_name = "%s_%s" % (src, dst)
        bw_mbps = float(data["bw"][:-1])  # remove 'm' and convert to float
        start_time = data["start_time"]
        period = data["period"]
        end_time = start_time + period
        profit_per_mbps = round(data["profit"] / bw_mbps, 4)
        total_profit = round(data["profit"], 4)

        row = [case_name, flow_name, bw_mbps, profit_per_mbps, total_profit,
               start_time, end_time, period, ""]
        rows.append(row)

    # sort by starting time
    rows.sort(key=lambda x: x[5])
    return rows

def write_all_tests_to_csv(file_path):
    headers = ["case", "flow", "bandwidth (Mbps)", "profit per mbps", "total profit",
               "start time", "end time", "duration", "cross-domain"]

    with open(file_path, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        # Process Test 1
        for idx, test in enumerate(test_1_4stages):
            case_name = extract_case_name("case", idx)
            rows = parse_test_case(test, case_name)
            for row in rows:
                writer.writerow(row)
            writer.writerow([])  # empty row for separation

        # Process Test 2
        for idx, test in enumerate(test_2_4cases):
            case_name = extract_case_name("case", idx )  
            rows = parse_test_case(test, case_name)
            for row in rows:
                writer.writerow(row)
            writer.writerow([])

if __name__ == "__main__":
    write_all_tests_to_csv("outputs/output_flow_info.csv")
    print("CSV file generated: output_flow_info.csv")
