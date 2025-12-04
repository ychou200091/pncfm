# Copyright (C) 2016 Li Cheng at Beijing University of Posts
# and Telecommunications. www.muzixing.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import struct
import networkx as nx
from operator import attrgetter
from ryu import cfg
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from time import sleep, ctime
from time import time as current_time
import time, random
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

from algorithms import network_awareness
from algorithms import network_monitor
from algorithms import network_delay_detector
from algorithms import network_Communication
import setting
import algorithms.flow_info as flow_infos
import algorithms.pncfm

CURRENT_MODE = flow_infos.CURRENT_MODE  # 0:PNCFM, 1:MCRM, 2: CFM
CONF = cfg.CONF
ip_domain = flow_infos.ip_domain
switch_domain={6633:1,6634:2,6635:3}
out_door_port={13:2,4:4,14:1,7:3,14:1, 11:4, 16:2,
               18:2,9:4, 6:3, 17:1
               }

out_door={'10.0.0.3':4,'10.0.0.4':4,'10.0.0.1':13,'10.0.0.2':13,'10.0.0.6':4,
          '10.0.0.5':13, '10.0.0.11':11 ,'10.0.0.12':17, 
          '10.0.0.7':6,'10.0.0.10':18, 
          '10.0.0.14':13,'10.0.0.15':4, 
          }
#in_door={'10.0.0.3':13,'10.0.0.4':13,'10.0.0.1':4,'10.0.0.2':4}

class ShortestForwarding(app_manager.RyuApp):
    """
        ShortestForwarding is a Ryu app for forwarding packets in shortest
        path.
        The shortest path computation is done by module network awareness,
        network monitor and network delay detector.
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        "network_awareness": network_awareness.NetworkAwareness,
        "network_monitor": network_monitor.NetworkMonitor,
        #"network_delay_detector": network_delay_detector.NetworkDelayDetector}
        "network_delay_detector": network_delay_detector.NetworkDelayDetector,
        "network_commun":network_Communication.Controller_Communication}

    WEIGHT_MODEL = {'hop': 'weight', 'delay': "delay", "bw": "bw" , 'hop-p':'profit' }

    def __init__(self, *args, **kwargs):
        super(ShortestForwarding, self).__init__(*args, **kwargs)
        self.name = 'shortest_forwarding'
        self.awareness = kwargs["network_awareness"]
        self.monitor = kwargs["network_monitor"]
        self.delay_detector = kwargs["network_delay_detector"]
        self.network_commun = kwargs["network_commun"]
        self.datapaths = {}
        self.weight = self.WEIGHT_MODEL[CONF.weight]
        
    def set_weight_mode(self, weight):
        """
            set weight mode of path calculating.
        """
        self.weight = weight
        if self.weight == self.WEIGHT_MODEL['hop']:
            self.awareness.get_shortest_paths(weight=self.weight)
        return True

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """
            Collect datapath information.
        """
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def add_flow(self, dp, p, match, actions, idle_timeout=15, hard_timeout=40,use_meter=False, dst_port=None):
        """
            Send a flow entry to datapath.
        """
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if use_meter:
            flow = (match['ipv4_src'],match['ipv4_dst'])
            if flow in self.monitor.metertable.keys():
                #print("dp.id == self.monitor.metertable[flow][dpid] ",dp)
                #print (dp.id)
                #print(self.monitor.metertable[flow]["dpid"] )
                #print("dst_port == self.monitor.metertable[flow][outport] ", dst_port , self.monitor.metertable[flow]["outport"] )
                
                if dp.id == self.monitor.metertable[flow]["dpid"] and dst_port == self.monitor.metertable[flow]["outport"]:
                    # add rate limit 
                    if "meter_id" in self.monitor.metertable[flow].keys():
                        # don't make new rate limit, use old limit
                        meter_id = self.monitor.metertable[flow]["meter_id"]
                    else:
                        # get new meter id and install rate limit
                        ids = self.monitor.get_existing_meter_id()
                        
                        meter_id = self.get_unique_num100(ids)
                        rate_mbps = self.monitor.metertable[flow]["rate"]
                        self.monitor.metertable[flow]["meter_id"] = meter_id
                        self.add_meter_entry(dp,meter_id,rate_mbps)
                    print("[Add_meter_entry] meter_id:",self.monitor.metertable[flow]["meter_id"],"rate: ",self.monitor.metertable[flow]["rate"], "flow: ", flow, "dpid-port",(dp.id,dst_port) )                        
                    inst.append(parser.OFPInstructionMeter(meter_id,ofproto.OFPIT_METER))
                elif dp.id == self.monitor.metertable[flow]["dpid2"] and dst_port == self.monitor.metertable[flow]["outport2"]:
                    # limit rate on Reverse direction 
                    if "meter_id2" in self.monitor.metertable[flow].keys():
                        # don't add new rate limit, use old limit
                        meter_id = self.monitor.metertable[flow]["meter_id2"]
                    else:
                        # get new meter id and install rate limit
                        ids = [v["meter_id2"] for v in self.monitor.metertable.itervalues() if "meter_id2" in v]  
                        meter_id = self.get_unique_num100(ids)
                        rate_mbps = self.monitor.metertable[flow]["rate"]
                        self.monitor.metertable[flow]["meter_id2"] = meter_id
                        self.add_meter_entry(dp,meter_id,rate_mbps)
                    print("[Add_meter_entry] meter_id:",self.monitor.metertable[flow]["meter_id"],"rate: ",self.monitor.metertable[flow]["rate"], "flow: ", flow, "dpid-port",(dp.id,dst_port) )                        
                    inst.append(parser.OFPInstructionMeter(meter_id,ofproto.OFPIT_METER))
        mod = parser.OFPFlowMod(datapath=dp, priority=p,
                                idle_timeout=idle_timeout,
                                hard_timeout=hard_timeout,
                                match=match, instructions=inst)
        dp.send_msg(mod)
    
    def add_meter_entry(self, dp, meter_id, rate_mbps):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser

        rate_kbps = int(round(rate_mbps *1.08* 1000))  # convert float Mbps to kbps
        # burst_size = int(round(rate_mbps * 1000/2))  # simple burst setting
        burst_size = 100
        bands = [parser.OFPMeterBandDrop(rate=rate_kbps, burst_size=burst_size)]
        meter_mod = parser.OFPMeterMod(
            datapath=dp,
            command=ofproto.OFPMC_ADD,
            flags=ofproto.OFPMF_KBPS,
            meter_id=meter_id,
            bands=bands)
        dp.send_msg(meter_mod)

    def get_unique_num100(self,ids) :
        mid = random.randint(0,100)
        while mid in ids:
            mid = random.randint(0,100)
        return mid

    def send_group_Table_add(self,datapath_id,flow_info,id_num=5):
        datapath=self.datapaths[datapath_id]
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        port_1=3
        port_2=1
        print 'Y_Y :',flow_info[1],flow_info[2], (flow_info[1],flow_info[2])==('10.0.0.1','10.0.0.3')
        if (flow_info[1],flow_info[2])==('10.0.0.1','10.0.0.3'):
            port_1 = 3
            port_2 = 1
            print "Y_Y"
        
        if flow_info[1] == '10.0.0.2': # src_ip
            port_1 = 1 
            port_2 = 2
            
        actions_1 = [parser.OFPActionOutput(port_1)]
        #port_2 = 1
        actions_2 = [parser.OFPActionOutput(port_2)]
        weight_1 = self.network_commun.grouptable[flow_info[1],flow_info[2]]["out_ratio"]
        weight_2 = self.network_commun.grouptable[flow_info[1],flow_info[2]]["in_ratio"]

        buckets = [
            parser.OFPBucket(weight=weight_1, actions=actions_1),
            parser.OFPBucket(weight=weight_2, actions=actions_2)] 


        group_id = id_num
        req = parser.OFPGroupMod(
            datapath,
            ofp.OFPFC_ADD,
            ofp.OFPGT_SELECT,
            group_id,
            buckets)
        datapath.send_msg(req)
        #only add one times
        self.network_commun.grouptable[flow_info[1],flow_info[2]]["count"]=self.network_commun.grouptable[flow_info[1],flow_info[2]]["count"]+1
    
    def send_group_mod(self,datapath_id,flow_info,group_id=5):
        datapath=self.datapaths[datapath_id]
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(
            in_port=flow_info[3],eth_type=flow_info[0],
            ipv4_src=flow_info[1], ipv4_dst=flow_info[2])     

        actions = [parser.OFPActionGroup(group_id)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=1,
                                idle_timeout=15,flags=ofp.OFPFF_SEND_FLOW_REM,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
    
    def send_flow_mod(self, datapath, flow_info, src_port, dst_port):
        """
            Build flow entry, and send it to datapath.
        """
        parser = datapath.ofproto_parser
        actions = []
        actions.append(parser.OFPActionOutput(dst_port))

        match = parser.OFPMatch(
            in_port=src_port, eth_type=flow_info[0],
            ipv4_src=flow_info[1], ipv4_dst=flow_info[2])
        
        flow = (flow_info[1],flow_info[2]) 
        if flow in self.monitor.metertable.keys():
            # print "add_meter_table! dpid:",datapath.id,"dst_port:",dst_port,"flow: ",flow_info,",limit:", self.monitor.metertable[flow]["rate"]
            self.add_flow(datapath, 1, match, actions,idle_timeout=15, hard_timeout=40,use_meter=True, dst_port=dst_port)
        else:
            self.add_flow(datapath, 1, match, actions,idle_timeout=15, hard_timeout=40)

    def _build_packet_out(self, datapath, buffer_id, src_port, dst_port, data):
        """
            Build packet out object.
        """
        actions = []
        if dst_port:
            actions.append(datapath.ofproto_parser.OFPActionOutput(dst_port))

        msg_data = None
        if buffer_id == datapath.ofproto.OFP_NO_BUFFER:
            if data is None:
                return None
            msg_data = data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=buffer_id,
            data=msg_data, in_port=src_port, actions=actions)
        return out

    def send_packet_out(self, datapath, buffer_id, src_port, dst_port, data):
        """
            Send packet out packet to assigned datapath.
        """
        out = self._build_packet_out(datapath, buffer_id,
                                     src_port, dst_port, data)
        if out:
            datapath.send_msg(out)

    def get_port(self, dst_ip, access_table):
        """
            Get access port if dst host.
            access_table: {(sw,port) :(ip, mac)}
        """
        if access_table:
            if isinstance(access_table.keys()[0], tuple):
                for key in access_table.keys():
                    if dst_ip == key[0]:
                        dst_port = access_table[key][1]			

                        return dst_port
        return None

    def get_port_pair_from_link(self, link_to_port, src_dpid, dst_dpid):
        """
            Get port pair of link, so that controller can install flow entry.
        """
        if (src_dpid, dst_dpid) in link_to_port:
            return link_to_port[(src_dpid, dst_dpid)]
        else:
            self.logger.info("dpid:%s->dpid:%s is not in links" % (
                             src_dpid, dst_dpid))
            return None

    def flood(self, msg):
        """
            Flood ARP packet to the access port
            which has no record of host.
        """
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for dpid in self.awareness.access_ports:
            for port in self.awareness.access_ports[dpid]:
                if (dpid, port) not in self.awareness.access_table.values():
                    datapath = self.datapaths[dpid]
                    out = self._build_packet_out(
                        datapath, ofproto.OFP_NO_BUFFER,
                        ofproto.OFPP_CONTROLLER, port, msg.data)
                    datapath.send_msg(out)
        self.logger.debug("Flooding msg")

    def arp_forwarding(self, msg, src_ip, dst_ip):
        """ Send ARP packet to the destination host,
            if the dst host record is existed,
            else, flow it to the unknow access port.
        """
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        result = self.awareness.get_host_location(dst_ip)
        if result:  # host record in access table.
            datapath_dst, out_port = result[0], result[1]
            datapath = self.datapaths[datapath_dst]
            out = self._build_packet_out(datapath, ofproto.OFP_NO_BUFFER,
                                         ofproto.OFPP_CONTROLLER,
                                         out_port, msg.data)
            datapath.send_msg(out)
            self.logger.debug("Reply ARP to knew host")
        else:
            self.flood(msg)

    def get_path(self, src, dst, weight):
        """
            Get shortest path from network awareness module.
        """
        shortest_paths = self.awareness.shortest_paths
        graph = self.awareness.graph

        if weight == self.WEIGHT_MODEL['hop']:
            return shortest_paths.get(src).get(dst)['hop'][0]
        elif weight == self.WEIGHT_MODEL['delay']:
            # If paths existed, return it, else calculate it and save it.
            try:
                paths = shortest_paths.get(src).get(dst)['delay']
                return paths[0]
            except:
                print "Find new delay path!"
                paths = self.awareness.k_shortest_paths(graph, src, dst,
                                                        weight=weight)

                #shortest_paths.setdefault(src, {})
                #shortest_paths[src].setdefault(dst, paths)
                shortest_paths[src][dst]['delay']=paths
                return paths[0]
        elif weight == self.WEIGHT_MODEL['bw']:
            # Because all paths will be calculate
            # when call self.monitor.get_best_path_by_bw
            # So we just need to call it once in a period,
            # and then, we can get path directly.
            try:
                # if path is existed, return it.
                path = self.monitor.best_paths.get(src).get(dst)['bw']
                return path
            except:
                # else, calculate it, and return.
                result = self.monitor.get_best_path_by_bw(graph,
                                                          shortest_paths)
                paths = result[1]
                best_path = paths.get(src).get(dst)['bw']
                return best_path
    
    def get_sw(self, dpid, in_port, src, dst):
        """
            Get pair of source and destination switches.
        """
        
        src_sw = dpid
        dst_sw = None

        src_location = self.awareness.get_host_location(src)
        if in_port in self.awareness.access_ports[dpid]:
            if (dpid,  in_port) == src_location:
                #print ("dpid= %s , in_port= %s ,src_location",(dpid,in_port,src_location))
                src_sw = src_location[0]
            else:
                #print ("dpid= %s , in_port= %s ,src_location",(dpid,in_port,src_location))
                return None

        dst_location = self.awareness.get_host_location(dst)
        if dst_location:
            dst_sw = dst_location[0]

        return src_sw, dst_sw

    def install_flow(self,num_step, datapaths, link_to_port, access_table, path,
                     flow_info, buffer_id, data=None):
        ''' 
            Install flow entires for roundtrip: go and back.
            @parameter: path=[dpid1, dpid2...]
                        flow_info=(eth_type, src_ip, dst_ip, in_port)
        '''
        if path is None or len(path) == 0:
            self.logger.info("Path error!")
            return
        in_port = flow_info[3]
        first_dp = datapaths[path[0]]
        out_port = first_dp.ofproto.OFPP_LOCAL
        back_info = (flow_info[0], flow_info[2], flow_info[1])

        # inter_link
        if len(path) > 2:
            for i in xrange(1, len(path)-1):
                port = self.get_port_pair_from_link(link_to_port,
                                                    path[i-1], path[i])
                port_next = self.get_port_pair_from_link(link_to_port,
                                                         path[i], path[i+1])
                if port and port_next:
                    src_port, dst_port = port[1], port_next[0]
                    datapath = datapaths[path[i]]
                    self.send_flow_mod(datapath, flow_info, src_port, dst_port)
                    self.send_flow_mod(datapath, back_info, dst_port, src_port)
                    self.logger.debug("inter_link flow install")
        if len(path) > 1:
            # the last flow entry: tor -> host
            port_pair = self.get_port_pair_from_link(link_to_port,
                                                     path[-2], path[-1])
            #print port_pair
            if port_pair is None:
                self.logger.info("Port is not found")
                return
            src_port = port_pair[1]
            if num_step ==1 or num_step ==3: #step 1 is outdoor 
                dst_port=out_door_port[path[-1]]
            else:
                dst_port = self.get_port(flow_info[2], access_table)
            if dst_port is None:
                self.logger.info("Last port is not found.")
                return

            last_dp = datapaths[path[-1]]
            self.send_flow_mod(last_dp, flow_info, src_port, dst_port)
            self.send_flow_mod(last_dp, back_info, dst_port, src_port)

            # the first flow entry
            port_pair = self.get_port_pair_from_link(link_to_port,
                                                     path[0], path[1])
            if port_pair is None:
                self.logger.info("Port not found in first hop.")
                return
            out_port = port_pair[0]
            self.send_flow_mod(first_dp, flow_info, in_port, out_port)
            self.send_flow_mod(first_dp, back_info, out_port, in_port)
            self.send_packet_out(first_dp, buffer_id, in_port, out_port, data)

        # src and dst on the same datapath
        else:
            if num_step ==1 or num_step==3:
                out_port=out_door_port[path[-1]]
            else:
                out_port = self.get_port(flow_info[2], access_table)
            if out_port is None:
                self.logger.info("Out_port is None in same dp")
                return
            self.send_flow_mod(first_dp, flow_info, in_port, out_port)
            self.send_flow_mod(first_dp, back_info, out_port, in_port)
            self.send_packet_out(first_dp, buffer_id, in_port, out_port, data)

    def shortest_forwarding(self, msg, eth_type, ip_src, ip_dst):
        """
            To calculate shortest forwarding path and install them into datapaths.
        """
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        #print self.awareness.access_table#modify
        #print "access_ports :",self.awareness.access_ports
        result = self.get_sw(datapath.id, in_port, ip_src, ip_dst)
	
        if result:
            src_sw, dst_sw = result[0], result[1]
            if dst_sw:
                # Path has already calculated, just get it.
                path = self.get_path(src_sw, dst_sw, weight=self.weight)	
                print("[PATH][DPID]=%s ::%s<-->%s: %s" % (datapath.id,ip_src, ip_dst, path))
                #paths = self.get_path(src_sw, dst_sw, weight='delay')
                #print("[PATH_delay][DPID]=%s ::%s<-->%s: %s" % (datapath.id,ip_src, ip_dst, paths))
                #paths = self.get_path(src_sw, dst_sw, weight='bw')
                #print("[PATH_bw][DPID]=%s ::%s<-->%s: %s" % (datapath.id,ip_src, ip_dst, paths))
                #print("[PATH_bw][DPID]=%s ::%s<-->%s: %s" % (datapath.id,ip_src, ip_dst, paths))
                #print self.monitor.best_paths
                
                flow_info = (eth_type, ip_src, ip_dst, in_port)
                print flow_info
                # install flow entries to datapath along side the path.
                self.install_flow(0,self.datapaths,
                                  self.awareness.link_to_port,
                                  self.awareness.access_table, path,
                                  flow_info, msg.buffer_id, msg.data)
                #self.send_group_mod(1,flow_info,5)
        return

    def alter_path_one(self, msg, eth_type, ip_src, ip_dst):
        """
            To calculate shortest forwarding path and install them into datapaths.
            Send flow to other domains
        """
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
	
        #result = self.get_sw(datapath.id, in_port, ip_src, ip_dst)
        #print "result :",result
        #if result:
        src_sw= datapath.id
        dst_sw=self.network_commun.flow_gateway[(ip_src,ip_dst)][0] # gateway sw to other domain
            #print "flow_gateway: ",self.network_commun.flow_gateway
            #dst_sw=13
        '''
	    if ip_src=='10.0.0.1':
		dst_sw=13
	    if ip_src=='10.0.0.2':
		dst_sw=13
	    if ip_src=='10.0.0.3':
		dst_sw=4
	    if ip_src=='10.0.0.4':
		dst_sw=4
	    print dst_sw
        '''
	    #print "test!!!!!!!!!",self.monitor.freeload_table[(2,3)]
	    #print self.awareness.link_to_port

	    #if ip_src=='10.0.0.1' and ip_dst=='10.0.0.3' and self.monitor.freeload_table[(2,3)]==1:
		#dst_sw=13
        if dst_sw:
                # Path has already calculated, just get it.
                path = self.get_path(src_sw, dst_sw, weight=self.weight)
                print 'src_sw(dpid): ',src_sw,', dst_sw:',dst_sw, ', weight: ', self.weight, ", Path: ",path
                #self.logger.info("[Alter1_PATH]%s<-->%s: %s" % (ip_src, ip_dst, path))

                print ("[Alter1_PATH]%s<-->%s: %s" % (ip_src, ip_dst, path))
                flow_info = (eth_type, ip_src, ip_dst, in_port)
                print flow_info
                # install flow entries to datapath along side the path.
                self.install_flow(1,self.datapaths,
                                  self.awareness.link_to_port,
                                  self.awareness.access_table, path,
                                  flow_info, msg.buffer_id, msg.data)
                                  
        if (ip_src,ip_dst) in self.network_commun.grouptable.keys() : # limiting meter
            print "src_sw(dpid):,", datapath.id,", tmptmp= ",(ip_src,ip_dst),(ip_src,ip_dst) == ('10.0.0.1','10.0.0.3') 
            if (ip_src,ip_dst) == ('10.0.0.1','10.0.0.3') :
                if self.network_commun.grouptable[(ip_src,ip_dst)]["count"]==0: #[40,60,0]
                    self.send_group_Table_add(1,flow_info,5)#dead
                self.send_group_mod(1,flow_info,5)#dead
            if (ip_src,ip_dst) ==('10.0.0.4','10.0.0.2') :
                if self.network_commun.grouptable[(ip_src,ip_dst)]["count"]==0 :
                    self.send_group_Table_add(1,flow_info,6)
                self.send_group_mod(1,flow_info,6)#dead
            if (ip_src,ip_dst) == ('10.0.0.1','10.0.0.6') :
                if self.network_commun.grouptable[(ip_src,ip_dst)]["count"]==0: #[40,60,0]
                    self.send_group_Table_add(1,flow_info,7)#dead
                self.send_group_mod(1,flow_info,7)#dead
            if (ip_src,ip_dst) == ('10.0.0.2','10.0.0.3') :
                if self.network_commun.grouptable[(ip_src,ip_dst)]["count"]==0: #[40,60,0]
                    self.send_group_Table_add(1,flow_info,8)#dead
                self.send_group_mod(1,flow_info,8)#deads
                
        return

    def alter_path_two(self, msg, eth_type, ip_src, ip_dst):
        """
            To calculate shortest forwarding path and install them into datapaths.
            Splited flow to send to original destination.
        """
        print "In alter_path_two"
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
	
        #result = self.get_sw(datapath.id, in_port, ip_src, ip_dst)
        dst_location = self.awareness.get_host_location(ip_dst)
        # src_location = self.awareness.get_host_location(ip_src)
        #print "dst_loc: ",dst_location
        #result:
        # src_sw=self.network_commun.flow_gateway[(ip_src,ip_dst)][0]
        # if datapath.id == self.network_commun.flow_gateway[(ip_src,ip_dst)][1]:
        #     src_sw = self.network_commun.flow_gateway[(ip_src,ip_dst)][1]
        # else:
        #     src_sw = src_location[0]
        src_sw=self.network_commun.flow_gateway[(ip_src,ip_dst)][1]
        dst_sw = dst_location[0]
        print src_sw,dst_sw
        
        """
	    if ip_src=='10.0.0.1':
		src_sw=4
		in_port=4
	    if ip_src=='10.0.0.2':
		src_sw=4
		in_port=4
	    if ip_src=='10.0.0.3':
		src_sw=13
		in_port=2
	    if ip_src=='10.0.0.4':
		src_sw=13
		in_port=2
        
            dst_sw= result[1]
        """
        if dst_sw:
                # Path has already calculated, just get it.
                path = self.get_path(src_sw, dst_sw, weight=self.weight)
                print ""
                #path = self.get_path(src_sw, 3, weight=self.weight)
		
                #self.logger.info("[Alter2_PATH]%s<-->%s: %s" % (ip_src, ip_dst, path))

                print ("[Alter2_PATH], dpid: ",datapath.id, ", %s<-->%s: %s" % (ip_src, ip_dst, path))
                flow_info = (eth_type, ip_src, ip_dst, in_port)
                print flow_info
                # install flow entries to datapath along side the path.
                self.install_flow(2,self.datapaths,
                                  self.awareness.link_to_port,
                                  self.awareness.access_table, path,
                                  flow_info, msg.buffer_id, msg.data)
        return
    def get_new_path_help(self,in_switch,out_switch,leatest_bw):
        shortest_paths = self.awareness.shortest_paths
        graph = self.monitor.graph
        paths=shortest_paths[in_switch][out_switch]['hop']# switch path
        
        best_path=None
        max_bw=0
        path_bw=0
        for i in range(len(paths)):
            path_bw=self.monitor.get_min_bw_of_links(graph,paths[i],setting.MAX_CAPACITY)
            print "path: ",paths[i]," bw= ",path_bw
            if  path_bw>max_bw:#by hop
                max_bw=path_bw
                best_path=i
        if max_bw>leatest_bw:
            print "max_bw :",max_bw, "new path: ", paths[best_path]
            return paths[best_path],True
        else:
            print "new path: ", paths[best_path], "max_bw :",max_bw
            return paths[best_path],False
        
    def do_help(self,msg,eth_type,ip_src,ip_dst):
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        path=self.network_commun.help_other_domain[(ip_src,ip_dst)][2]
        have_higher_bw=False
        # helping others and the helped conjested flow
        if (ip_src,ip_dst) in self.monitor.warning_flow_table.keys():
            path,have_higher_bw=self.get_new_path_help(path[0],path[-1],flow_infos.flow_bw[(ip_src,ip_dst)])
            #change the table path
            if have_higher_bw is False or self.network_commun.help_other_domain[(ip_src,ip_dst)][3]>=1: #second chance or not have_higher_bw
                print "[Do_help]", "not have_higher_bw", "flow help count: ", self.network_commun.help_other_domain[(ip_src,ip_dst)][3] 
                
                if (ip_src,ip_dst) not in self.monitor.metertable.keys(): # have not limit rates yet, limit rate based on weights
                    #congested_flows,target_dpdp = self.monitor.find_congestedlink_flows_and_dpdp((ip_src,ip_dst), self.monitor.flow_change_table)
                    flow =(ip_src,ip_dst)
                    pop_flow = []
                    if CURRENT_MODE == 0:  # 0:PNCFM, 1:MCRM, 2: CFM, 3: Baseline
                        print "Calcualte nbs"
                        self.monitor.nbs_bw_share(flow,pop_flow)
                        print "Set rate limit own own domain flows"
                        self.monitor.process_limit_rate(flow,pop_flow)   
                    elif CURRENT_MODE == 1:
                        print "Set rate limit by profit proportionally"
                        self.monitor.process_limit_rate_by_profit_proportional(flow,pop_flow) 
                        self.network_commun.send_congestion(ip_src,ip_dst,help_bw=self.monitor.metertable[(ip_src,ip_dst)]["rate"])

                    elif CURRENT_MODE == 2: # CFM
                        print "Set no rate limit due to CFM method"
                        pass
                    elif CURRENT_MODE == 3: # Baseline
                        print "shortest_forwarding - Do_help - nothing"

                    #self.network_commun.send_congestion(ip_src,ip_dst,help_bw=self.monitor.metertable[(ip_src,ip_dst)])#dead
                    # other_domain_flow_token = flow_infos.flow_[(ip_src,ip_dst)]
                    
                    # my_domain_flow_token = flow_infos.flow_priority [('10.0.0.5','10.0.0.6')]
                    # self.monitor.metertable[(ip_src,ip_dst)]=int(float(other_domain_flow_token)/(int(other_domain_flow_token)+int(my_domain_flow_token))*10)
                    # self.monitor.metertable[('10.0.0.5','10.0.0.6')]=int(float(my_domain_flow_token)/(int(other_domain_flow_token)+int(my_domain_flow_token))*10)
                    # print 'Y_Y :','10.0.0.5','10.0.0.6',self.monitor.metertable[('10.0.0.5','10.0.0.6')]
                    # print "flow:",(ip_src,ip_dst), ", rate limit: ",self.monitor.metertable[(ip_src,ip_dst)]
                    # self.network_commun.send_congestion(ip_src,ip_dst,help_bw=self.monitor.metertable[(ip_src,ip_dst)])#dead
                    
            elif self.network_commun.help_other_domain[(ip_src,ip_dst)][3]==0:
                self.network_commun.help_other_domain[(ip_src,ip_dst)][3]=self.network_commun.help_other_domain[(ip_src,ip_dst)][3]+1
                #self.monitor.warning_flow_table.pop((ip_src,ip_dst))
                self.network_commun.help_other_domain[(ip_src,ip_dst)][2]=path
                print("Change help path---->Path=",path)
            self.monitor.warning_flow_table.pop((ip_src,ip_dst))
            #self.monitor.warning_flow_table.pop((ip_dst,ip_src))
        
        path=self.network_commun.help_other_domain[(ip_src,ip_dst)][2]
        print ("[DO_Help] %s<-->%s: %s, in_port: %s, dpid: %s" % (ip_src, ip_dst, path, in_port, datapath.id))
        flow_info=(eth_type, ip_src, ip_dst, in_port)
        self.install_flow(3,self.datapaths,
                                  self.awareness.link_to_port,
                                  self.awareness.access_table, path,
                                  flow_info, msg.buffer_id, msg.data)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        '''
            In packet_in handler, we need to learn access_table by ARP.
            Therefore, the first packet from UNKOWN host MUST be ARP.
        '''
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        graph = self.awareness.graph 
        if isinstance(arp_pkt, arp.arp) and (ip_domain[arp_pkt.src_ip] == switch_domain[CONF.ofp_tcp_listen_port] or ip_domain[arp_pkt.dst_ip] == switch_domain[CONF.ofp_tcp_listen_port]):	 
            print "ARP processing: ID= ",datapath.id," ", arp_pkt.src_ip ," to ",arp_pkt.dst_ip
            self.arp_forwarding(msg, arp_pkt.src_ip, arp_pkt.dst_ip)

        '''
        elif isinstance(arp_pkt, arp.arp) and ip_domain[arp_pkt.src_ip]==ip_domain[arp_pkt.dst_ip] and ip_domain[arp_pkt.dst_ip]==1 and switch_domain[CONF.ofp_tcp_listen_port]==2:
            #self.arp_forwarding(msg, arp_pkt.src_ip, arp_pkt.dst_ip)
	    eth_type = pkt.get_protocols(ethernet.ethernet)[0].ethertype
	    self.other_domain_path(msg, eth_type, arp_pkt.src_ip, arp_pkt.dst_ip)
	 
        if isinstance(arp_pkt, arp.arp) and arp_pkt.src_ip=='10.0.0.1' and arp_pkt.dst_ip=='10.0.0.3':
            graph.add_edge(1, 2, weight=10,end=2)
	   
	'''

	

        if isinstance(ip_pkt, ipv4.ipv4):
            self.logger.debug("IPV4 processing")
            if len(pkt.get_protocols(ethernet.ethernet)):
                eth_type = pkt.get_protocols(ethernet.ethernet)[0].ethertype
                flow =(ip_pkt.src,ip_pkt.dst)
                back =(ip_pkt.dst,ip_pkt.src)
                #print "Condition1: ",((ip_pkt.src,ip_pkt.dst) in self.monitor.warning_flow_table.keys())
                #print "Condition2: ",((ip_pkt.src,ip_pkt.dst) in self.network_commun.flow_gateway.keys())
                if  flow in self.network_commun.help_other_domain.keys():
                    self.do_help(msg,eth_type,ip_pkt.src,ip_pkt.dst)#the last is path
                elif  flow  in self.network_commun.flow_gateway.keys(): # flow should exit through gateway and come back
                    print  "IPV4 processing(Do change!!!) ID=",datapath.id," :",ip_pkt.src ," to ",ip_pkt.dst
                    if datapath.id == 2:
                        self.shortest_forwarding(msg, eth_type, ip_pkt.src, ip_pkt.dst)
                    elif datapath.id == self.network_commun.flow_gateway[flow][1]: #back_switch
                        '''
                        note:
                            in network_Communication.py, deal(jsondata)
                                self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])
                                [0]: in_switch
                                [1]: out_switch
                        '''
                        self.alter_path_two(msg, eth_type, ip_pkt.src, ip_pkt.dst) # going back to org domain
                    else:
                        self.alter_path_one(msg, eth_type, ip_pkt.src, ip_pkt.dst) # might break into 2 paths
                        self.alter_path_two(msg, eth_type, ip_pkt.src, ip_pkt.dst) # going back to org domain
        
                elif  flow  in self.monitor.warning_flow_table.keys() :
                    if flow not in self.network_commun.help_list.keys() or (flow in self.network_commun.help_list.keys() and current_time()>self.network_commun.help_list[flow][0]+self.network_commun.help_list[flow][1]):#and back not in self.network_commun.help_list.keys():
                        print  "IPV4 processing(alter) ID=",datapath.id," :",ip_pkt.src ," to ",ip_pkt.dst
                        if CURRENT_MODE == 3: # Nothing
                            self.shortest_forwarding(msg, eth_type, ip_pkt.src, ip_pkt.dst)
                        else:
                            self.network_commun.send_help(out_door[ip_pkt.src],out_door[ip_pkt.dst],ip_pkt.src,ip_pkt.dst,flow_infos.flow_bw[flow],flow_infos.flow_profit[flow], setting.SLICE)
                        # network_commun.send_help(self, in_switch,out_switch,src_ip,dis_ip,max_bw,max_token)
                    else:
                        print  "IPV4 processing(shortest_forwarding) ID= ",datapath.id," :",ip_pkt.src ," to ",ip_pkt.dst
                        self.shortest_forwarding(msg, eth_type, ip_pkt.src, ip_pkt.dst)
                else:
                    print  "IPV4 processing(shortest_forwarding) ID= ",datapath.id," :",ip_pkt.src ," to ",ip_pkt.dst 
                    self.shortest_forwarding(msg, eth_type, ip_pkt.src, ip_pkt.dst)
            #self.network_commun.__help()