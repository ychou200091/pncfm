# Document Overview

This document explains how to run the simulation after the environment has been correctly set up.

Recommendation: open five terminals to run the simulation.

## Restart OVS when the machine starts

In terminal 1: run the script that restarts OVS at boot.

Go to the directory that contains the `restart_OVS` script and run it. For example:

```sh
cd /Desktop/project/grad/env/code/
sudo ./restart_OVS.sh
```
or 
```
sudo ~/Desktop/project/grad/env/code/restart_OVS
```

## Prepare simulation parameters

1. Use `flow_info.py` to choose the test, case, and method you want to run.
     
     - Find your `flow_info.py` file.
     - All test cases are defined in the Python code; choose the test and case you want to run.
         - Edit `running_test_num` and `case_num` to select the simulation.
             - For example, to run test 1 case 4, set `running_test_num = 1` and `case_num = 4`.
         - To edit specific dataflow parameters, locate and modify dictionary variables such as `test_1_4stages_1`, `test_2_4cases_1`, `test_2_4cases_3`.
     - Edit `CURRENT_MODE` to choose the load-balancing algorithm:
         - `0`: PNCFM
         - `1`: MCRM
         - `2`: CFM
         - `3`: Baseline
     - Notes: 
        - The controllers and simulation environment rely on `flow_info.py` for configuration.
        - This project uses many absolute paths; verify that all paths are correct before running it.
            - Note: I have reorganized the files and directory structure to align with industry standards (e.g., `docs/`, `scripts/`, `bin/`, etc., with a well-documented `README.md` file). This reorganization is primarily intended for HR professionals and employers to review my work and algorithms. However, I have not retested all dependencies after this reorganization. I have also removed files I deemed unnecessary for this repository (e.g., old duplicates and logs). If you need access to the files before reorganization, please contact me by raising an "issue" or creating a "pull request". Please note that my original "messy folder" runs correctly, but you may find it difficult to locate specific code due to its disorganized structure.

2. Edit `setting.py` before you run the simulation. `setting.py` contains meta parameters for the running environment. Below are the parameters and their meanings:
- DISCOVERY_PERIOD: For discovering the topology. Default: `DISCOVERY_PERIOD = 3`
- MONITOR_PERIOD: For monitoring traffic. Default: `MONITOR_PERIOD = 3`
- TOSHOW: For displaying information in the terminal. Default: `TOSHOW = True`
- MAX_CAPACITY: Maximum capacity of a link. Default: `MAX_CAPACITY = 281474976710655L`
- SLICE: The percentage of profit that a domain's controller is willing to share with another domain. Default: `SLICE = 0.3`
- PLR: The packet loss rate of a link that triggers load balancing algorithms. Default: `PLR = 0.2`

## Start the simulation

1. In terminal 2: Open the Test Broker.

    Find your test broker and use ports `9089` and `9090`. Example:

     ```sh
     cd ~/Desktop/project/grad/env/code/test
     python ~/Desktop/project/grad/env/code/test/test_broker.py 9089 9090
     ```

2. Start the Ryu controllers (terminals 3, 4, and 5).

    For these three controllers, open ports `6633`, `6634`, and `6635`, and redirect each controller's output to a corresponding log file. Example:

     ```sh
     cd ~/Desktop/project/grad/env/codeM
     ryu-manager ryu_controller_shortest_forwarding.py --observe-links --k-paths=2 --weight=hop --ofp-tcp-listen-port=6633 > 6633_FPLM.txt

     ryu-manager ryu_controller_shortest_forwarding.py --observe-links --k-paths=2 --weight=hop --ofp-tcp-listen-port=6634 > 6634_FPLM.txt

     ryu-manager ryu_controller_shortest_forwarding.py --observe-links --k-paths=2 --weight=hop --ofp-tcp-listen-port=6635 > 6635_FPLM.txt
     ```

3. Log real-time bandwidth.

     

4. Start the Mininet topology and run the network simulation.

     ```sh
     cd ~/Desktop/project/grad/env/codeM
     sudo python run_mininet_simulation.py
     ```

     Check the following settings before running:
     - Controller port numbers must match the ports opened by the Ryu controllers, e.g. ``c0_port, c1_port, c2_port``
     - Add or remove hosts and links as needed.
     - Adjust link bandwidth and port numbers if necessary.
          
          In the python code,  `net.addLink(s4, s16, 2, 1, cls=TCLink, bw=tc_bw)` means switch `s4` uses port `2` to connect to switch `s16`'s port `1`, the link uses traffic control (`TCLink`), and ``tc_bw=10`` (10 Mbps) by default.
     - ``run_mininet_simulation.py`` file is used every time when running the simulations. It tracks the amount of bytes each port outputs per second. 
     
          Remember to verify and set the `INTERFACES` variable to the list of ports you want to monitor. For example:

          ```py
          INTERFACES = ['s1-eth1', 's1-eth3', 's3-eth2', 's13-eth2', 's7-eth1', 's7-eth2','s5-eth1', 's6-eth2', 's6-eth3', 's6-eth4', 's6-eth5']
          ```
          Or run the script seperately, for example: 
          ```sh
          cd ~/Desktop/project/grad/env/codeM/log
          python3 real_bw.py
          ```


## Compute statistics

Two steps:

1. Convert `iperf` output to CSV files:

     ```sh
     cd ~/Desktop/project/grad/env/codeM/log
     python3 out_all_bw_convert.py
     ```

2. Analyze the CSV files and generate graphs and usable data:

     ```sh
     cd ~/Desktop/project/grad/env/codeM/
     python3 output_test_organize_data.py
     # or
     python3 ~/Desktop/project/grad/env/codeM/output_test_organize_data.py
     ```

## Notes and additional information

- `PNCFM` corresponds to `profitNBS`. If you see `profitNBS` in the project, it refers to `PNCFM` because the name was changed midway.

- Test Mininet example:

    ```sh
    sudo mn --controller=remote,ip=127.0.0.1,port=6635 --topo=tree,depth=2,fanout=2 --switch ovs,protocols=OpenFlow13
    ```

- iperf server and client examples:

    - h1 -> h3:

        1. On `h3` (server):

             ```sh
             iperf -u -s -e -i 5
             ```

        2. On `h1` (client):

             ```sh
             iperf -u -c 10.0.0.3 -b 10m -i 5 -e -t 40
             ```

    - h5 -> h6:

        1. On `h6` (server):

             ```sh
             iperf -u -s -e -i 5
             ```

        2. On `h5` (client):

             ```sh
             iperf -u -c 10.0.0.10 -b 10m -i 5 -e -t 40
             ```

    - `iperf3` example:

        ```sh
        iperf3 -u -s -e -i 3
        iperf3 -c 10.0.0.3 -u -b 10M -t 40 -i 3
        ```





