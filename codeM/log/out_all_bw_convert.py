import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
'''
    Part 1:
    Goal of this file:
        Input: Iperf server records. e.g. 1_3.out
        Ouput: A csv file with these headers
            "Time,  Transfer(MBytes),   Bandwidth(Mbits/sec),   Packet_Lost,
            Total_Packets,  Min_Latency(ms),    Max_Latency(ms),    Avg_Latency(ms)"
    Part 2:

'''
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
file_root =  "/home/admin123/Desktop/grad/env/codeM/log/CHFM/"
# file_root =  "/home/admin123/Desktop/grad/env/codeM/log/CFM_org/"

# List of input files to process
input_files = [
    "1_3.out",
    "2_4.out",
    "5_6.out",
    "9_10.out",
]
file_list = {
    "1_3.csv": {"name": "Flow 1_3", "start_time": 0},
    "2_4.csv": {"name": "Flow 2_4", "start_time": 25},
    "9_10.csv": {"name": "Flow 9_10", "start_time": 100},
    "5_6.csv": {"name": "Flow 5_6", "start_time": 130}
} 

def convert_to_mbytes(value, unit):
    """Convert KBytes or MBytes to MBytes"""
    value = float(value)
    if unit == "KBytes":
        return value / 1024
    elif unit == "MBytes":
        return value
    elif  unit == "Bytes":
        if value == 0.0:
            return 0.0
        else:
            return value / 1048576 # 1024*1024
    else:
        print(f"Warning: Unknown transfer unit: {unit}")
        return value

def convert_to_mbits_per_sec(value, unit):
    """Convert Kbits/sec or Mbits/sec to Mbits/sec"""
    value = float(value)
    if unit == "Kbits/sec":
        return value / 1000
    elif unit == "Mbits/sec":
        return value
    elif unit == "bits/sec":
        return value if value ==0.0 else value/1000000 # value /(10^6)  
    else:
        print(f"Warning: Unknown bandwidth unit: {unit}")
        return value

def process_file(input_file, output_file):
    """Process a single iperf output file and convert it to CSV"""
    print(f"Processing {input_file} -> {output_file}")
    
    # Dictionary to store aggregated data by timestamp
    aggregated_data = {}
    
    # Read the file
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    count = 0
    # Process each line
    for line in lines:
        line = line.strip()
        # Skip header lines and other non-data lines
        if (line.startswith("----") or 
            "Server listening" in line or 
            "Receiving" in line or 
            "UDP buffer size" in line or 
            "local" in line or 
            "ID" in line):
            continue
        
        # Skip lines with "datagrams received out-of-order"
        if "datagrams received out-of-order" in line:
            continue
        
        # Only process lines that start with "[ ID]"
        if not line.startswith("["):
            print (line)
            continue
        
        # Split the line by spaces
        parts = line.split()
        # Check if this is a valid data line
        # full string breakdown:  [|3]|30.0000-35.0000|sec|2.60|MBytes|4.36|Mbits/sec|0.881|ms|2212/|4067|(54%)|377.461/290.980/658.129/63.038|ms|371|pps|1.44|
        # 0-4:   [|3]|30.0000-35.0000|sec|2.60|
        # 5-9:   MBytes|4.36|Mbits/sec|0.881|ms|
        # 10-14: 2212/|4067|(54%)|377.461/290.980/658.129/63.038|ms|
        # 15-17: 371|pps|1.44|

        if len(parts) < 15:  # Valid data lines have at least 15 parts
            continue
        
        try:
            # Parse the interval
            if not '-' in parts[2]:
                continue
            count +=1
            interval = parts[2].split("-") # 30.0000-35.0000  -> [0]: 30.0000, [1]:35.0000
            # Get the start time
            start_time = interval[0] 
            end_time = interval[1]
            
            # Determine if this is an overall summary line
            is_overall = False
            if start_time == "0.0000" and "sec" in parts[3] and float(end_time) > 10:
                is_overall = True
                #start_time = "Overall"
                continue # skip it
            # print(parts)
            
            idx = parts.index("sec") + 1
            # Find transfered data
            transfer_value = parts[idx]
            transfer_unit = parts[idx + 1]
            
            # Find bandwidth data
            idx = idx + 2
            bandwidth_value = parts[idx]
            bandwidth_unit = parts[idx + 1]
            
            idx = parts.index("ms") + 1
            # Find packets lost and total packets
            packet_lostNtotal = parts[idx].split("/") # usually at idx 10
            packets_lost = packet_lostNtotal[0]
            if packet_lostNtotal[1] and packet_lostNtotal != "":
                total_packets = packet_lostNtotal[1]
                idx+=2
            else:
                idx +=1
                total_packets = parts[idx]
                idx += 2
            # for i, part in enumerate(parts):
            #     if "/" in part and "(" in parts[i+1]:
            #         packets_info = part.split("/")
            #         packets_lost = packets_info[0]
            #         total_packets = packets_info[1]
            #         break
            
            # Find latency information
            latency_info = parts[idx].split("/") # usually idx 13
            idx += 1 # usually 14
            avg_latency,min_latency,max_latency =0,0,0
            avg_latency = latency_info[0]
            if len(latency_info)<3:
                #print("parts:",parts)
                #print("latency_info:",latency_info)
                latency_info = parts[idx].split("/")
                idx += 1
                #print("more latency_info:",latency_info)
                min_latency = latency_info[0]
                #max_latency = latency_info[1]
                if len(latency_info)<2:
                    latency_info = parts[idx].split("/")
                    idx += 1
                    max_latency = latency_info[0]
            else:
                min_latency = latency_info[1]
                max_latency = latency_info[2]
            
            # Convert transfer to MBytes and bandwidth to Mbits/sec
            transfer_mbytes = convert_to_mbytes(transfer_value, transfer_unit)
            bandwidth_mbits = convert_to_mbits_per_sec(bandwidth_value, bandwidth_unit)
            
            # Create or update entry in aggregated_data
            if start_time not in aggregated_data:
                
                aggregated_data[start_time] = {
                    "transfer": transfer_mbytes,
                    "bandwidth": bandwidth_mbits,
                    "packets_lost": int(packets_lost),
                    "total_packets": int(total_packets),
                    "min_latency": 0 if min_latency == "-" else float(min_latency),
                    "max_latency": 0 if max_latency == "-" else float(max_latency),
                    "avg_latency": [0 if avg_latency == "-" else float(avg_latency),0 if avg_latency == "-" else float(avg_latency)] # 0 is avg, 1,2,3,4... are records 
                }
            else:
                # Add values for the same timestamp
                aggregated_data[start_time]["transfer"] += transfer_mbytes
                aggregated_data[start_time]["bandwidth"] += bandwidth_mbits
                aggregated_data[start_time]["packets_lost"] += int(packets_lost)
                aggregated_data[start_time]["total_packets"] += int(total_packets)
                #print (f"transfer: {transfer_mbytes}, bandwidth:{bandwidth_mbits}, packets_lost: {int(packets_lost)}, total_packets: {int(total_packets)}")
                # Keep only the minimum min_latency
                if min_latency == '-': # inside inpu5 file (e.g 1_3.out): -/-/-/- ms
                    continue # no need to process
                print("min_latency: ",min_latency)
                if float(min_latency) < aggregated_data[start_time]["min_latency"]:
                    aggregated_data[start_time]["min_latency"] = float(min_latency)
                
                # Keep only the maximum max_latency
                if float(max_latency) > aggregated_data[start_time]["max_latency"]:
                    aggregated_data[start_time]["max_latency"] = float(max_latency)
                
                # calculate avg_latency
                aggregated_data[start_time]["avg_latency"].append(float(avg_latency))
                lat_len = len(aggregated_data[start_time]["avg_latency"])
                total_lat = 0
                if(lat_len>=2):
                    for i in range(lat_len):
                        if i == 0:
                            continue
                        total_lat = aggregated_data[start_time]["avg_latency"][i] + total_lat
                    aggregated_data[start_time]["avg_latency"][0]  = round( total_lat / (lat_len-1) , 3)
                #print("aggregated_data[avg_latency]: ",aggregated_data[start_time]["avg_latency"])
                
        except (ValueError, IndexError) as e:
            # Skip lines that can't be parsed properly
            raise(e)
            continue

    #print("count: " , count)
    
    # Sort timestamps, ensuring "Overall" is at the end
    sorted_timestamps = sorted([ int(float(t)) for t in aggregated_data.keys() if t != "Overall"])
    if "Overall" in aggregated_data:
        sorted_timestamps.append("Overall")
    
    # Write data to CSV file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Transfer(MBytes)", "Bandwidth(Mbits/sec)", "Packet_Lost", "Total_Packets", "Min_Latency(ms)", "Max_Latency(ms)", "Avg_Latency(ms)"])
        
        for time in sorted_timestamps:
            timestamp = str(time)+".0000"
            data = aggregated_data[timestamp]
            writer.writerow([
                timestamp,
                f"{data['transfer']:.4f}",
                f"{data['bandwidth']:.4f}",
                data['packets_lost'],
                data['total_packets'],
                f"{data['min_latency']:.4f}",
                f"{data['max_latency']:.4f}",
                f"{data['avg_latency'][0]:.4f}"
            ])
    #print(aggregated_data)
    return len(aggregated_data)
# main function of part 1
def organize_data_into_csv():
    # Process each file
    for input_file in input_files:
        input_file= file_root+input_file
        output_file = input_file.replace(".out", ".csv")
        rows_processed = process_file(input_file, output_file)
        print(f"Processed {rows_processed} unique timestamps from {input_file}")
# end of part 1
# start of part 2

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

# end of part 2
def main():
    # part 1
    organize_data_into_csv()
    # part 2
    df = load_and_align_data()
    generate_total_throughput_csv(df)
    generate_packet_loss_csv(df)
    generate_line_graphs(df)
    
    
    
if __name__ == "__main__":
    main()
