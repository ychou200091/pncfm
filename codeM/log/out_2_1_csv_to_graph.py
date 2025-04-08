import os
import pandas as pd
import matplotlib.pyplot as plt

file_root = "/home/admin123/Desktop/grad/env/codeM/log/CFM"

file_list = {
    "1_3.csv": {"name": "Flow A", "start_time": 0},
    "2_4.csv": {"name": "Flow B", "start_time": 25},
    "9_10.csv": {"name": "Flow C", "start_time": 100},
    "5_6.csv": {"name": "Flow D", "start_time": 130}
}


bandwidth_data = {}
transfer_data = {}
combined_data = pd.DataFrame()

# Containers for summary csv
summary_df = pd.DataFrame()
flow_throughput_totals = {}
packet_loss_data = {}

# Read and align data by start_time
def organize_data():
    global combined_data
    global summary_df
    for filename, meta in file_list.items():
        path = os.path.join(file_root, filename)
        df = pd.read_csv(path)
        df["Time"] = df["Time"] + meta["start_time"]
        df['Flow'] = meta['name']

        for _, row in df.iterrows():
            t = row["Time"]
            bandwidth_data[t] = bandwidth_data.get(t, 0) + row["Bandwidth(Mbits/sec)"]
            transfer_data[t] = transfer_data.get(t, 0) + row["Transfer(MBytes)"]

        combined_data = pd.concat([combined_data, df])

        # For summary CSV: pivot into separate columns by flow
        temp = df[['Time', 'Bandwidth(Mbits/sec)', 'Transfer(MBytes)']].copy()
        temp = temp.rename(columns={
            "Bandwidth(Mbits/sec)": f"{meta['name']} Bandwidth(Mbits/sec)",
            "Transfer(MBytes)": f"{meta['name']} Transfer(MBytes)"
        })
        if summary_df.empty:
            summary_df = temp
        else:
            summary_df = pd.merge(summary_df, temp, on="Time", how="outer")

        # Sum up throughput per flow
        flow_throughput_totals[meta['name']] = df["Transfer(MBytes)"].sum()

        
        # Packet Loss Summary Calculation
        total_packets = df["Total Datagrams"].sum() if "Total Datagrams" in df.columns else None
        lost_packets = df["Lost Datagrams"].sum() if "Lost Datagrams" in df.columns else None

        if total_packets is not None and lost_packets is not None:
            loss_rate = lost_packets / total_packets if total_packets > 0 else 0
            packet_loss_data[meta["name"]] = {
                "transferred": total_packets,
                "lost": lost_packets,
                "loss_rate": loss_rate
            }


# === Save Summary CSV (time series) ===
def make_csv_1():
    global summary_df
    summary_df = summary_df.sort_values(by="Time").fillna(0)
    summary_csv_path = os.path.join(file_root, "graph_data_summary.csv")
    summary_df.to_csv(summary_csv_path, index=False)

    # === Save total throughput CSV ===
    totals = {f"total throughput of {flow}": value for flow, value in flow_throughput_totals.items()}
    totals["total throughput of network"] = sum(totals.values())
    totals_df = pd.DataFrame([totals])
    total_throughput_csv_path = os.path.join(file_root, "total_throughput_summary.csv")
    totals_df.to_csv(total_throughput_csv_path, index=False)


def make_csv_2():
    # Calculate network totals
    network_transferred = sum(v["transferred"] for v in packet_loss_data.values())
    network_lost = sum(v["lost"] for v in packet_loss_data.values())
    network_loss_rate = network_lost / network_transferred if network_transferred > 0 else 0

    # Flatten into single-row dictionary
    result_row = {}
    for flow_name in ["Flow A", "Flow B", "Flow C", "Flow D"]:
        if flow_name in packet_loss_data:
            data = packet_loss_data[flow_name]
            result_row[f"{flow_name}'s packet transferred"] = data["transferred"]
            result_row[f"{flow_name}'s packet lost"] = data["lost"]
            result_row[f"{flow_name}'s packet lost rate"] = data["loss_rate"]

    # Add network stats
    result_row["Network's packet transferred"] = network_transferred
    result_row["Network's packet lost"] = network_lost
    result_row["Network's packet lost rate"] = network_loss_rate

    # Write to CSV
    packet_loss_csv_path = os.path.join(file_root, "packet_loss_summary.csv")
    pd.DataFrame([result_row]).to_csv(packet_loss_csv_path, index=False)


# === Graph 1: Bandwidth of Different Flows ===
def make_graph_1():
    plt.figure(figsize=(10, 6))
    for flow_name in file_list.values():
        flow_data = combined_data[combined_data['Flow'] == flow_name['name']]
        plt.plot(flow_data['Time'], flow_data['Bandwidth(Mbits/sec)'], label=flow_name['name'])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Bandwidth (Mbits/sec)')
    plt.title('Bandwidth of Different Flows')
    plt.legend()
    plt.savefig(os.path.join(file_root, "graph_diff_flow_bandwidth.png"))
    plt.close()


# === Graph 2: Throughput of Different Flows ===
def make_graph_2():
    plt.figure(figsize=(10, 6))
    for flow_name in file_list.values():
        flow_data = combined_data[combined_data['Flow'] == flow_name['name']]
        plt.plot(flow_data['Time'], flow_data['Transfer(MBytes)'], label=flow_name['name'])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Transfered(MBytes)')
    plt.title('Throughput of Different Flows')
    plt.legend()
    plt.savefig(os.path.join(file_root, "graph_diff_flow_throughput.png"))
    plt.close()

# === Graph 3: Total Bandwidth Over Time ===
def make_graph_3():
    sorted_bandwidth = dict(sorted(bandwidth_data.items()))
    plt.figure(figsize=(10, 6))
    plt.plot(list(sorted_bandwidth.keys()), list(sorted_bandwidth.values()), label="Total Bandwidth")
    plt.xlabel("Time (s)")
    plt.ylabel("Bandwidth (Mbits/sec)")
    plt.title("Total Bandwidth Over Time")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(file_root, "graph_bandwidth_over_time.png"))
    plt.close()

# === Graph 4: Total Throughput Over Time ===
def make_graph_4():
    sorted_transfer = dict(sorted(transfer_data.items()))
    plt.figure(figsize=(10, 6))
    plt.plot(list(sorted_transfer.keys()), list(sorted_transfer.values()), label="Total Throughput", color='orange')
    plt.xlabel("Time (s)")
    plt.ylabel("Transfer (MBytes)")
    plt.title("Throughput Over Time")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(file_root, "graph_throughput_over_time.png"))
    plt.close()

def main():
    organize_data()
    make_csv_1()
    make_csv_2()

    make_graph_1()
    make_graph_2()
    make_graph_3()
    make_graph_4()


if __name__ == '__main__':
    main()