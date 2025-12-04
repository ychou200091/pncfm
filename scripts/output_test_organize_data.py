# Re-import everything after code execution state reset

import os
import importlib.util
import pandas as pd
import matplotlib.pyplot as plt
from algorithms import flow_info

# Paths
t_num = flow_info.running_test_num # 1: general test, 2: correlation test
CURRENT_MODE = flow_info.CURRENT_MODE
root_dir = "/home/admin123/Desktop/project/grad/env/codeM"
result_relative_path = ["", "test2"]
log_methods = {
    "CFM": os.path.join(root_dir, "log", "CFM",result_relative_path[t_num-1]),
    "MCRM": os.path.join(root_dir, "log", "MCRM",result_relative_path[t_num-1]),
    "PNCFM": os.path.join(root_dir, "log", "ProfitNBS",result_relative_path[t_num-1]),
    "Baseline": os.path.join(root_dir, "log", "Nothing",result_relative_path[t_num-1]),
}
output_dir = os.path.join(root_dir, "log", "test"+str(t_num))
os.makedirs(output_dir, exist_ok=True)

# test1 cases
stage_to_dict = {
    "stage1": flow_info.test_1_4stages_1,
    "stage2": flow_info.test_1_4stages_2,
    "stage3": flow_info.test_1_4stages_3,
    "stage4": flow_info.test_1_4stages_4,
}
# test2 cases
case_to_dict = {
    "case1": flow_info.test_2_4cases_1,
    "case2": flow_info.test_2_4cases_2,
    "case3": flow_info.test_2_4cases_3,
}
CASE = flow_info.case # string , ex: case1, case2flow_info.test_2_4cases
test_dicts = [stage_to_dict,case_to_dict]
data_dict = test_dicts[t_num-1]


# Helper to load throughput CSV
def load_throughput(method_path, case):
    path = os.path.join(method_path, case, "graph_throughput_over_time.csv")
    #print ("throughput path: ", path)
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = ["Time", "Throughput"]
        return df
    return None

# Helper to load packet loss summary CSV
def load_packet_loss(method_path, case):
    path = os.path.join(method_path, case, "packet_loss_summary.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# --- Throughput Analysis ---
def throughput_analysis():
    markers = ['x', 's', 'D', 'o', '^', 'v']  # you can add more if needed
    for idx, (case, flows) in enumerate(data_dict.items(), 1):
        plt.figure(figsize=(10, 6))
        for m_idx, (method, path) in enumerate(log_methods.items()):
            df = load_throughput(path, case)
            if df is not None:
                marker_style = markers[m_idx % len(markers)]
                plt.plot(
                    df["Time"],
                    df["Throughput"],
                    label=method,
                    linestyle='dotted',
                    linewidth=4,
                    marker=marker_style,
                    markersize=8
                )
        plt.title(f"Case {idx} - Throughput Over Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Total Throughput (Mbps)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"case{idx}_throughput_overtime.png"))
        plt.close()
        
# --- Profit Gain Analysis ---
def profit_gain_analysis():
    all_results =  pd.DataFrame()
    for idx, (case, flows) in enumerate(data_dict.items(), 1):
        print(f"idx{idx}, stage:{case}, flows:{flows}")
        rows = []
        for (src, dst) in flows.keys():
            flow_name = f"{src[1:]}_{dst[1:]}"
            profit = flows[(src, dst)]["profit"]
            row = {"Flow": flow_name, "Profit": profit}
            for method, path in log_methods.items():
                print (f"[{case}] Method:{method}, path{path}")
                df = load_packet_loss(path, case)
                #print ("=-=-=-=-=-=-=")
                #print(df)
                #print ("=-=-=-=-=-=-=")
                if df is not None:
                    col_name = f"Flow {flow_name}'s packet lost rate"
                    print(f"current column name: {col_name}") 
                    #print(f"columns names: {df.columns}")
                    if col_name in df.columns:
                        loss_rate = float(df[col_name].iloc[0])
                        obtained_profit = profit * (1.0 - loss_rate)
                        #print (f"obtained_profit: {obtained_profit}")
                        row[f"{method}_packet_loss_rate"] = loss_rate
                        row[f"{method}_profit_gain"] = obtained_profit
                        a_str = f"{method}_profit_gain"
                        print (f"[{case}]{method}_profit_gain:{ row[a_str]  } ")

                    col_name2 =  "Network's packet lost rate"
                    if col_name2 in df.columns:
                        plr = float(df[col_name2].iloc[0])
                        row[f"{method}_network_packet_loss_rate"] =plr
            rows.append(row)
        
        for row in rows:
            for method in log_methods.keys():
                # row[f"{method}_total_plr"] = (r.get(f"{method}_packet_loss_rate", 0) for r in rows)
                row[f"{method}_network_total_profit_gain"] = sum(r.get(f"{method}_profit_gain", 0) for r in rows)

        df_result = pd.DataFrame(rows)

        desired_column_order = [
            "Baseline_packet_loss_rate", "CFM_packet_loss_rate", "MCRM_packet_loss_rate", "PNCFM_packet_loss_rate",
            "Baseline_profit_gain", "CFM_profit_gain", "MCRM_profit_gain", "PNCFM_profit_gain",
            "Baseline_network_packet_loss_rate", "CFM_network_packet_loss_rate", "MCRM_network_packet_loss_rate", "PNCFM_network_packet_loss_rate",
            "Baseline_network_total_profit_gain", "CFM_network_total_profit_gain", "MCRM_network_total_profit_gain", "PNCFM_network_total_profit_gain"
        ]


        df_result = df_result[["Flow", "Profit"] + desired_column_order]

        df_result.to_csv(os.path.join(output_dir, f"case{idx}_profit_table.csv"), index=False)

        # Plotting profit gain
        plt.figure(figsize=(12, 6))
        x = range(len(rows))
        bar_width = 0.25
        for i, method in enumerate(log_methods.keys()):
            y = [r.get(f"{method}_gain", 0) for r in rows]
            plt.bar([v + i * bar_width for v in x], y, width=bar_width, label=method)
        plt.xticks([v + bar_width for v in x], [r["Flow"] for r in rows], rotation=45)
        plt.ylabel("Profit Gain")
        plt.title(f"Case {idx} - Profit Gain by Flow")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"case{idx}_profit_gain.png"))
        plt.close()

def profit_gain_analysis_with_jains():
    def jains_fairness(values):
        """Compute Jain's fairness index."""
        if not values:
            return None
        s = sum(values)
        s2 = sum([v**2 for v in values])
        n = len(values)
        if s2 == 0:
            return 0.0
        return (s ** 2) / (n * s2)

    for idx, (case, flows) in enumerate(data_dict.items(), 1):
        print(f"idx{idx}, case:{case}, flows:{flows}")
        rows = []
        for (src, dst) in flows.keys():
            flow_name = f"{src[1:]}_{dst[1:]}"
            profit = flows[(src, dst)]["profit"]
            row = {"Flow": flow_name, "Profit": profit}
            for method, path in log_methods.items():
                # print (f"[{case}] Method:{method}, path{path}")
                df = load_packet_loss(path, case)
                if df is not None:
                    col_name = f"Flow {flow_name}'s packet lost rate"
                    # print(f"current column name: {col_name}") 
                    # print(f"columns names: {df.columns}")
                    if col_name in df.columns:
                        loss_rate = float(df[col_name].iloc[0])
                        obtained_profit = profit * (1.0 - loss_rate)
                        row[f"{method}_packet_loss_rate"] = loss_rate
                        row[f"{method}_profit_gain"] = obtained_profit
                        print (f"[{case}]{method}_profit_gain:{ obtained_profit }")

                    col_name2 =  "Network's packet lost rate"
                    if col_name2 in df.columns:
                        plr = float(df[col_name2].iloc[0])
                        row[f"{method}_network_packet_loss_rate"] = plr
            rows.append(row)
        
        for row in rows:
            for method in log_methods.keys():
                row[f"{method}_network_total_profit_gain"] = sum(r.get(f"{method}_profit_gain", 0) for r in rows)

        # 🧠 Add Jain’s Index Calculation if condition matched
        print ("t_num: %s, case: %s"%(t_num, case))
        if t_num == 1 and (case == "case4" or case == "stage4"):
            jain_flows = ["1_6", "2_3","5_4",  "14_3"]
            print ("Flows: ", jain_flows)
            for method in log_methods.keys():
                # Collect loss rates
                plr_values = []
                for r in rows:
                    if r["Flow"] in jain_flows and f"{method}_packet_loss_rate" in r:
                        plr = r[f"{method}_packet_loss_rate"]
                        plr_values.append(1.0 - plr)  # Convert to success rate
                if len(plr_values) > 0:
                    jain_val = jains_fairness(plr_values)
                else:
                    jain_val = ''
                for r in rows:
                    col_name = f"{method}_network_jains"
                    r[col_name] = jain_val
        else:
            # Not target case, add empty jain columns
            for r in rows:
                for method in log_methods.keys():
                    r[f"{method}_network_jains"] = ''

        df_result = pd.DataFrame(rows)

        desired_column_order = [
            "Nothing_packet_loss_rate", "CFM_packet_loss_rate", "MCRM_packet_loss_rate", "PNCFM_packet_loss_rate",
            "Nothing_profit_gain", "CFM_profit_gain", "MCRM_profit_gain", "PNCFM_profit_gain",
            "Nothing_network_packet_loss_rate", "CFM_network_packet_loss_rate", "MCRM_network_packet_loss_rate", "PNCFM_network_packet_loss_rate",
            "Nothing_network_total_profit_gain", "CFM_network_total_profit_gain", "MCRM_network_total_profit_gain", "PNCFM_network_total_profit_gain",
            "Nothing_network_jains", "CFM_network_jains", "MCRM_network_jains", "PNCFM_network_jains"
        ]

        df_result = df_result[["Flow", "Profit"] + desired_column_order]
        df_result.to_csv(os.path.join(output_dir, f"case{idx}_profit_table.csv"), index=False)

        # Plotting profit gain
        plt.figure(figsize=(12, 6))
        x = range(len(rows))
        bar_width = 0.25
        for i, method in enumerate(log_methods.keys()):
            y = [r.get(f"{method}_gain", 0) for r in rows]
            plt.bar([v + i * bar_width for v in x], y, width=bar_width, label=method)
        plt.xticks([v + bar_width for v in x], [r["Flow"] for r in rows], rotation=45)
        plt.ylabel("Profit Gain")
        plt.title(f"Case {idx} - Profit Gain by Flow")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"case{idx}_profit_gain.png"))
        plt.close()

def combine_profit_gain_analysis():
    output_dir = os.path.join(root_dir, "log", "test"+str(t_num))
    all_dfs = []

    for i in range(1, 5):  # Case 1 to Case 4
        case_path = os.path.join(output_dir, f"case{i}_profit_table.csv")
        if os.path.exists(case_path):
            df = pd.read_csv(case_path)
            df.insert(0, "Case", f"Case {i}")  # insert "Case" column
            all_dfs.append(df)
            empty_row = pd.DataFrame([[""] * len(df.columns)], columns=df.columns)
            all_dfs.append(empty_row)
    df_all = pd.concat(all_dfs, ignore_index=True)

    # output result
    df_all.to_csv(os.path.join(output_dir, "all_results.csv"), index=False)

# region =============== part2 domain profit gain ====================

import os
import csv
import pandas as pd
from datetime import datetime
from algorithms import flow_info  # This should be available in your environment


def output_domain_profit_gain(current_mode, case_num):
    # Setup
    # root_dir = "/home/admin123/Desktop/project/grad/env/codeM"
    test_strs= ["", "test2"]
    log_file_path =""
    #log_file_path = os.path.join(root_dir, "log", "ProfitNBS", "test"+str(t_num), "case"+str(case_num), "Assist_congestion_log.txt")
    if t_num == 1:
        log_file_path = os.path.join(root_dir, "log", "ProfitNBS", "case"+str(case_num), "Assist_congestion_log.txt")
    else:
        log_file_path = os.path.join(root_dir, "log", "ProfitNBS", "test"+str(t_num), "case"+str(case_num), "Assist_congestion_log.txt")
    csv_file_path = os.path.join(root_dir, "log", "test"+str(t_num), "case"+str(case_num)+"_profit_table.csv")
    output_dir = os.path.join(root_dir, "log", f"test{flow_info.running_test_num}")
    file_name = f"case{case_num}_domain_profit_gain.csv"
    # Load profit table
    df_profit = pd.read_csv(csv_file_path, delimiter="\t" if "\t" in open(csv_file_path).readline() else ",")

    # Helper
    def get_loss_rate_column(mode):
        return ["PNCFM_packet_loss_rate", "MCRM_packet_loss_rate", "CFM_packet_loss_rate", "Nothing_packet_loss_rate"][mode]

    def get_profit_gain_column(mode):
        return ["PNCFM_profit_gain", "MCRM_profit_gain", "CFM_profit_gain", "Nothing_profit_gain"][mode]

    def ip_to_id(src_ip, dst_ip):
        if src_ip is None or dst_ip is None:
            return None
        return "{}_{}".format(src_ip.split('.')[-1], dst_ip.split('.')[-1])
    
    def get_assisted_flow_profits(domain_profit):
        # Step 1: Parse log
        with open(log_file_path) as f:
            lines = [line.strip() for line in f if line.strip()]
        congestion_lines = [line for line in lines if "[Congestion_Notify]" in line]
        latest_congestion_line = congestion_lines[-1]

        # Extract info
        import re
        match = re.search(r"flow: \((u?'10\..*?'), (u?'10\..*?')\), help_bw: ([\d\.]+), org_profit: (\d+)", latest_congestion_line)
        src_ip = match.group(1).replace("u'", "").replace("'", "")
        dst_ip = match.group(2).replace("u'", "").replace("'", "")
        assisted_src_ip,assisted_dst_ip = src_ip,dst_ip
        help_bw = float(match.group(3))
        org_profit = int(match.group(4))

        # Find flow start time
        flow_start_time = None
        flow_org_bw = None
        for line in reversed(lines[:lines.index(latest_congestion_line)]):
            if "flow:" in line and src_ip in line and dst_ip in line:
                print (f"line: {line}")
                match = re.search(r"Time: (.*?), flow", line)
                if match:
                    flow_start_time = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                    match = re.search(r"bw:\s*(\d+)", line) # find org bandwidth size
                    print(f"bw_match: {match}")
                    if match:
                        flow_org_bw = int(match.group(1))
                        print("Extracted bw:", flow_org_bw)
                    else:
                        print("bw not found.")
                    break
                
                
        congestion_time = datetime.strptime(re.search(r"Time: (.*?), flow", latest_congestion_line).group(1), "%Y-%m-%d %H:%M:%S")
        print(f"Flow: {src_ip},{dst_ip}, flow_start_time: {flow_start_time}, congestion_time {congestion_time}")
        # Step 2: Calculate assisted profit
        duration = data_dict[CASE][("h" + src_ip.split('.')[-1], "h" + dst_ip.split('.')[-1])]["period"]
        no_cong_time = (congestion_time - flow_start_time).total_seconds()
        cong_time = max(duration - no_cong_time, 0)
        portion_no_cong = no_cong_time / duration # portion of no congestion
        portion_cong = cong_time / duration       # portion of congestion
        flow_id = ip_to_id(src_ip, dst_ip)
        loss_rate_col = get_loss_rate_column(current_mode)
        packet_loss_rate = float(df_profit[df_profit["Flow"] == flow_id][loss_rate_col].values[0])
        print(f"{case_num-1} :{data_dict[CASE]}")
        print(f"")
        #print(f"weird stuff: {flow_info.test_2_4cases[flow_info.case_num - 1][("h" + src_ip.split('.')[-1], "h" + dst_ip.split('.')[-1])]["bw"].replace("m", "")}")
        share_profit = portion_cong * help_bw / flow_org_bw * org_profit
        assisted_gain = org_profit * (1 - packet_loss_rate) - share_profit
        total_gain = org_profit * (1 - packet_loss_rate)
        # print data
        print("===== Flow Profit Analysis =====")
        print("Flow ID           : {} → {}".format(src_ip, dst_ip))
        print("Flow Duration     : {:.2f} seconds".format(duration))
        print("Flow Start Time   : {}".format(flow_start_time))
        print("Congestion Time   : {}".format(congestion_time))
        print("No Congestion Time: {:.2f} seconds".format(no_cong_time))
        print("Congestion Time   : {:.2f} seconds".format(cong_time))
        print("Portion No Cong   : {:.2%}".format(portion_no_cong))
        print("Portion Congested : {:.2%}".format(portion_cong))
        print("Packet Loss Rate  : {:.4f}".format(packet_loss_rate))
        print("Original Profit   : {:.2f}".format(org_profit))
        print("Help Bandwidth    : {:.2f}".format(help_bw))
        print("Share Profit      : {:.2f}".format(share_profit))
        print("Assisted Gain     : {:.2f}".format(assisted_gain))
        print("Total Gain        : {:.2f}".format(total_gain))
        print("===============================\n")
        domain_profit = {1: 0.0, 2: 0.0, 3: 0.0}
        domain_profit[flow_info.ip_domain[src_ip]] += assisted_gain
        domain_profit[2] += share_profit  # Always domain 2 helps
        assisted_flow = (assisted_src_ip,assisted_dst_ip)
        return domain_profit, assisted_flow
    
    domain_profit = {1: 0.0, 2: 0.0, 3: 0.0}
    assisted_flow = None
    if current_mode == 0: # PNCFM
        domain_profit,assisted_flow = get_assisted_flow_profits(domain_profit)
    print(f"Domain Profit: {domain_profit}")
    # Step 3: Accumulate domain profits
    
    profit_col = get_profit_gain_column(current_mode)
    #ata_dict[CASE][flow]
    
    for flow in data_dict[CASE].keys():
        src = data_dict[CASE][flow]["src_ip"]
        dst = data_dict[CASE][flow]["dst_ip"]
        fid = ip_to_id(src, dst)
        if assisted_flow is None or fid != ip_to_id(assisted_flow[0],assisted_flow[1]):  # Already counted
            gain = float(df_profit[df_profit["Flow"] == fid][profit_col].values[0])
            print(f"flow: {src,dst}, gain:{gain}")
            domain_profit[flow_info.ip_domain[src]] += gain
    domain_profit["Total_Gain"] = sum([domain_profit[d] for d in sorted(domain_profit)])
    # Step 4: Output
    df_output = pd.DataFrame([{"Domain": d, "Profit_Gain": domain_profit[d]} for d in domain_profit])
    os.makedirs(output_dir, exist_ok=True)
    df_output.to_csv(os.path.join(output_dir, file_name), index=False)
    print(f"Mode: {flow_info.mode_text[current_mode]}")
    print(df_output)


def output_many_domain_profit_gain(modes, cases):
    for i in range(len(modes)):
        for k in range(len(cases)):
            output_domain_profit_gain(modes[i],cases[k]) # flow_info.CURRENT_MODE, flow_info.case_num

# endregion  =============== part2 domain profit gain ====================

# region =======part 3 throughput ================
import os
import pandas as pd
import sys


sys.path.append("/home/admin123/Desktop/project/grad/env/codeM")
from algorithms import flow_info

def parse_flow_name(src, dst):
    return "%s_%s" % (src[1:], dst[1:])

def make_arrow_name(src, dst):
    return "%s->%s" % (src, dst)

def load_throughput_csv(method_path, stage):
    file_path = os.path.join(method_path, stage, "graph_diff_flow_throughput.csv")
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path)

def calc_total_throughput(df, flow_col, interval_sec=2.0):
    if flow_col not in df.columns:
        return 0.0
    return df[flow_col].sum() * interval_sec  # Mbps * 秒 = Mbits

def generate_case_throughput_profit_table(t_num, case_num):
    output_dir = os.path.join("log", "test" + str(t_num))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    mode_text = ["ProfitNBS", "MCRM", "CFM", "Nothing"]
    case = "case" + str(case_num)
    stage = "stage" + str(case_num)

    if t_num == 1:
        data_dict = flow_info.test_1_4stages[case_num - 1]
    else:
        data_dict = flow_info.test_2_4cases[case_num - 1]

    all_rows = []
    for (src, dst), meta in data_dict.items():
        row = {"Flow": make_arrow_name(src, dst), "Profit": meta["profit"]}
        flow_col = "Flow " + parse_flow_name(src, dst) + " Transfer"
        for method in mode_text:
            method_path = os.path.join("log", method)
            df = load_throughput_csv(method_path, stage)
            if df is None:
                row["%s_throughput" % method] = ""
                row["%s_profit_gain" % method] = ""
                continue

            total_mbits = calc_total_throughput(df, flow_col)
            row["%s_throughput" % method] = total_mbits
            row["%s_profit_gain" % method] = total_mbits * meta["profit"]

        all_rows.append(row)

    # 計算整體網域 throughput / gain
    for method in mode_text:
        th_key = "%s_throughput" % method
        pg_key = "%s_profit_gain" % method
        net_th = sum(r.get(th_key, 0) or 0 for r in all_rows)
        net_pg = sum(r.get(pg_key, 0) or 0 for r in all_rows)
        for r in all_rows:
            r["%s_network_throughput" % method] = net_th
            r["%s_network_total_profit_gain" % method] = net_pg

    df_result = pd.DataFrame(all_rows)
    ordered_cols = ["Flow", "Profit"]
    for method in mode_text:
        ordered_cols += ["%s_throughput" % method]
    for method in mode_text:
        ordered_cols += ["%s_profit_gain" % method]
    for method in mode_text:
        ordered_cols += ["%s_network_total_profit_gain" % method]
    for method in mode_text:
        ordered_cols += ["%s_network_throughput" % method]
    df_result = df_result[ordered_cols]

    output_file = os.path.join(output_dir, "throu_case%d_profit_table.csv" % case_num)
    df_result.to_csv(output_file, index=False)
    return df_result

def generate_total_summary_csv(t_num, case_count=4):
    summary_lines = []
    for c in range(1, case_count + 1):
        case_file = os.path.join("log", "test{}".format(t_num), "throu_case{}_profit_table.csv".format(c))
        if os.path.exists(case_file):
            with open(case_file, "r") as f:
                summary_lines.extend(f.readlines())
            summary_lines.append("\n")  # add blank line between cases

    out_path = os.path.join("log", "test{}".format(t_num), "test{}_total_throuput_profit_gain.csv".format(t_num))
    with open(out_path, "w") as f:
        f.writelines(summary_lines)






# endregion ==========================


# region what to run ===


print ("throughput_analysis")
throughput_analysis()
print ("profit_gain_analysis")
profit_gain_analysis()
# profit_gain_analysis_with_jains()
combine_profit_gain_analysis()
# print ("profitoutput_many_domain_profit_gain_gain_analysis[0,1,2],[2]")
# output_many_domain_profit_gain([0,1,2,3],[2])
# -- throughput

# Main execution
# t_num = flow_info.running_test_num
iteration = len(data_dict)
for case_num in range(1, iteration+1):
    print(f"generate_case_throughput_profit_table {t_num} {case_num}")
    generate_case_throughput_profit_table(t_num, case_num)
generate_total_summary_csv(t_num)

#combine_profit_gain_analysis2()
flow_info.CURRENT_MODE, flow_info.case_num
# output_domain_profit_gain(2,1)  
