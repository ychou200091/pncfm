log_root = "FPLM"
file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"
# file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/CFM/"

iperf_flow_info_big = {
    ("h1","h3"): {  "bw": "9m", "start_time": 15, "period": 300,
                    "src_ip": "10.0.0.1", "dst_ip": "10.0.0.3"  },
    ("h2","h4"): {  "bw": "6m", "start_time": 60, "period": 300,
                    "src_ip": "10.0.0.2", "dst_ip": "10.0.0.4", },
    ("h9","h10"): { "bw": "9m", "start_time": 20, "period": 300,
                    "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10" },
    ("h5","h6"): {  "bw": "6m", "start_time": 125, "period": 300,
                    "src_ip": "10.0.0.5", "dst_ip": "10.0.0.6"  }
}

iperf_flow_info_quick = {
    ("h1","h3"): {  "bw": "9m", "start_time": 5, "period": 85, "priority":4,"profit":80,
                    "src_ip": "10.0.0.1", "dst_ip": "10.0.0.3"  },
    ("h2","h4"): {  "bw": "6m", "start_time": 25, "period": 75,"priority":3,"profit":80,
                    "src_ip": "10.0.0.2", "dst_ip": "10.0.0.4", },
    ("h9","h10"): { "bw": "9m", "start_time": 10, "period": 100,"priority":5,"profit":80,
                    "src_ip": "10.0.0.9", "dst_ip": "10.0.0.10" },
    ("h5","h6"): {  "bw": "6m", "start_time": 45, "period": 60,"priority":3, "profit":80,
                    "src_ip": "10.0.0.5", "dst_ip": "10.0.0.6"  }
}

iperf_flow_info = iperf_flow_info_quick
flow_priority = {}
flow_bw = {}
flow_profit= {}
for hosts in iperf_flow_info.keys():
    (src_ip,dst_ip) = iperf_flow_info[hosts]["src_ip"], iperf_flow_info[hosts]["dst_ip"]
    flow_priority[(src_ip,dst_ip)] = iperf_flow_info[hosts]["priority"]
    flow_bw[(src_ip,dst_ip)] =int( iperf_flow_info[hosts]["bw"][:-1])
    flow_profit[(src_ip,dst_ip)] = iperf_flow_info[hosts]["profit"]

