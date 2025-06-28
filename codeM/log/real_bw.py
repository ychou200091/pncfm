import time
import csv
import os

INTERFACES = ['s1-eth1', 's1-eth3', 's3-eth2','s13-eth2','s7-eth1', 's7-eth2', 's5-eth1', 's6-eth2', 's6-eth4','s8-eth5','s8-eth6','s2-eth3', 's4-eth5','s4-eth6','s4-eth7']


#INTERFACES = ['s1-eth1', 's1-eth3', 's3-eth2', 's2-eth3', 's4-eth5']
CSV_FILE = 'log/real_bw_log.csv'

prev_bytes = None

def get_tx_bytes(iface):
    """Get transmitted bytes from sysfs."""
    try:
        with open('/sys/class/net/{}/statistics/tx_bytes'.format(iface), 'r') as f:
            return int(f.read().strip())
    except IOError:
        return None


def write_header_if_needed():
    """Write CSV header if file does not exist yet (Python 2 version)."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'wb') as f:  # 'wb' is important for correct CSV formatting
            writer = csv.writer(f)
            writer.writerow(['timestamp'] + INTERFACES)


def log_bandwidth(prev_bytes, msg=None):
    
    """Calculate bandwidth and write to CSV (Python 2 version)."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    row = [timestamp]

    for iface in INTERFACES:
        curr_bytes = get_tx_bytes(iface)
        prev = prev_bytes.get(iface)

        if curr_bytes is None or prev is None:
            row.append('N/A')
        else:
            delta_bytes = curr_bytes - prev
            mbps = (delta_bytes * 8.0) / 1000000  # Convert to Mbit/s
            row.append("{0:.4f}".format(mbps))
            prev_bytes[iface] = curr_bytes

    if msg is not None:
        row.append(msg)

    with open(CSV_FILE, 'ab') as f:  # binary append mode
        writer = csv.writer(f)
        writer.writerow(row)




def init():
    global prev_bytes
    write_header_if_needed()
    prev_bytes = {iface: get_tx_bytes(iface) for iface in INTERFACES}

def main():
    global prev_bytes
    write_header_if_needed()
    prev_bytes = {iface: get_tx_bytes(iface) for iface in INTERFACES}

    try:
        while True:
            time.sleep(1)
            log_bandwidth(prev_bytes)
    except KeyboardInterrupt:
        print("Logging stopped.")

if __name__ == '__main__':
    main()
