log_root = "FPLM"
file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/" +log_root+"/"
# file_root =  "/home/admin123/Desktop/project/grad/env/codeM/log/CFM/"

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

ip_domain={'10.0.0.1':1,'10.0.0.2':1,'10.0.0.3':1,'10.0.0.4':1,
           '10.0.0.5':1,'10.0.0.6':1,'10.0.0.7':2,'10.0.0.8':2,
           '10.0.0.9':2,'10.0.0.10':2,'10.0.0.11':3, '10.0.0.12':3 }

iperf_flow_info = iperf_flow_info_quick

# Calculate simulation end time
simulation_end_time = max(
    flow["start_time"] + flow["period"]
    for flow in iperf_flow_info.values()
)+15

flow_priority = {}
flow_bw = {}
flow_profit= {}
for hosts in iperf_flow_info.keys():
    (src_ip,dst_ip) = iperf_flow_info[hosts]["src_ip"], iperf_flow_info[hosts]["dst_ip"]
    flow_priority[(src_ip,dst_ip)] = iperf_flow_info[hosts]["priority"]
    flow_bw[(src_ip,dst_ip)] =int( iperf_flow_info[hosts]["bw"][:-1])
    flow_profit[(src_ip,dst_ip)] = iperf_flow_info[hosts]["profit"]

