

https://hackmd.io/MLVqE31WQGCQDHXOLP8m2w =>大部分的環境架設

1.基本上RYU ,OVS 要重新改過
2.OVS有改過的也給妳附上了 CODE/OVS281_modify
3.restart_OVS 為你重新編譯OVS後每次開機都要執行一次了幫你打包好了


腳本
------
paper_topo_standard_big.py =>為拓譜的腳本(包括打流量)
avgStats.awk =>為抓取iperf的結果資料的腳本(單個流量)
output_bw_copy => 為呼叫avgStats.awk 腳本的腳本(多個流量)
------
code/test/test_broker.py -中間實作溝通的 指令=>python test_broker.py 9089 9090
code/shortest_forwarding.py -為本論文所要執行的 指令=>
ryu-manager shortest_forwarding.py --observe-links --k-paths=2 --weight=hop --ofp-tcp-listen-port=6633
------
baseline 由_packet_in_handler裡面 註解 685~701(詳細自己看一下
CFM 由 Do_help裡面  註解 註解 618~630
meter註解 send_congestion 和network_Communication.py 裡面 deal 裡的-2 



