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

from __future__ import division
import copy
from operator import attrgetter
from ryu import cfg
from ryu.base import app_manager
from ryu.base.app_manager import lookup_service_brick
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.lib import hub
from ryu.lib.packet import packet
import setting
import random
from numpy import array
CONF = cfg.CONF
host_loc={(5,4),(6,4),(11,5),(12,3),(7,3),(7,4),(8,4),(6,3),(9,3),(11,4),(10,4),(9,4)}
out_door={13:2,4:4,14:1,7:3,14:1}
ip_domain={'10.0.0.1':1,'10.0.0.2':1,'10.0.0.3':1,'10.0.0.4':1,'10.0.0.5':2,'10.0.0.6':2,'10.0.0.7':3,'10.0.0.8':3,'10.0.0.9':2,'10.0.0.10':2}
switch_domain={6633:1,6634:2,6635:3}
class NetworkMonitor(app_manager.RyuApp):
    """
        NetworkMonitor is a Ryu app for collecting traffic information.
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(NetworkMonitor, self).__init__(*args, **kwargs)
        self.name = 'monitor'
        self.datapaths = {}
        self.port_stats = {}
        self.port_speed = {}
        self.flow_stats = {}
        self.flow_speed = {}
        self.stats = {}
        self.port_features = {}
        self.free_bandwidth = {}
        self.awareness = lookup_service_brick('awareness')
        self.communication = lookup_service_brick('Communication')
        self.graph = None
        self.capabilities = None
        self.best_paths = None
        self.pre_load_table = {} 
        self.load_diff_table = {}
        self.freeload_table = {}
        self.to_calculate = {}
        self.link_load_table = {}
        self.flow_change_table = {}
        self.warning_flow_table = {}
        self.load_loss_table ={}
        # Start to green thread to monitor traffic and calculating
        # free bandwidth of links respectively.
        self.monitor_thread = hub.spawn(self._monitor)
        self.save_freebandwidth_thread = hub.spawn(self._save_bw_graph)
	
    # detects when a swtich connect or disconnect to the controller
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """
            Record datapath's info
        """
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER: # running switch
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER: # dead switch removed from self.datapaths.
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        """
            Main entry method of monitoring traffic.
        """
        while CONF.weight == 'hop':
            self.stats['flow'] = {}
            self.stats['port'] = {}
            for dp in self.datapaths.values():
                self.port_features.setdefault(dp.id, {})
                self._request_stats(dp)
                # refresh data.
                self.capabilities = None
                self.best_paths = None
            hub.sleep(setting.MONITOR_PERIOD)
            if self.stats['flow'] or self.stats['port']:
                self.show_stat('port')
                self.show_stat('flow')
                
                hub.sleep(1)

    def _save_bw_graph(self):
        """
            Save bandwidth data into networkx graph object.
        """
        while CONF.weight == 'hop':
            self.graph = self.create_bw_graph(self.free_bandwidth)
            self.logger.debug("save_freebandwidth")
            hub.sleep(setting.MONITOR_PERIOD)

    def sortedDictValues(self,adict): 
        keys = adict.keys() 
        keys.sort() 
        return map(adict.get, keys) 

    def _request_stats(self, datapath):
        """
            Sending request msg to datapath
        """
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    def get_min_bw_of_links(self, graph, path, min_bw):
        """
            Getting bandwidth of path. Actually, the mininum bandwidth
            of links is the bandwith, because it is the neck bottle of path.
        """
        _len = len(path)
        if _len > 1:
            minimal_band_width = min_bw
            for i in xrange(_len-1):
                pre, curr = path[i], path[i+1]
                if 'bandwidth' in graph[pre][curr]:
                    bw = graph[pre][curr]['bandwidth']
                    minimal_band_width = min(bw, minimal_band_width)
		    
                else:
                    continue
            return minimal_band_width
        return min_bw

    def get_best_path_by_bw(self, graph, paths):
        """
            Get best path by comparing paths.
            1st find paths with smallest number of hops.
            2nd find paths with largest available bandwidth
        """
        capabilities = {}
        best_paths = copy.deepcopy(paths)
        for src in paths:
            for dst in paths[src]:
                if src == dst:
                    best_paths[src][src]['bw'] = [src]
                    capabilities.setdefault(src, {src: setting.MAX_CAPACITY})
                    capabilities[src][src] = setting.MAX_CAPACITY
                    continue
                max_bw_of_paths = 0
                best_path = paths[src][dst]['hop'][0]
                for path in paths[src][dst]['hop']:
                    min_bw = setting.MAX_CAPACITY
                    min_bw = self.get_min_bw_of_links(graph, path, min_bw)
                    if min_bw > max_bw_of_paths:
                        max_bw_of_paths = min_bw
                        best_path = path

                best_paths[src][dst]['bw'] = best_path
                capabilities.setdefault(src, {dst: max_bw_of_paths})
                capabilities[src][dst] = max_bw_of_paths
        self.capabilities = capabilities
        self.best_paths = best_paths
        return capabilities, best_paths

    def create_bw_graph(self, bw_dict):
        """
            Save bandwidth data into networkx graph object.
        """
        try:
            graph = self.awareness.graph
            link_to_port = self.awareness.link_to_port
            for link in link_to_port:
                (src_dpid, dst_dpid) = link
                (src_port, dst_port) = link_to_port[link]
                if src_dpid in bw_dict and dst_dpid in bw_dict:
                    bw_src = bw_dict[src_dpid][src_port]
                    bw_dst = bw_dict[dst_dpid][dst_port]
                    bandwidth = min(bw_src, bw_dst)

                    # add key:value of bandwidth into graph.
                    graph[src_dpid][dst_dpid]['bandwidth'] = bandwidth
                else:
                    graph[src_dpid][dst_dpid]['bandwidth'] = 0
            return graph
        except:
            self.logger.info("Create bw graph exception")
            if self.awareness is None:
                self.awareness = lookup_service_brick('awareness')
            return self.awareness.graph

    def _save_freebandwidth(self, dpid, port_no, speed):
        # Calculate free bandwidth of port and save it.
        port_state = self.port_features.get(dpid).get(port_no)
        if port_state:

            capacity = port_state[2]
            curr_bw = self._get_free_bw(capacity, speed)
            #print "capacity: ",capacity," speed:",speed," curr_bw: ",curr_bw
            self.free_bandwidth[dpid].setdefault(port_no, None)
            self.free_bandwidth[dpid][port_no] = curr_bw
        else:
            self.logger.info("Fail in getting port state")

    def _save_stats(self, _dict, key, value, length):
        if key not in _dict:
            _dict[key] = []
        _dict[key].append(value)

        if len(_dict[key]) > length:
            _dict[key].pop(0)

    def _get_speed(self, now, pre, period):
        if period:
            return (now - pre) / (period)
        else:
            return 0

    def _get_free_bw(self, capacity, speed):
        # BW:Mbit/s
        return max(capacity/10**6 - speed * 8/10**6, 0)

    def _get_time(self, sec, nsec):
        return sec + nsec / (10 ** 9)

    def _get_period(self, n_sec, n_nsec, p_sec, p_nsec):
        return self._get_time(n_sec, n_nsec) - self._get_time(p_sec, p_nsec)



    def register_load_info(self,link_host,dpid,link_port,packet):
        """
            Register access host info into access table.
        """
        #if dpid==13 or dpid==14 or dpid==15 or dpid==16 or dpid==17 or dpid==18:
        #    return	
        #for key in host_loc:
        #   if dpid==key[0] and link_port[1]==key[1]:
        #      return
        key=(link_host,dpid,link_port)
	

        if key in self.pre_load_table and key in self.load_diff_table:
            diff=packet-self.pre_load_table[key]
            if diff<0:
                diff=0#packet

	    
            self.load_diff_table[key] =diff #round((load-self.pre_load_table[(dpid, outport)])*8/(10*1024*1024*12),2)
            self.pre_load_table[key]=packet
            #if dpid==2 and outport==3:
                #self.freeload_table[(dpid, outport)] = 1
            return
          
        else:
            self.pre_load_table.setdefault(key, None)
            self.pre_load_table[key] = packet
	    
            self.load_diff_table.setdefault(key, None)
            self.load_diff_table[key] = packet

            self.sortedDictValues(self.pre_load_table)
            self.sortedDictValues(self.load_diff_table)



        if link_host not in self.load_loss_table:

            self.load_loss_table.setdefault(link_host, None)
            self.load_loss_table[link_host] = 0

            '''
            self.freeload_table.setdefault((dpid, outport), None)
            #if dpid==2 and outport==3:
            #   self.freeload_table[(dpid, outport)] = 1
            #else:
            self.freeload_table[(dpid, outport)] = 0

	    for key in self.awareness.link_to_port:
	    	if (dpid==key[0] and outport==self.awareness.link_to_port[key][0] ) or  (dpid==key[1] and outport==self.awareness.link_to_port[key][1]):
		    print "(dpid, outport):",dpid, outport,"key:",key
		    link=key
		    break

	    if link not in self.link_load_table:
	    	self.link_load_table.setdefault(link, None)
	    	self.link_load_table[link] = 0

	    self.to_calculate.setdefault(link, None)
	    self.to_calculate[link] = 0
	    '''
        return


    def calcu_loss_rate(self):
        for key in  self.load_loss_table:
            #print 'key:',key , (self.communication.help_other_domain) 
            if (key not in self.communication.help_other_domain.keys()) and (ip_domain[key[0]]!=switch_domain[CONF.ofp_tcp_listen_port] or ip_domain[key[1]]!=switch_domain[CONF.ofp_tcp_listen_port]):
                continue
            send_port=self.awareness.get_host_location(key[0])
            recv_port=self.awareness.get_host_location(key[1])
            if key in self.communication.help_other_domain.keys():
                send_port=(7,3)
                recv_port=(14,1)
            if key in self.communication.flow_gateway.keys():
                send_port=(13,1)
                #recv_port=(4,4)
            send_packet=0
            recv_packet=0
            print send_port,recv_port
            for key2 in self.load_diff_table:
                if key2[0]==key:# flow the same 
                    print key2,"diff:",self.load_diff_table[key2]
                    if key2[1]==send_port[0] and key2[2][0]==send_port[1]:#dpid the same and port the same
                        if self.load_diff_table[key2]>send_packet:
                            send_packet=self.load_diff_table[key2]
                    if key2[1]==recv_port[0] and key2[2][1]==recv_port[1]:
                        if self.load_diff_table[key2]>recv_packet:
                            recv_packet=self.load_diff_table[key2]
	
            print "flow:",key,"send_packet:",send_packet,"recv_packet:",recv_packet,'\n'
            if send_packet!=0:
                self.load_loss_table[key]=abs(send_packet-recv_packet)/send_packet
            else:
                self.load_loss_table[key]=0
	

    def set_load_weight(self,flow):
        #if flow in self.communication.help_other_domain:#if change one times the dpid will leave the old rule
        #    return
        for key in self.load_diff_table:
        #    print "KKey: ",key 
            if key[0]==flow:
                link=key[1],key[2][1]
                #print "Link to port :",self.awareness.link_to_port
                for key2 in self.awareness.link_to_port: #key2=> dpid,dpid
        #            print "keyy2: ",key2
                    if (key[1]==key2[0] and key[2][1]==self.awareness.link_to_port[key2][0] ) :#dpid and port to find dpid dpid
                        print "(dpid, outport):",link,"key:",key2
                        if key2 in self.flow_change_table :
                            self.flow_change_table[key2].append((key[0]))
                        else:
                            self.flow_change_table[key2]=list() 
                            self.flow_change_table[key2].append((key[0]))
		    
    def select_the_warningflow(self,flow_change_list):
        '''
        If multiple flows are congested, it randomly selects one.
        Prioritizes flows involved in inter-domain communication.
        '''
        tmp=list(set(flow_change_list).intersection(set(self.communication.help_other_domain.keys())))#if help other warning should selete it
        tmp2=list(set(flow_change_list).intersection(set(self.communication.flow_gateway.keys())))#because the information on dpid will leave should omit it
        if tmp2:
            return 
        if tmp and len(tmp) ==1:
            print 'tmp : ',tmp
            return tmp[0]
        elif tmp and len(tmp)>1:
            k=random.randint(0,len(tmp)-1)
            return tmp[k]
        else:
            if ('10.0.0.1','10.0.0.3') in flow_change_list:
                flow=('10.0.0.1','10.0.0.3')#dead
            if ('10.0.0.4','10.0.0.1') in flow_change_list:
                flow=('10.0.0.4','10.0.0.1')#dead 1
            if ('10.0.0.4','10.0.0.2') in flow_change_list:
                flow=('10.0.0.4','10.0.0.2')#dead 1
            else:
                k=random.randint(0,len(flow_change_list)-1)
                flow=flow_change_list[k]
            return flow
            



    def set_warning_flow(self):
        for key in self.flow_change_table:
            print "link:",key,"values: ",self.flow_change_table[key]," member num:",len(self.flow_change_table[key])

            if len(self.flow_change_table[key])>=2:#only two flow in same dpid_dpid will deal
                print "This link is congestion,the link is",key
                if self.warning_flow_table :#first in is null
                    for key_2 in self.warning_flow_table :#if not impore still select this flow
                        if key_2 in self.flow_change_table[key]:
                            flow=key_2
                            print "still select:",flow

                        else:
                            flow=self.select_the_warningflow(self.flow_change_table[key])
                            #k=random.randint(0,len(self.flow_change_table[key])-1)
                            #flow=self.flow_change_table[key][k]
                            print "select:",flow
                else:
                    #k=random.randint(0,len(self.flow_change_table[key])-1)#random select flow
	            
                    #flow=self.flow_change_table[key][k]
                    flow=self.select_the_warningflow(self.flow_change_table[key])
                    if flow is None:
                        break
                    print "select:",flow

	    
                if flow not in self.warning_flow_table.keys():
                    self.warning_flow_table.setdefault(flow, None)
                    self.warning_flow_table[flow]=1
		    #self.warning_flow_table.setdefault((flow[1],flow[0]), None)
	            #self.warning_flow_table[(flow[1],flow[0])]=1

	



    def record_link_load(self):
        for key in self.link_load_table:
            self.link_load_table[key]=0

        for key in self.load_diff_table:
            for key2 in self.awareness.link_to_port:
                if (key[0]==key2[0] and key[1]==self.awareness.link_to_port[key2][0] ) or  (key[0]==key2[1] and key[1]==self.awareness.link_to_port[key2][1]):
                    self.link_load_table[key2]+=self.load_diff_table[key]
                    break
	
    def set_free_load_table(self,load_mean):
        link_stdev = array([self.link_load_table[key] for key in self.link_load_table.keys()]).std()
        threshold=load_mean+link_stdev
        print "Threshold:",threshold

        for key in self.link_load_table:
            if self.link_load_table[key]>threshold:
                for key2 in self.awareness.link_to_port:
                    if key==key2:
                        self.freeload_table[key[0],self.awareness.link_to_port[key][0]]=1
                        self.freeload_table[key[1],self.awareness.link_to_port[key][1]]=1


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        """
            Save flow stats reply info into self.flow_stats.
            Calculate flow speed and Save it.
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        self.stats['flow'][dpid] = body
        self.flow_stats.setdefault(dpid, {})
        self.flow_speed.setdefault(dpid, {})
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match.get('in_port'),
                                             flow.match.get('ipv4_dst'))):
            #print stat
            #print stat.instructions[-1]
            if isinstance(stat.instructions[-1].actions[0],ev.msg.datapath.ofproto_parser.OFPActionGroup):
                continue

            key = (stat.match['in_port'],  stat.match.get('ipv4_dst'),
                   stat.instructions[-1].actions[0].port)
            
            value = (stat.packet_count, stat.byte_count,
                     stat.duration_sec, stat.duration_nsec)
            self._save_stats(self.flow_stats[dpid], key, value, 5)

            # Get flow's speed.
            pre = 0
            period = setting.MONITOR_PERIOD
            tmp = self.flow_stats[dpid][key]
            if len(tmp) > 1:
                pre = tmp[-2][1]
                period = self._get_period(tmp[-1][2], tmp[-1][3],
                                          tmp[-2][2], tmp[-2][3])

            speed = self._get_speed(self.flow_stats[dpid][key][-1][1],
                                    pre, period)
            self._save_stats(self.flow_speed[dpid], key, speed, 5)


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        """
            Save port's stats info
            Calculate port's speed and save it.
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        self.stats['port'][dpid] = body
        self.free_bandwidth.setdefault(dpid, {})

        for stat in sorted(body, key=attrgetter('port_no')):
            port_no = stat.port_no
            if port_no != ofproto_v1_3.OFPP_LOCAL:
                key = (dpid, port_no)
                value = (stat.tx_bytes, stat.rx_bytes, stat.rx_errors,
                         stat.duration_sec, stat.duration_nsec)

                self._save_stats(self.port_stats, key, value, 5)

                # Get port speed.
                pre = 0
                period = setting.MONITOR_PERIOD
                tmp = self.port_stats[key]
                if len(tmp) > 1:
                    pre = tmp[-2][0] + tmp[-2][1]
                    period = self._get_period(tmp[-1][3], tmp[-1][4],
                                              tmp[-2][3], tmp[-2][4])

                speed = self._get_speed(
                    self.port_stats[key][-1][0] + self.port_stats[key][-1][1],
                    pre, period)

                self._save_stats(self.port_speed, key, speed, 5)
                self._save_freebandwidth(dpid, port_no, speed)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        """
            Save port description info.
        """
        msg = ev.msg
        dpid = msg.datapath.id
        ofproto = msg.datapath.ofproto

        config_dict = {ofproto.OFPPC_PORT_DOWN: "Down",
                       ofproto.OFPPC_NO_RECV: "No Recv",
                       ofproto.OFPPC_NO_FWD: "No Farward",
                       ofproto.OFPPC_NO_PACKET_IN: "No Packet-in"}

        state_dict = {ofproto.OFPPS_LINK_DOWN: "Down",
                      ofproto.OFPPS_BLOCKED: "Blocked",
                      ofproto.OFPPS_LIVE: "Live"}

        ports = []
        for p in ev.msg.body:
            ports.append('port_no=%d hw_addr=%s name=%s config=0x%08x '
                         'state=0x%08x curr=0x%08x advertised=0x%08x '
                         'supported=0x%08x peer=0x%08x curr_speed=%d '
                         'max_speed=%d' %
                         (p.port_no, p.hw_addr,
                          p.name, p.config,
                          p.state, p.curr, p.advertised,
                          p.supported, p.peer, p.curr_speed,
                          p.max_speed))

            if p.config in config_dict:
                config = config_dict[p.config]
            else:
                config = "up"

            if p.state in state_dict:
                state = state_dict[p.state]
            else:
                state = "up"

            port_feature = (config, state, p.curr_speed)
            self.port_features[dpid][p.port_no] = port_feature

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        """
            Handle the port status changed event.
        """
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no
        dpid = msg.datapath.id
        ofproto = msg.datapath.ofproto

        reason_dict = {ofproto.OFPPR_ADD: "added",
                       ofproto.OFPPR_DELETE: "deleted",
                       ofproto.OFPPR_MODIFY: "modified", }

        if reason in reason_dict:

            print "switch%d: port %s %s" % (dpid, reason_dict[reason], port_no)
        else:
            print "switch%d: Illeagal port state %s %s" % (port_no, reason)

    def show_stat(self, type):
        '''
            Show statistics info according to data type.
            type: 'port' 'flow'
        '''
        if setting.TOSHOW is False:
            return

        print "===========Show Stat=========="
        print "send help trigger count: ",self.communication.send_help_count
        bodys = self.stats[type]
        if(type == 'flow'):
            self.flow_change_table.clear()
            #self.warning_flow_table.clear()
	    
            print('datapath         ''   in-port        ip-dst      '
                  'out-port packets  bytes  flow-speed(B/s)')
            print('---------------- ''  -------- ----------------- '
                  '-------- -------- -------- -----------')
            for dpid in bodys.keys():
                for stat in sorted(
                    [flow for flow in bodys[dpid] if flow.priority == 1],
                    key=lambda flow: (flow.match.get('in_port'),
                                      flow.match.get('ipv4_dst'))):
                    #print "stat",stat
                    if isinstance(stat.instructions[-1].actions[0],self.datapaths.values()[0].ofproto_parser.OFPActionGroup):
                        continue
                    print('%016d %8x %17s %8x %8d %8d %8.1f' % (
                        dpid,
                        stat.match['in_port'],
                        stat.match['ipv4_dst'],
                        stat.instructions[-1].actions[0].port,
                        stat.packet_count, stat.byte_count,
                        abs(self.flow_speed[dpid][(stat.match.get('in_port'),stat.match.get('ipv4_dst'),stat.instructions[-1].actions[0].port)][-1])))

                    link_host=stat.match.get('ipv4_src'),stat.match.get('ipv4_dst')
                    link_port=stat.match['in_port'],stat.instructions[-1].actions[0].port
                    self.register_load_info(link_host,dpid,link_port,stat.packet_count)


                    '''
                    if stat.byte_count>0:
                    if key in self.freeload_table :
                            if self.freeload_table[key]==1 :
                            print stat.match['ipv4_src'],stat.match['ipv4_dst'],"should warning"
                        for key2 in self.awareness.link_to_port:
                                if (key[0]==key2[0] and key[1]==self.awareness.link_to_port[key2][0] ) or  (key[0]==key2[1] and key[1]==self.awareness.link_to_port[key2][1]):
                            link_key=key2
                            break





                        if link_key not in self.flow_change_table:
                            self.flow_change_table[link_key]=list()
                        self.flow_change_table[link_key].append((stat.match['ipv4_src'],stat.match['ipv4_dst']))

                        #self.flow_change_table.append((stat.match['ipv4_src'],stat.match['ipv4_dst'],key))
                    '''
            '''
            print self.flow_change_table
            if self.flow_change_table:
                self.set_warning_flow()
            else:
                self.warning_flow_table.clear()

            '''
		
            self.calcu_loss_rate()

            if self.load_loss_table:
                for key in self.load_loss_table:
                    # print "flow:",key,"loss_rate:",self.load_loss_table[key]
                    if self.load_loss_table[key]>0.2 and  self.load_loss_table[key]<1.0:
                        self.set_load_weight(key)#set flow change
                        self.set_warning_flow()#set warning on flow change
			
            if self.flow_change_table:
                for key2 in self.flow_change_table:
                    print 'flow_change_table:', key2,self.flow_change_table[key2]
            #for test
            if ('10.0.0.2','10.0.0.4') in self.warning_flow_table :
                    self.warning_flow_table.pop(('10.0.0.2','10.0.0.4'))#bug the table speed not update
            print "The warning_flow_table:",self.warning_flow_table,'\n'

            print '\n'

        '''if(type == 'port'):


            print('datapath             port   ''rx-pkts  rx-bytes rx-error '
                  'tx-pkts  tx-bytes tx-error  port-speed(B/s)'
                  ' current-capacity(Kbps)  '
                  'port-stat   link-stat')
            print('----------------   -------- ''-------- -------- -------- '
                  '-------- -------- -------- '
                  '----------------  ----------------   '
                  '   -----------    -----------')
	    
            format = '%016x %8x %8d %8d %8d %8d %8d %8d %8.1f %16d %16s %16s'
	    
            for dpid in bodys.keys():
                for stat in sorted(bodys[dpid], key=attrgetter('port_no')):
                    if stat.port_no != ofproto_v1_3.OFPP_LOCAL:
			
                        print(format % (
                            dpid, stat.port_no,
                            stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                            stat.tx_packets, stat.tx_bytes, stat.tx_errors,
                            abs(self.port_speed[(dpid, stat.port_no)][-1]),
                            self.port_features[dpid][stat.port_no][2],
                            self.port_features[dpid][stat.port_no][0],
                            self.port_features[dpid][stat.port_no][1]))
'''
'''			
			self.register_load_info(dpid, stat.port_no,stat.rx_bytes)

			
	    
	    domain_all_load=0
	    load_var=0

	    self.record_link_load()
	    
	    
	    for key in self.load_diff_table.keys():
		domain_all_load+=self.load_diff_table[key]
		
		print "key:",key,self.load_diff_table[key],self.freeload_table[key]
	    
	    load_mean=array([self.link_load_table[key] for key in self.link_load_table.keys()]).mean()
	    

	    for key in self.to_calculate.keys():
		self.to_calculate[key]=(abs(load_mean-self.link_load_table[key]))**2
	    load_var=array([self.to_calculate[key] for key in self.to_calculate.keys()]).mean()
	    print "load_mean:",load_mean,"load_var:",load_var

	    for key in self.load_diff_table.keys():
	        print "(dpid,port):",key,self.load_diff_table[key]

	    for key in self.link_load_table.keys():
		print "link:",key,self.link_load_table[key]

	    for key in self.freeload_table.keys():
	        self.freeload_table[key]=0

	    if load_var>0.25:
		self.set_free_load_table(load_mean)

	    for key in self.freeload_table.keys():
		print  "(dpid,port):",key,self.freeload_table[key]

	    """

            print '\n'
	'''
