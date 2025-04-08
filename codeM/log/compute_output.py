import os
import matplotlib.pyplot as plt
import numpy as np

# Sample hardcoded file list with start times in seconds
file_list = {
    "avgTCP2_4.out": {"name": "Flow A", "start_time": 0},
    "avgTCP1_3.out": {"name": "Flow B", "start_time": 25},
    "avgTCP9_10.out": {"name": "Flow C", "start_time": 100},
    "avgTCP5_6.out": {"name": "Flow D", "start_time": 130}
}

# Data containers for the combined graph
bandwidth_over_time = {}
datagrams_over_time = {}

# Process each file
for filename, info in file_list.items():
    filename= "/home/admin123/Desktop/grad/env/codeM/log/"+filename
    if not os.path.exists(filename):
        print "file[",filename,"] does not exist"

    start_time = info["start_time"]
    with open(filename, 'r') as f:
        lines = f.readlines()[1:]  # skip header
        for i, line in enumerate(lines):
            parts = line.strip().split()
            #print parts
            if len(parts) < 4 or len(parts)>5:
                continue
            try:
                int(parts[1])
            except:
                continue
            time_sec = start_time + i 
            bandwidth = float(parts[0])
            total_datagrams = int(parts[2])
            
            bandwidth_over_time[time_sec] = round( bandwidth_over_time.get(time_sec, 0) + bandwidth , 3)
            datagrams_over_time[time_sec] = datagrams_over_time.get(time_sec, 0) + total_datagrams

# Sort and prepare data for plotting
times = sorted(bandwidth_over_time.keys())
bandwidth_values = [bandwidth_over_time[t] for t in times]
datagram_values = [datagrams_over_time[t] for t in times]
print "bandwidth_values:",bandwidth_over_time
print "datagram_values:",datagrams_over_time

# Plotting Bandwidth over Time
plt.figure(figsize=(12, 6))
plt.plot(times, bandwidth_values, marker='o', label="Total Bandwidth")
plt.title("Total Bandwidth over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Bandwidth (Mbps)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("bandwidth_over_time.png")

# Plotting Total Datagrams over Time
plt.figure(figsize=(12, 6))
plt.plot(times, datagram_values, marker='s', color='orange', label="Total Datagrams")
plt.title("Total Datagrams over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Total Datagrams")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("datagrams_over_time.png")

"Graphs generated and saved as PNG files."

import csv

# Get the union of all time keys

with open('output.csv', 'wb') as csvfile:  # 'wb' is important for correct newlines
    writer = csv.writer(csvfile)
    writer.writerow(['time', 'bandwidth', 'datagrams'])
    for t in sorted(set(bandwidth_over_time) | set(datagrams_over_time)):
        writer.writerow([t, bandwidth_over_time.get(t, 0.0), datagrams_over_time.get(t, 0.0)])

