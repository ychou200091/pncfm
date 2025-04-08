import csv
import os
'''
    Goal of this file:
        Input: Iperf server records.
        Ouput: A csv file with headers
            "Time,  Transfer(MBytes),   Bandwidth(Mbits/sec),   Packet_Lost,
            Total_Packets,  Min_Latency(ms),    Max_Latency(ms),    Avg_Latency(ms)"

"
'''
file_root =  "/home/admin123/Desktop/grad/env/codeM/log/"
# List of input files to process
input_files = [
    "1_3.out",
    "2_4.out",
    "5_6.out",
    "9_10.out",
]

def convert_to_mbytes(value, unit):
    """Convert KBytes or MBytes to MBytes"""
    value = float(value)
    if unit == "KBytes":
        return value / 1024
    elif unit == "MBytes":
        return value
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
            if start_time == "0.0000" and "sec" in parts[3] and float(end_time) > 100:
                is_overall = True
                #start_time = "Overall"
                continue # skip it

            
            # Find transfered data
            transfer_idx = parts.index("sec") + 1
            transfer_value = parts[transfer_idx]
            transfer_unit = parts[transfer_idx + 1]
            
            # Find bandwidth data
            bandwidth_idx = transfer_idx + 2
            bandwidth_value = parts[bandwidth_idx]
            bandwidth_unit = parts[bandwidth_idx + 1]
            
            # Find packets lost and total packets
            packets_lost = parts[10].split("/")[0] 
            total_packets = parts[11]
            # for i, part in enumerate(parts):
            #     if "/" in part and "(" in parts[i+1]:
            #         packets_info = part.split("/")
            #         packets_lost = packets_info[0]
            #         total_packets = packets_info[1]
            #         break
            
            # Find latency information
            latency_info = parts[13].split("/")
            #
            
            
            
            avg_latency = latency_info[0]
            if len(latency_info)<3:
                #print("parts:",parts)
                #print("latency_info:",latency_info)
                latency_info = parts[14].split("/")
                #print("more latency_info:",latency_info)
                min_latency = latency_info[0]
                #max_latency = latency_info[1]
                if len(latency_info)<2:
                    latency_info = parts[15].split("/")
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
                    "min_latency": float(min_latency),
                    "max_latency": float(max_latency),
                    "avg_latency": [float(avg_latency),float(avg_latency)] # 0 is avg, 1,2,3,4... are records 
                }
            else:
                # Add values for the same timestamp
                aggregated_data[start_time]["transfer"] += transfer_mbytes
                aggregated_data[start_time]["bandwidth"] += bandwidth_mbits
                aggregated_data[start_time]["packets_lost"] += int(packets_lost)
                aggregated_data[start_time]["total_packets"] += int(total_packets)
                
                # Keep only the minimum min_latency
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

def main():
    # Process each file
    for input_file in input_files:
        input_file= file_root+input_file
        output_file = input_file.replace(".out", ".csv")
        rows_processed = process_file(input_file, output_file)
        print(f"Processed {rows_processed} unique timestamps from {input_file}")

if __name__ == "__main__":
    main()