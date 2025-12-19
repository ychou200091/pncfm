# PNCFM - Profit-Aware Network Flow Management

Welcome to the PNCFM Repository.

This is the codebase for my graduate thesis: "Cooperative Route Management for Profit-Oriented Flows in Multi-domain SDN Networks."

This thesis proposes a profit-oriented cross-domain cooperative method that leverages the programmability of SDN to dynamically adjust bandwidth allocation and routing decisions based on the profit (an abstract economic value to the network owner) associated with each flow. 
For detailed experiment explanation and data, please refer to **docs/thesis.pdf**. Note, the thesis is in Chinese.

## The Problem (Business/Technical Context)

In multi-domain networks—like those found in large companies and schools—network operators face a fundamental challenge: **when some network segments are congested while others have available capacity, previous solutions do not consider the economic value of traffic when rerouting data flows to alleviate congestion.**

This naive approach leaves money on the table. If your network carries both:
- High-priority, revenue-generating streams (e.g., video conferencing: 10 Mbps = $500/hr value)
- Best-effort background traffic (e.g., backups: 10 Mbps = $10/hr value)

previous methods (CFM, MCRM) make routing decisions that maximize throughput and consider priority, not profit. They might route your $10/hr backup traffic and drop your $500/hr video call during congestion.


**Research Solution**: **Profit Negotiation Collaborative Flow Management (PNCFM)** adds profit awareness to network routing—making SDN controllers negotiate and allocate routes based on profit and bandwidth. It draws inspiration from previous research and a game-theoretic concept: the Nash Bargaining Solution. 

---

## Why This Matters

- **For Companies**: Maximize revenue from limited network infrastructure; better monetization of CDN/ISP services
- **For Research**: Likely the first to combine profit optimization with multi-domain SDN cooperation.
- **Showcasing Capabilities**: Demonstrates systems thinking, algorithmic innovation, and real-world problem solving


## Key Innovation: Differences from Previous Research

Previous work [CFM](https://ieeexplore.ieee.org/document/9322815) and [MCRM](https://ieeexplore.ieee.org/document/9720743/):
- ☑ Enabled cross-domain route borrowing
- ☑ MCRM considered priorities of different traffic, while CFM didn't consider any importance matrix while allocating network resources.
- ☑ Dynamic traffic re-assignment during congestions.
- ☒ No mechanism to prioritize high-profit traffic.
- ☒ No incentive mechanism for other domains to participate in cooperation.


**PNCFM adds**:
- Profit and bandwidth awareness
- Intelligent rate limiting based on profit: Profit maximization module.
- Negotiation procedures between domains to provide incentives for other domains to help.

**Notably**, in mixed-correlation scenarios (where profit and bandwidth don't correlate), PNCFM achieves **15% higher profit than MCRM, 37% higher than CFM**.


## Experimental Results
We validated PNCFM against three methods (baseline, CFM, and MCRM) under realistic multi-domain congestion scenarios.


**Test 1: Different Congestion Situation**
| Scenario | PNCFM vs Baseline Profit Gain| PNCFM vs CFM Profit Gain | PNCFM vs MCRM Profit Gain |
|----------|------------------|--------------|---------------|
|Case| 49%| 0%| 0%| 
|Case 2|  12%| 13%| 5%| 
|Case 3| 7%| 25%| 4%| 
|Case 4| 42%| 22%| 11%| 

For detailed experiment explanation and data, please refer to **docs/thesis.pdf**

**Test 2: Profit-Bandwidth Correlation Test**
| Scenario | PNCFM vs Baseline Profit Gain| PNCFM vs CFM Profit Gain | PNCFM vs MCRM Profit Gain |
|----------|------------------|--------------|---------------|
|Case 1: Positive Correlation | 21%| 9%| 5% |
|Case 2: Negative Correlation|  42%| 23% |16% |
|Case 3: Mixed Correlation |47%| 37%| 15% |

---

## Implementation Details

**Technology Stack**:
- **SDN Controller**: **[Ryu Controller](https://github.com/faucetsdn/ryu)** (Python-based, chosen for extensibility)
- **Network Simulation**:  **[Mininet](https://mininet.org/)**+ modified Open vSwitch. Reference **[Stochastic Switching](https://github.com/saeenali/openvswitch/wiki/Stochastic-Switching-using-Open-vSwitch-in-Mininet)** for modifications made.
- **Testing**:  multi-domain topologies with 3 domains. The experiments used **[iPerf](https://iperf.fr/)** to send traffic and collect traffic data.

**Core Algorithms** (`src/`):
- `pncfm.py`: Profit negotiation and flow routing logic
- `network_Communication.py`: Inter-domain controller communication
- `network_monitor.py`: Real-time profit/bandwidth metrics collection and decision making
- `ryu_controller_shortest_forwarding.py`: Main SDN controller implementation


## Problem Statement & Related Work

### Motivation

In the past, many methods have been proposed to manage single networks or multiple networks. In a multi-domain network, each domain operates independently. When some domains experience congestion while others have available capacity, the lack of inter-domain cooperation results in suboptimal resource utilization. Previous research such as [CFM](https://ieeexplore.ieee.org/document/9322815) and [MCRM](https://ieeexplore.ieee.org/document/9720743/) addressed this challenge by proposing cooperative methods between controllers. These methods enable the borrowing of routes from different domains—allowing a data flow's packets to exit one domain's gateway switch, traverse through another domain, and re-enter the original domain via a different switch, which is important to alleviate congestion.

However, data flows may have different "profit" (an abstract economic value) to the network owner, which prior research has not adequately considered. This thesis proposes **Profit Negotiation Collaborative Flow Management (PNCFM)**, a novel method designed to maximize the overall profit gain of multi-domain networks.

### Experimental Results

We conducted two sets of experiments comparing PNCFM against three baseline methods: baseline routing, CFM, and MCRM.

1. **[Test 1] Overall Performance Evaluation**: PNCFM demonstrated improved total throughput and profit output in multi-domain SDN networks compared to the other methods, as well as a better adaptability under complex situations. 

    For example, when route borrowing is occurring and the borrowing domain becomes congested, PNCFM can effectively reassign portions of traffic to avoid the congested borrowing domain and instead route through the original domain. Furthermore, profit-oriented rate limiting is applied across various scenarios to ensure maximum profit gain.  

2. **[Test 2] Profit-to-Bandwidth Correlation Analysis**: This experiment examined how flows with different profit-to-bandwidth ratios (or unit profit) behave under congestion. Results show that PNCFM optimally utilizes network resources to achieve the highest profit gain among all methods compared.

### Research Contribution
Our experimental evaluation demonstrates that PNCFM achieves performance on par with existing methods across various network conditions. In specific scenarios, PNCFM improves profit gain by 11%, 22%, and 42% compared to MCRM, CFM, and baseline routing, respectively.

During the **Profit-to-Bandwidth Correlation Analysis** phase, we observed that when profit gain and bandwidth consumption exhibit mixed correlations—where certain data flows demonstrate positive correlation between profit and bandwidth consumption (e.g., 5 Mbps = 100 profit units, 2 Mbps = 50 profit units) and some data flows have negative correlations — PNCFM achieves superior performance. Specifically, PNCFM improves profit gain by 15% relative to MCRM, 37% relative to CFM, and 47% relative to baseline routing.

In summary, our experimental results substantiate that PNCFM more effectively allocates network resources across diverse scenarios, thereby maximizing overall profit extraction from multi-domain SDN networks.

### Background Information

This project involves several key components:

- **Controllers**: Make rules and oversee designated network areas. In this thesis, controllers are responsible for network data collection, cross-domain cooperation, flow rate metering, flow splitting, and load balancing.
- **Switches**: Forward packets and provide controllers with real-time network data (bytes sent, latency, packet loss, etc.).
- **Hosts**: User devices that send packets between each other. At the end of each simulation, iPerf reports from flow receivers are analyzed.

### Operational Context

In large organizations, schools, and data centers, network administrators must manage extensive networks where some traffic is more important than others. We assume each network traffic has an economic value (or "profit") to the network owner. This thesis develops a method to extract more profit from network resources than previous approaches. To achieve this, the following functionality is essential: cross-controller communication, switch flow data extraction and organization, metering, load balancing, and cross-domain cooperation.

### Terminology

- **Data Flow**: A series of data packets transmitted from a source to a destination.

**Flow Types**:
- **Local Flow**: The source and destination hosts are in the same domain.
- **Cross-Domain Flow**: The source and destination hosts are in different domains.
- **Assisting Flow**: Originally a local flow that is redirected due to load balancing algorithms. It exits the original domain to an assisting domain and returns to the original domain via a different gateway switch to complete packet transportation. 

## Quick Start

Refer to `docs/setup.md` for detailed setup instructions.

## Run Simulations

This project includes comprehensive simulation capabilities built on Mininet, Open vSwitch, Ryu controller, and a message server.

Refer to `docs/run_simulation.md` for step-by-step instructions on running simulations.


## Architecture & Design Decisions

### Network Topology

![simulation_topology](resources/diagrams_simulation_topology.drawio.png)

### Ryu Controller Modification

**Why We Modified Open vSwitch**: Standard OVS does not support flow splitting—the ability to forward a data flow's packets across multiple output ports. The controller determines how many packets exit each port. For example, a flow consuming 5 Mbps of bandwidth normally arrives at Switch A on port 1 and exits on port 2. During congestion, the controller may reduce traffic on port 2's attached links. With our modification, the controller can split this flow: sending 2 Mbps out port 2 and 3 Mbps out port 3. 

### System Architecture Flowchart

![PNCFM-overview](resources/diagram_PNCFM_overview.drawio.png)


## Repository structure

This section explains the organization of directories and files in the project following industry-standard software engineering practices.

### Directory Purpose Summary

| Directory | Purpose |
|-----------|---------|
| **`src/`** | Core algorithms, controllers, and network logic that form the project's foundation |
| **`scripts/`** | Executable scripts for simulation, analysis, and system management |
| **`tests/`** | Unit tests, integration tests, and experimental simulation variants |
| **`dependencies/`** | External source code (Modified OVS) with custom changes |
| **`outputs/`** | Generated simulation results, logs, and CSV analysis files |
| **`docs/`** | User-facing documentation and guides |
| **`resources/`** | Static assets like diagrams, images, and notification sound |

### Key Files

- **`src/pncfm.py`**: Main algorithm implementation for PNCFM (Profit Negotiation Collaborative Flow Management).
- **`src/setting.py`**: Core environment parameters (DISCOVERY_PERIOD, MONITOR_PERIOD, PLR threshold, SLICE, MAX_CAPACITY).
- **`src/flow_info.py`**: Test case definitions and flow configurations.
- **`scripts/run_mininet_simulation.py`**: Primary entry point for running simulations.
- **`scripts/ryu_controller_shortest_forwarding.py`**: Main network controller script that runs during simulations.
- **`docs/run_simulation.md`**: Complete guide for setting up and running simulations.
- **`dependencies/ovs/`**: Custom-modified Open vSwitch source code with thesis-specific features.

### Detailed File Tree
```
PNCFM/
├── README.md                      # Project overview and getting started guide
├── .gitignore                     # Git ignore rules for build artifacts and generated files
├── requirements.txt               # Python dependencies (Ryu, etc.)
│
├── dependencies/                  # External dependencies and modified source code
│   └── OVS281_modified/          # Custom-modified Open vSwitch 2.8.1 source code
│       ├── README.md             # Explains modifications made to OVS
│       ├── CHANGES.md            # Detailed list of custom changes
│       └── [OVS source files]
├── scripts/                      # Utility and analysis scripts
│   ├── run_mininet_simulation.py         # Main simulation runner
│   ├── ryu_controller_shortest_forwarding.py  # Ryu controller 
│   ├── output_test_organize_data.py      # Organize and parse simulation results
│   ├── out_all_bw_convert.py            # Convert iPerf output to CSV
│   ├── script_ovs_install.sh            # Install Open vSwitch
│   ├── script_ovs_start.sh              # Start OVS services
│   ├── script_ovs_restart.sh            # Restart OVS services
│   └── script_ovs_notes.sh              # OVS configuration notes and related commands
│
├── src/                          # Core source code (algorithms, network logic, configuration)
│   ├── __init__.py
│   ├── pncfm.py                 # Main PNCFM (Profit-oriented Network Cooperation) algorithm
│   ├── bw_alloc.py              # Bandwidth allocation logic for CFM and MCRM algorithms.
│   ├── network_awareness.py     # For ryu controller: Network topology discovery and awareness
│   ├── network_Communication.py # For ryu controller: Inter-domain controller communication
│   ├── network_delay_detector.py # For ryu controller: Link delay detection
│   ├── network_monitor.py       # For ryu controller: Network monitoring and metrics collection
│   ├── flow_info.py             # For the whole project: Flow configuration and test case definitions
│   ├── setting.py               # For ryu controller: Environment parameters (DISCOVERY_PERIOD, MONITOR_PERIOD, PLR, SLICE, MAX_CAPACITY)
│   └── real_bw.py               # For simulation realtime monitoring: Real-time bandwidth tracking
│
├── tests/                        # Test cases and experimental simulations
│   ├── __init__.py
│   ├── paper_topo_test.py       # Test if mininet works.
│   ├── SimpleSwitch13.py         # Simple OpenFlow 1.3 switch implementation
│   ├── test_broker.py           # Message broker for inter-controller communication
│   ├── test_client.py           # Test client for broker communication
│   ├── test_pub.py              # Publisher for testing message passing
│   └── simulation/              # Experimental and variant simulations
│       ├── simu.py              # test algorithms variant1
│       ├── simu2.py             # test algorithms variant2
│       ├── simu3.py             # test algorithms variant3
│       └── simu_nbs.py          # PNCFM related test algorithms.
│
├── outputs/                      # Generated results and logs
│   ├── output_flow_info.csv     # Flow information summary. Get this by running flow_info.py directly.
│   └── log/                     # Simulation logs and results
│       ├── real_bw_log_stage*.csv  # Test 1 stage-specific bandwidth logs
│       ├── real_bw_log_t2_case*.csv # Test 2 case-specific bandwidth logs
│       ├── all_method_comparison/   # Comparative analysis aggregating results from all algorithm implementations(Baseline, CFM, MCRM, PNCFM)
│       ├── Baseline/            # Baseline algorithm results
│       ├── CFM/                 # CFM algorithm results
│       ├── MCRM/                # MCRM algorithm results
│       └── PNCFM/               # PNCFM algorithm results
│
├── docs/                         # Documentation
│   ├── README.md               # Documentation index
│   ├── run_simulation.md        # Step-by-step guide to run simulations
│   ├── reorganization.md        # File reorganization plan and structure
│   ├── interview_related_questions_en.md  # Interview Q&A (English)
│   ├── interview_related_questions.md     # Interview Q&A (Chinese)
│   ├── other_notes.md          # Additional notes and observations
│   └── todo.md                 # Project TODO list
│
└── resources/                    # Supporting resources, including diagrams, a ringtone, etc.
    └── diagrams.drawio         # Network topology and system architecture diagrams
```

---


## Known Limitations & Future Work

**Current Scope**:
- Tested on topologies with 3 domains
- Assumes stable profit values during simulation; dynamic repricing not evaluated
- Requires modified OVS; not compatible with standard OVS versions or future updates

**Future Directions**:
- Dynamic profit adjustment based on real-time market conditions
- Integration with real production networks
- Incorporate inter-domain and intra-domain fairness metrics (e.g., Jain's Fairness Index)
- Account for flow characteristics where partial bandwidth allocation is insufficient (e.g., live streaming requires minimum bitrate thresholds) 

---

## Contact & Attribution

This work is my graduate thesis research (2025). 

If you:
- **Want to use this commercially**: Requires GPLv3 compliance; contact me via [LinkedIn](https://www.linkedin.com/in/choumengyu-18174019a/) for licensing details.
- **Are hiring**: Connect with me on [LinkedIn](https://www.linkedin.com/in/choumengyu-18174019a/).

---

## 🛡️ License

This project is licensed under the **GPLv3 License**. You are free to use, modify, and share this project with proper attribution, but you can't use it for commercialization.
Any derivative work, even if modified, must also be licensed under GPLv3. 