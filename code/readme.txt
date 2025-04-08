環境安裝:
Ryu: https://github.com/muzixing/ryu

Open vSwitch(安裝指定版本、meter table): https://www.cnblogs.com/goldsunshine/p/10959199.html

Open vSwitch中ovs-ofctl 指令:
http://www.rendoumi.com/open-vswitchzhong-ovs-ofctlde-xiang-xi-yong-fa/

Mininet : 
https://sites.google.com/site/sdnruantidingyiwanglu/vmware-xia-zai-yu-an-zhuang/mininet


論文程式參考(環境參數):
https://github.com/muzixing/ryu/tree/master/ryu/app/network_awareness

論文程式啟動:

拓樸:
python paper_topo.py


controller:
ryu-manager shortest_forwarding.py --observe-links --k-paths=2 --weight=hop --ofp-tcp-listen-port=6633 

(不同controller更改port，6633、6634、6635)


