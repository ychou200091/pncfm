import os
import pandas as pd
import matplotlib.pyplot as plt
'''
Read.me
This Python script analyzes time-series network performance data from multiple CSV files.
Input:
- Folder structure: All input CSV files must reside in the same folder.
- File format: Each CSV file must follow this column structure:
    [Time, Transfer(MBytes), Bandwidth(Mbits/sec), 
    Packet_Lost, Total_Packets, Min_Latency(ms), 
    Max_Latency(ms), Avg_Latency(ms) ]
- Metadata definition: Inside the script, the file_list dictionary defines the mapping between each CSV file and its flow name and start time.

Outputs:
1. total_throughput_summary.csv
    Summarizes total data transferred (Transfer(MBytes)) for each flow and the entire network.

2. packet_loss_summary.csv
    Reports:
        -Total packets transferred and lost per flow.
        Packet loss rate per flow (Packet_Lost / Total_Packets).
        Aggregated values for the entire network.

3. Line Graphs & CSV Data Series Each graph also saves the corresponding data into a CSV file for future reference.
3.1. graph_diff_flow_bandwidth.png + graph_diff_flow_bandwidth.csv
    → Bandwidth of each flow over time.
3.2 graph_diff_flow_throughput.png + graph_diff_flow_throughput.csv
    → Throughput of each flow over time.
3.3. graph_total_bandwidth.png + graph_total_bandwidth.csv
    → Total bandwidth of the entire network over time.
3.4 graph_total_throughput.png + graph_total_throughput.csv
    → Total throughput of the entire network over time.

'''
file_root = "/home/admin123/Desktop/grad/env/codeM/log/CHFM"

file_list = {
    "1_3.csv": {"name": "Flow A", "start_time": 0},
    "2_4.csv": {"name": "Flow B", "start_time": 25},
    "9_10.csv": {"name": "Flow C", "start_time": 100},
    "5_6.csv": {"name": "Flow D", "start_time": 130}
}

def load_and_align_data():
    all_data = []
    for filename, meta in file_list.items():
        path = os.path.join(file_root, filename)
        df = pd.read_csv(path)
        df['Time'] += meta['start_time']
        df['Flow'] = meta['name']
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

def generate_total_throughput_csv(df):
    results = {}
    for flow in df['Flow'].unique():
        flow_data = df[df['Flow'] == flow]
        results[f"total throughput of {flow}"] = flow_data['Transfer(MBytes)'].sum()
    results['total throughput of network'] = sum(results.values())
    pd.DataFrame([results]).to_csv(os.path.join(file_root, 'total_throughput_summary.csv'), index=False)

def generate_packet_loss_csv(df):
    results = {}
    total_packets = 0
    total_lost = 0

    for flow in df['Flow'].unique():
        flow_data = df[df['Flow'] == flow]
        packets = flow_data['Total_Packets'].sum()
        lost = flow_data['Packet_Lost'].sum()
        loss_rate = lost / packets if packets else 0
        results[f"{flow}'s packet transfered"] = packets
        results[f"{flow}'s packet lost"] = lost
        results[f"{flow}'s packet lost rate"] = loss_rate
        total_packets += packets
        total_lost += lost

    total_loss_rate = total_lost / total_packets if total_packets else 0
    results["Network's packet transfered"] = total_packets
    results["Network's packet lost"] = total_lost
    results["Network's packet lost rate"] = total_loss_rate

    pd.DataFrame([results]).to_csv(os.path.join(file_root, 'packet_loss_summary.csv'), index=False)

def generate_line_graphs(df):
    time_bandwidth = {}
    time_throughput = {}

    bandwidth_df = pd.DataFrame()
    throughput_df = pd.DataFrame()

    plt.figure(figsize=(10, 6))
    for flow in df['Flow'].unique():
        flow_data = df[df['Flow'] == flow]
        plt.plot(flow_data['Time'], flow_data['Bandwidth(Mbits/sec)'], label=flow)
        bw = flow_data[['Time', 'Bandwidth(Mbits/sec)']].rename(columns={'Bandwidth(Mbits/sec)': f'{flow} Bandwidth'})
        if bandwidth_df.empty:
            bandwidth_df = bw
        else:
            bandwidth_df = pd.merge(bandwidth_df, bw, on='Time', how='outer')
        for _, row in flow_data.iterrows():
            time_bandwidth[row['Time']] = time_bandwidth.get(row['Time'], 0) + row['Bandwidth(Mbits/sec)']
    plt.xlabel('Time (seconds)')
    plt.ylabel('Bandwidth (Mbits/sec)')
    plt.title('Bandwidth of Different Flows')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(file_root, 'graph_diff_flow_bandwidth.png'))
    plt.close()
    bandwidth_df.sort_values(by='Time').fillna(0).to_csv(os.path.join(file_root, 'graph_diff_flow_bandwidth.csv'), index=False)

    plt.figure(figsize=(10, 6))
    for flow in df['Flow'].unique():
        flow_data = df[df['Flow'] == flow]
        plt.plot(flow_data['Time'], flow_data['Transfer(MBytes)'], label=flow)
        tp = flow_data[['Time', 'Transfer(MBytes)']].rename(columns={'Transfer(MBytes)': f'{flow} Transfer'})
        if throughput_df.empty:
            throughput_df = tp
        else:
            throughput_df = pd.merge(throughput_df, tp, on='Time', how='outer')
        for _, row in flow_data.iterrows():
            time_throughput[row['Time']] = time_throughput.get(row['Time'], 0) + row['Transfer(MBytes)']
    plt.xlabel('Time (seconds)')
    plt.ylabel('Transfered(MBytes)')
    plt.title('Throughput of Different Flows')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(file_root, 'graph_diff_flow_throughput.png'))
    plt.close()
    throughput_df.sort_values(by='Time').fillna(0).to_csv(os.path.join(file_root, 'graph_diff_flow_throughput.csv'), index=False)

    total_bandwidth = pd.DataFrame(sorted(time_bandwidth.items()), columns=['Time', 'Total Bandwidth'])
    total_throughput = pd.DataFrame(sorted(time_throughput.items()), columns=['Time', 'Total Throughput'])

    plt.figure(figsize=(10, 6))
    plt.plot(total_bandwidth['Time'], total_bandwidth['Total Bandwidth'], color='blue')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Bandwidth (Mbits/sec)')
    plt.title('Total Bandwidth Over Time')
    plt.grid(True)
    plt.savefig(os.path.join(file_root, 'graph_bandwidth_over_time.png'))
    plt.close()
    total_bandwidth.to_csv(os.path.join(file_root, 'graph_bandwidth_over_time.csv'), index=False)

    plt.figure(figsize=(10, 6))
    plt.plot(total_throughput['Time'], total_throughput['Total Throughput'], color='orange')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Transfer(MBytes)')
    plt.title('Throughput Over Time')
    plt.grid(True)
    plt.savefig(os.path.join(file_root, 'graph_throughput_over_time.png'))
    plt.close()
    total_throughput.to_csv(os.path.join(file_root, 'graph_throughput_over_time.csv'), index=False)

def main():
    df = load_and_align_data()
    generate_total_throughput_csv(df)
    generate_packet_loss_csv(df)
    generate_line_graphs(df)

if __name__ == '__main__':
    main()
