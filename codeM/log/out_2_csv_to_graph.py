import os
import pandas as pd
import matplotlib.pyplot as plt

'''
    Goal of this file:
        Input: CSV files with header
            "Time,  Transfer(MBytes),   Bandwidth(Mbits/sec),   Packet_Lost,
            Total_Packets,  Min_Latency(ms),    Max_Latency(ms),    Avg_Latency(ms)"
        Ouput: 4 graphs that graph data overtime
            1. "graph_diff_flow_bandwidth.png"
                shows how multiple flows' bandwidth change overtime.
            2. "graph_diff_flow_throughput.png"
                shows how multiple flows' throughput change overtime. It uses amount of datagram as source of input.
            3. "graph_bandwidth_over_time.png"
                shows overall bandwidth activated throughput the network
            4. "graph_throughput_over_time.png"
                shows overall datagram transfered over entire network.
        Ouput:  CSV files that graph data overtime
            packet_loss_summary.csv
'''
file_root = "/home/admin123/Desktop/grad/env/codeM/log/CHFM"
file_root = "/home/admin123/Desktop/grad/env/codeM/log/CFM"

# Input data
file_list = {
    "1_3.csv": {"name": "Flow A", "start_time": 0},
    "2_4.csv": {"name": "Flow B", "start_time": 25},
    "9_10.csv": {"name": "Flow C", "start_time": 100},
    "5_6.csv": {"name": "Flow D", "start_time": 130}
}


# Initialize containers for combined data
bandwidth_data = {}
transfer_data = {}
combined_data = pd.DataFrame() # Initialize an empty DataFrame to store the combined data


# Read and align data by start_time
for filename, meta in file_list.items():
    path = os.path.join(file_root, filename)
    df = pd.read_csv(path)
    df["Time"] = df["Time"] + meta["start_time"] # add start_time to every "Time" index
    
    for _, row in df.iterrows():
        t = row["Time"]
        bandwidth_data[t] = bandwidth_data.get(t, 0) + row["Bandwidth(Mbits/sec)"]
        transfer_data[t] = transfer_data.get(t, 0) + row["Transfer(MBytes)"]
    file_path = os.path.join(file_root, filename)
    
    # Adjust the time column based on the start time of the flow
    df['Flow'] = meta['name']
    
    # Append the data to the combined DataFrame
    combined_data = pd.concat([combined_data, df])


# graph 1:
plt.figure(figsize=(10, 6))
for flow_name in file_list.values():
    flow_data = combined_data[combined_data['Flow'] == flow_name['name']]
    plt.plot(flow_data['Time'], flow_data['Bandwidth(Mbits/sec)'], label=flow_name['name'])

# Label the axes and title
plt.xlabel('Time (seconds)')
plt.ylabel('Bandwidth (Mbits/sec)')
plt.title('Bandwidth of Different Flows')
plt.legend()
diff_flow_bandwidth_plot_path = os.path.join(file_root, "graph_diff_flow_bandwidth.png")
plt.savefig(diff_flow_bandwidth_plot_path)
plt.close()

# # === Save graph data to CSV === Sort combined data for readability
combined_data_sorted = combined_data.sort_values(by=["Flow", "Time"])
graph_data_csv_path = os.path.join(file_root, "graph_diff_flow_bandwidth.csv")
combined_data_sorted.to_csv(graph_data_csv_path, index=False)



# graph 2: throughput of different flows

plt.figure(figsize=(10, 6))
for flow_name in file_list.values():
    flow_data = combined_data[combined_data['Flow'] == flow_name['name']]
    plt.plot(flow_data['Time'], flow_data['Transfer(MBytes)'], label=flow_name['name'])

# Label the axes and title
plt.xlabel('Time (seconds)')
plt.ylabel('Transfered(MBytes)')
plt.title('Throughput of Different Flows')
plt.legend()
diff_flow_throughput_plot_path = os.path.join(file_root, "graph_diff_flow_throughput.png")
plt.savefig(diff_flow_throughput_plot_path)
plt.close()


# graph 3
# Sort by time
sorted_bandwidth = dict(sorted(bandwidth_data.items()))
sorted_transfer = dict(sorted(transfer_data.items()))

# Create plots
plt.figure(figsize=(10, 6))
plt.plot(list(sorted_bandwidth.keys()), list(sorted_bandwidth.values()), label="Total Bandwidth")
plt.xlabel("Time (s)")
plt.ylabel("Bandwidth (Mbits/sec)")
plt.title("Total Bandwidth Over Time")
plt.grid(True)
plt.legend()
bandwidth_plot_path = os.path.join(file_root, "graph_bandwidth_over_time.png")
plt.savefig(bandwidth_plot_path)
plt.close()

# graph 3
plt.figure(figsize=(10, 6))
plt.plot(list(sorted_transfer.keys()), list(sorted_transfer.values()), label="Total Throughput", color='orange')
plt.xlabel("Time (s)")
plt.ylabel("Transfer (MBytes)")
plt.title("Throughput Over Time")
plt.grid(True)
plt.legend()
transfer_plot_path = os.path.join(file_root, "graph_throughput_over_time.png")
plt.savefig(transfer_plot_path)
plt.close()



