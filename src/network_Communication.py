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
from ryu.lib import hub
from ryu.base.app_manager import lookup_service_brick
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
import setting
from ryu.lib.packet import ether_types
from ryu.lib.packet import  in_proto as inet

import time
import zmq, re, os
import json
import flow_info

CURRENT_MODE = flow_info.CURRENT_MODE
CONF = cfg.CONF
ip_domain = flow_info.ip_domain
switch_domain={6633:1,6634:2,6635:3}
out_door={(1,2):(13,2)}
XSub_port=9089
XPub_port=9090
gateway_link={13:7,4:14,14:4,7:13}
gateway_domain={13:1,4:1,7:2,14:2}

#     pub pub pub pub
#   
#          xsub
#         proxy
#          xpub
#
#     sub sub sub sub
class Controller_Communication(app_manager.RyuApp):
    #server_push_socket
    #client_push_socket
    def __init__(self, *args, **kwargs):
        
        super(Controller_Communication, self).__init__(*args, **kwargs)
        self.name="Communication"
        #look other methon
        self.awareness = lookup_service_brick('awareness')
        self.monitor = lookup_service_brick('monitor')
        #self.monitor = lookup_service_brick('monitor')
        #for send and recv socket
        self.server_push_socket = self.get_publisher('127.0.0.1', XSub_port)
        self.client_pull_socket = self.get_subscriber('127.0.0.1', XPub_port, "test")
        self.listen_ = hub.spawn(self.listen)
        self.topic="test"
        self.weight = "hop"
        self.flow_gateway={} #flow send to gateway
        self.help_list={}#too many the same flow which is send
        self.help_other_domain={} # value of each key is a list.
            # help_other_domain[flow]=[
            #   [0]: gateway_link[jsondata['in_switch']],
            #   [1]: gateway_link[jsondata['out_switch']],
            #   [2]: path,
            #   [3]: 0]
        self.grouptable={}
        self.weight_flow={}
        #self.grouptable[('10.0.0.1','10.0.0.3')]=[40,60]
        #self.listen()
        
    def listen(self):
        """
            Main entry method of monitoring traffic.
        """
        #poller
        self.poller = zmq.Poller()
        self.poller.register(socket=self.server_push_socket, flags=zmq.POLLOUT)
        self.poller.register(socket=self.client_pull_socket, flags=zmq.POLLIN)
        #noblock for recv message
        while True:
            events = dict(self.poller.poll(1000))
            if self.client_pull_socket in events:
                message = self.client_pull_socket.recv_multipart()
                print("subscription message: {}".format(message[0]))
                jsondata=json.loads(message[0].split(',',1)[1])
               # print "jsondata: ",jsondata
                self.deal(jsondata)
            
            hub.sleep(1)
    def get_path(self,jsondata,max_bw,token):
        shortest_paths = self.awareness.shortest_paths
        graph = self.awareness.graph
        paths=shortest_paths[gateway_link[jsondata['in_switch']]][gateway_link[jsondata['out_switch']]]['hop']# switch path
        print "Finding paths for:"
        print "\t src_ip:",jsondata['src_ip'],"dis_ip:",jsondata['dis_ip'], "jsondata['in_switch']: ", jsondata['in_switch'], "jsondata['out_switch']: ",jsondata['out_switch']
        print "Found paths: \n\t", paths
        best_path=None
        for path in paths:
            if self.get_min_bw_of_links(graph,path,setting.MAX_CAPACITY)>=max_bw:#by hop
                best_path=path
                print "can_help_bw: ",self.get_min_bw_of_links(graph,path,setting.MAX_CAPACITY)," ",path
                break
            print "can_help_bw: ",self.get_min_bw_of_links(graph,path,setting.MAX_CAPACITY)," ",path
        return best_path
   
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

    def deal(self,jsondata):#help_other_domain[flow][in_switch,out_switch,path,times(second chance)] i'm lazy.
        flow =(jsondata['src_ip'],jsondata['dis_ip'])     

        if jsondata['command'] =='Help' :
            print "------------------------------"
            print "receive Help msg. ", "\tswitch_domain[CONF.ofp_tcp_listen_port]= ",switch_domain[CONF.ofp_tcp_listen_port] 
            print "gateway_domain[gateway_link[jsondata['in_switch']]]: ",gateway_domain[gateway_link[jsondata['in_switch']]]
            print "gateway_domain[gateway_link[jsondata['in_switch']]]== switch_domain[CONF.ofp_tcp_listen_port]: ",gateway_domain[gateway_link[jsondata['in_switch']]]== switch_domain[CONF.ofp_tcp_listen_port]
            # print "domain, ",gateway_domain[gateway_link[jsondata['in_switch']]]== switch_domain[CONF.ofp_tcp_listen_port]  , "  ",gateway_domain[gateway_link[jsondata['out_switch']]]
            print "jsondata['in_switch']: ", jsondata['in_switch']
            print "gateway_link[jsondata['in_switch']]", gateway_link[jsondata['in_switch']]
            print "gateway_domain[gateway_link[jsondata['in_switch']]], ", gateway_domain[gateway_link[jsondata['in_switch']]] 
            # domains the flow is "coming from" and "going to" should be the same.
            if gateway_domain[gateway_link[jsondata['in_switch']]] == switch_domain[CONF.ofp_tcp_listen_port] and gateway_domain[gateway_link[jsondata['out_switch']]] == switch_domain[CONF.ofp_tcp_listen_port]:
                path=self.get_path(jsondata,jsondata['max_bw'],True)
                if CURRENT_MODE == 0: # ProfitNBS
                    if path :
                        print "send can_help"

                        bw = jsondata['max_bw']
                        profit = jsondata['max_token']
                        s = jsondata['slice']
                        
                        print("path found, can help, send can help")
                        self.send_can_help(jsondata)
                        self.help_other_domain.setdefault(flow,{})
                        print "self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0]"
                        print "self.help_other_domain[",flow,"]=[" ,gateway_link[jsondata['in_switch']], ", ",gateway_link[jsondata['out_switch']], ",",path,"0]"
                        self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0, s ,bw, profit]
                        in_sw = gateway_link[jsondata['in_switch']]
                        out_sw = gateway_link[jsondata['out_switch']]
                        self.awareness.update_in_out_sw(flow,in_sw,out_sw) # 7,14
                        flow_info.flow_profit[flow] = int(jsondata['max_token']) 
                if CURRENT_MODE == 1: # MCRM
                    if path :
                        print "send can_help"

                        bw = jsondata['max_bw']
                        profit = jsondata['max_token']
                        s = jsondata['slice']
                        
                        print("path found, can help, send can help")
                        self.send_can_help(jsondata)
                        self.help_other_domain.setdefault(flow,{})
                        print "self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0]"
                        print "self.help_other_domain[",flow,"]=[" ,gateway_link[jsondata['in_switch']], ", ",gateway_link[jsondata['out_switch']], ",",path,"0]"
                        self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0, s ,bw, profit]
                        in_sw = gateway_link[jsondata['in_switch']]
                        out_sw = gateway_link[jsondata['out_switch']]
                        self.awareness.update_in_out_sw(flow,in_sw,out_sw) # 7,14
                        flow_info.flow_profit[flow] = int(jsondata['max_token']) 
                    else:  # path not found
                        print "send can_help with bw = 0"
                        jsondata['max_bw'] = 0
                        
                        profit = jsondata['max_token']
                        s = jsondata['slice']
                        
                        print("path not found, send can help")
                        self.send_can_help(jsondata)
                        self.help_other_domain.pop(flow,None)
                if CURRENT_MODE == 2: # CFM
                    if path :
                        print "send can_help"

                        bw = jsondata['max_bw']
                        profit = jsondata['max_token']
                        s = jsondata['slice']
                        
                        print("path found, can help, send can help")
                        self.send_can_help(jsondata)
                        self.help_other_domain.setdefault(flow,{})
                        print "self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0]"
                        print "self.help_other_domain[",flow,"]=[" ,gateway_link[jsondata['in_switch']], ", ",gateway_link[jsondata['out_switch']], ",",path,"0]"
                        self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0, s ,bw, profit]
                        in_sw = gateway_link[jsondata['in_switch']]
                        out_sw = gateway_link[jsondata['out_switch']]
                        self.awareness.update_in_out_sw(flow,in_sw,out_sw) # 7,14
                        flow_info.flow_profit[flow] = int(jsondata['max_token']) 
                if CURRENT_MODE == 3: # Nothing
                    print "shortest_forwarding - deal _help_other_domain - nothing"
                
        elif jsondata['command'] == 'Help_Reply' :
            if jsondata['Domain'] == switch_domain[CONF.ofp_tcp_listen_port] :
                if CURRENT_MODE == 0: # ProfitNBS, CFM
                    print "-------------------"
                    print "[deal]_Help_Reply"
                    self.flow_gateway.setdefault(flow,{})
                    print " self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])"
                    print "self.flow_gateway[flow]=(", jsondata['in_switch'],",",jsondata['out_switch'], ")"
                    self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])
                    print "flow_gateway: " ,self.flow_gateway
                    print "---------------------"

                    self.help_reply_reroute(flow, jsondata['in_switch'],jsondata['out_switch'],jsondata['help_switch_out'], jsondata['help_switch_in'] )
                if CURRENT_MODE == 1: #MCRM
                    
                    print "-------------------"
                    print "[deal]_Help_Reply"
                    print " self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])"
                    print "self.flow_gateway[flow]=(", jsondata['in_switch'],",",jsondata['out_switch'], ")"
                    if jsondata['help_bw'] == 0: 
                        print "[Help_Reply] Help bandwidth is 0, can't help"
                        bw=jsondata['help_bw']
                        if flow in self.grouptable.keys():
                            org_bw = self.grouptable[flow]["org_bw"]
                            out_ratio = (1 if bw/org_bw > 1 else bw/org_bw) * 100
                            self.grouptable[flow]["out_ratio"]= round(out_ratio,4)
                            self.grouptable[flow]["in_ratio"]= round(100-out_ratio,4)
                            self.grouptable[flow]["count"] = 0
                        
                        else:
                            org_bw = flow_info.flow_bw[flow]
                            out_ratio = (1.0 if bw/org_bw > 1 else bw/org_bw) * 100
                            
                            self.grouptable[flow]={
                                "out_ratio": round(out_ratio,4), "in_ratio": round(100-out_ratio,4), 
                                "count":0, "org_bw": flow_info.flow_bw[flow], "org_profit": flow_info.flow_profit[flow]
                            }

                        if self.monitor == None:
                            self.monitor = lookup_service_brick('monitor')

                        self.monitor.process_limit_rate_by_profit_proportional(flow,[])
                        return 
                    else:
                        self.flow_gateway.setdefault(flow,{})
                        self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])
                        print "flow_gateway: " ,self.flow_gateway
                        print "---------------------"

                        self.help_reply_reroute(flow, jsondata['in_switch'],jsondata['out_switch'],jsondata['help_switch_out'], jsondata['help_switch_in'] )

                elif CURRENT_MODE == 2: # CFM
                    print "-------------------"
                    print "[deal]_Help_Reply"
                    print " self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])"
                    print "self.flow_gateway[flow]=(", jsondata['in_switch'],",",jsondata['out_switch'], ")"
                    if jsondata['help_bw'] == 0:  # CFM can't limit rate
                        return 
                    
                    self.flow_gateway.setdefault(flow,{})
                    self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])
                    print "flow_gateway: " ,self.flow_gateway
                    print "---------------------"

                    self.help_reply_reroute(flow, jsondata['in_switch'],jsondata['out_switch'],jsondata['help_switch_out'], jsondata['help_switch_in'] )
                elif CURRENT_MODE == 3: # Nothing
                    pass

        elif jsondata['command']=='Congestion_Notify':
            if jsondata['Domain'] == switch_domain[CONF.ofp_tcp_listen_port] and (flow) in self.flow_gateway.keys():
                bw=jsondata['help_bw']
                if flow in self.grouptable.keys():
                    org_bw = self.grouptable[flow]["org_bw"]
                    out_ratio = (1 if bw/org_bw > 1 else bw/org_bw) * 100
                    self.grouptable[flow]["out_ratio"]= round(out_ratio,4)
                    self.grouptable[flow]["in_ratio"]= round(100-out_ratio,4)
                    self.grouptable[flow]["count"] = 0
                
                else:
                    org_bw = flow_info.flow_bw[flow]
                    out_ratio = (1.0 if bw/org_bw > 1 else bw/org_bw) * 100
                    
                    self.grouptable[flow]={
                        "out_ratio": round(out_ratio,4), "in_ratio": round(100-out_ratio,4), 
                        "count":0, "org_bw": flow_info.flow_bw[flow], "org_profit": flow_info.flow_profit[flow]
                    }

                if self.monitor == None:
                    self.monitor = lookup_service_brick('monitor')

                self.monitor.delete_flows_by_ip_pair(flow[0],flow[1])

                # org_bw = flow_info.flow_bw[flow]
                # out_ratio = (1 if bw/org_bw > 1 else bw/org_bw) * 100
                # self.grouptable[flow]=[round(out_ratio,4),round(100-out_ratio,4),0] # out_ratio(out of 100), in_ratio, help count
                
                print "flow", flow, "Split: ", self.grouptable[flow]
                # self.help_reply_reroute(flow, jsondata['in_switch'],jsondata['out_switch'])
                # out_ratio: the percentage of bandwidth help_domain can help
                # in_bw: the  percentage of bandwidth orginal domain needs to handle
                # self.grouptable[flow]=[bw*10,100-bw*10,0] # org code

    def send_can_help(self,data_json):
        print "Inside send_can_help, data_json: ",data_json
        data_json_out=json.dumps({"command":"Help_Reply",
        "Domain":data_json['Domain'],
        "in_switch":data_json['in_switch'],
        "out_switch":data_json['out_switch'],
        "src_ip":data_json['src_ip'],
        "dis_ip":data_json['dis_ip'],
        "help_switch_in":7,"help_switch_out":14, 
        "help_bw":data_json['max_bw']}, sort_keys=True)#dead
        mes=str(self.topic)+","+data_json_out
        print "mes: ",mes
        self.server_push_socket.send_string(mes)

    def send_congestion(self,src_ip,dst_ip,help_bw,domain=1):
        data_json_out=json.dumps({"command":"Congestion_Notify",
        "Domain":domain,
        "in_switch":gateway_link[self.help_other_domain[(src_ip,dst_ip)][0]],
        "out_switch":gateway_link[self.help_other_domain[(src_ip,dst_ip)][1]],
        "src_ip":src_ip,
        "dis_ip":dst_ip,
        "help_bw":help_bw}, sort_keys=True)#dead
        mes=str(self.topic)+","+data_json_out
        print "mes: ",mes

        # store status in log
        if CURRENT_MODE == 0: # only for PNCFM
            flow = (src_ip,dst_ip)
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print "Assist_congestion_log_location: ", flow_info.file_root
            # log_text = "Time : ", timestamp_str, ",flow:",  flow,",help_bw:", help_bw, ",org_profit:", flow_info.flow_profit[flow]
            log_text = "[Congestion_Notify]Time: %s, flow: %s, help_bw: %s, org_profit: %s, slice: %s" % (
                timestamp_str, flow, help_bw, flow_info.flow_profit[flow], setting.SLICE
            )
            print log_text
            self.append_to_log_file(flow_info.file_root,"Assist_congestion_log.txt", log_text )
        
        self.server_push_socket.send_string(mes)

    def append_to_log_file(self,file_root, filename, content):
        """
        Append a string to a text file. Create the file if it does not exist.

        Parameters:
            file_root (str): The directory where the file is located or will be created.
            filename (str): The name of the text file (e.g., 'log.txt').
            content (str): The string to append to the file.
        """
        # Ensure the directory exists (Python 2 compatible)
        if not os.path.exists(file_root):
            os.makedirs(file_root)
        file_path = os.path.join(file_root, filename)
        # Use binary mode to ensure consistency across Python 2
        with open(file_path, 'ab') as f:
            f.write(content + '\n')


    def send_help(self,in_switch,out_switch,src_ip,dis_ip,max_bw,max_token,s):
        '''ask for help'''
        print "==========================="
        print "[send help]"
        print ("network_commun.send_help() triggered, in_switch:", in_switch, "out_switch:", out_switch, "src_ip:", src_ip, "dst_ip:", dis_ip, "max_bw:", max_bw, "max_token:", max_token)
        print "[send help]"
        print "==========================="
        if CURRENT_MODE == 3: #Nothing
            return 
        if((src_ip,dis_ip) not in self.help_list.keys()):
            self.help_list.setdefault((src_ip,dis_ip),[5,time.time()])
        else:
            self.help_list[src_ip,dis_ip][0]=(300 if self.help_list[src_ip,dis_ip][0]>300 else self.help_list[src_ip,dis_ip][0]*2)
            self.help_list[src_ip,dis_ip][1]=time.time()

        
        data_json=json.dumps({"command":"Help",
        "Domain":switch_domain[CONF.ofp_tcp_listen_port],
        "in_switch":in_switch,
        "out_switch":out_switch,
        "src_ip":src_ip,"dis_ip":dis_ip,'max_bw':max_bw,
        'max_token':max_token, "slice":s}, sort_keys=True)
        # add topic for xsub
        mes=str(self.topic)+","+data_json
        print "mes: ",mes
        self.server_push_socket.send_string(mes)


    def get_publisher(self,address, port):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        connect_addr = 'tcp://%s:%s' % (address, port)
        socket.connect(connect_addr)
        return socket

    def get_subscriber(self,address, port, topics):
	    # Subscriber can register one more topics once
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        connect_addr = 'tcp://%s:%s' % (address, port)
        socket.connect(connect_addr)
        if isinstance(topics, str):
            socket.subscribe(topics)
        elif isinstance(topics, list):
            [socket.subscribe(topic) for topic in topics]
        return socket
         
         
    def normalize_to_mbps(s):
        match = re.match(r'(\d+)([mM])', s)
        if not match:
            raise ValueError("Invalid format: {}".format(s))
        value, unit = match.groups()
        value = int(value)
        return value * 8 if unit == 'M' else value
    
    def help_reply_reroute(self, flow, in_switch ,out_switch,help_switch_out,help_switch_in ):
        """
            To calculate shortest forwarding path and install them into datapaths.
            when help reply triggered, install flow to refreash.
            in_swtich: flow is going into a differ domain with sw
            help_switch_out: flow is going into a differ domain with sw
            out_switch: flow exist help domain with this switch
            help_switch_in: flow exist help domain with this switch


        """ 
        print " link_to_port",  self.awareness.link_to_port
        
        # route flow to domain in-gateway in_switch,
        # accept flow domain out-gateway out_switch
        src_ip, dst_ip = flow
        
        if self.monitor is None:
            self.monitor = lookup_service_brick('monitor')
        src_sw = self.awareness.get_host_location(src_ip)[0]
        dst_sw = in_switch
        path = self.get_path_src_dst_hop(src_sw, dst_sw, weight=self.weight)
        print "path", path
        if path == None:
            print "ERROR: NO PATH"

        if len(path) == 1: # sw is gateway switch
            nxt_sw = gateway_link[path[0]]
        else:
            nxt_sw = path[1]

        dp = self.monitor.datapaths[src_sw]
        try:
            dp2= self.monitor.datapaths[nxt_sw]
        except:
            dp2 = None


        ofproto = dp.ofproto
        parser = dp.ofproto_parser

        access_table = self.awareness.access_table
        link_to_port = self.awareness.link_to_port
        #print "link_to_port"
        #print link_to_port
        # get in-port
        for ip,mac in access_table:
            # print ("src_ip %s, ip %s,mac %s, sw %s, in_port %s" %(flow[0] ,ip, mac,sw,in_port))
            if ip == src_ip :
                in_port = access_table[(ip,mac)][1] 
                break
        if in_port == None:
            print "error No in-port find"

        if src_sw == 4 and nxt_sw == 14:
            out_port = 4
        # if src_sw == 6 and nxt_sw == 17:
        #     out_port = 3
        # if src_sw == 9 and nxt_sw == 18:
        #     out_port = 4 
        else:
            out_port = link_to_port[(src_sw,nxt_sw)][0]
        print 'src_sw(dpid): ',src_sw,', dst_sw:',dst_sw,"out-p",out_port ,', weight: ', self.weight, ", Path: ",path
        print ("[Alter1_PATH]%s<-->%s: %s" % (src_ip, dst_ip, path))
        flow_info = (0x0800,src_ip, dst_ip, in_port)
        
        
        if path is None or len(path) == 0:
            self.logger.info("Path error!")
            return

        parser = dp.ofproto_parser
        actions = []
        actions.append(parser.OFPActionOutput(out_port))

        
        match = parser.OFPMatch(
            in_port=in_port, eth_type=0x0800,
            ipv4_src=src_ip, ipv4_dst=dst_ip )
        print "simple_add_flow", "flow", flow, "in-out-port",(in_port, out_port), "dpid:",src_sw, dp.id
        self.simple_add_flow(dp,1,match,actions,2,2)
        match = parser.OFPMatch(
            in_port=out_port, eth_type=0x0800,
            ipv4_src=dst_ip, ipv4_dst= src_ip)
        if dp2:
            self.simple_add_flow(dp2,1,match,actions,2,2)

    def simple_add_flow(self, dp, p, match, actions, idle_timeout=15, hard_timeout=15):
        """
            Send a flow entry to datapath.
        """
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        mod = parser.OFPFlowMod(datapath=dp, priority=p,
                                idle_timeout=idle_timeout,
                                hard_timeout=hard_timeout,
                                match=match, instructions=inst)
        dp.send_msg(mod)

    

    def get_path_src_dst_hop(self, src, dst, weight):
        """
            Get shortest path from network awareness module.
        """
        shortest_paths = self.awareness.shortest_paths
        graph = self.awareness.graph

        
        return shortest_paths.get(src).get(dst)['hop'][0]
