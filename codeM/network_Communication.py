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
from time import sleep, time, ctime
import zmq, re
import json
import flow_info

CONF = cfg.CONF
ip_domain={'10.0.0.1':1,'10.0.0.2':1,'10.0.0.3':1,'10.0.0.4':1,'10.0.0.5':2,'10.0.0.6':2,'10.0.0.7':3,'10.0.0.8':3,'10.0.0.9':2,'10.0.0.10':2}
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
                print "send can_help"
                path=self.get_path(jsondata,jsondata['max_bw'],True)
                if path :
                        print("path found, can help, send can help")
                        self.send_can_help(jsondata)
                        self.help_other_domain.setdefault(flow,{})
                        print "self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0]"
                        print "self.help_other_domain[",flow,"]=[" ,gateway_link[jsondata['in_switch']], ", ",gateway_link[jsondata['out_switch']], ",path,0]"
                        self.help_other_domain[flow]=[gateway_link[jsondata['in_switch']],gateway_link[jsondata['out_switch']],path,0]
                        flow_info.flow_priority[flow] = int(jsondata['max_token'])-2
                        flow_info.flow_profit[flow] = round(int(jsondata['max_token']) * 0.7, 4)
                        
        elif jsondata['command'] == 'Help_Reply' :
            if jsondata['Domain'] == switch_domain[CONF.ofp_tcp_listen_port] :
                print "-------------------"
                print "[deal]_Help_Reply"
                self.flow_gateway.setdefault(flow,{})
                print " self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])"
                print "self.flow_gateway[flow]=(", jsondata['in_switch'],",",jsondata['out_switch'], ")"
                self.flow_gateway[flow]=(jsondata['in_switch'],jsondata['out_switch'])
                print "flow_gateway: " ,self.flow_gateway
                print "---------------------"
        elif jsondata['command']=='Congestion_Notify':
            if jsondata['Domain'] == switch_domain[CONF.ofp_tcp_listen_port] and (flow) in self.flow_gateway.keys():
                bw=jsondata['help_bw']
                org_bw = flow_info.flow_bw[flow]
                out_ratio = (1 if bw/org_bw > 1 else bw/org_bw) * 100
                self.grouptable[flow]=[round(out_ratio,4),round(100-out_ratio,4),0] # out_ratio(out of 100), in_ratio, help count
                print "flow", flow, "Split: ", self.grouptable[flow]
                # out_ratio: the percentage of bandwidth help_domain can help
                # in_bw: the  percentage of bandwidth orginal domain needs to handle
                # self.grouptable[flow]=[bw*10,100-bw*10,0] # org code

    def send_can_help(self,data_json):
        data_json_out=json.dumps({"command":"Help_Reply",
        "Domain":data_json['Domain'],
        "in_switch":data_json['in_switch'],
        "out_switch":data_json['out_switch'],
        "src_ip":data_json['src_ip'],
        "dis_ip":data_json['dis_ip'],
        "help_switch_in":7,"help_switch_out":14}, sort_keys=True)#dead
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
        self.server_push_socket.send_string(mes)

    
    def send_help(self,in_switch,out_switch,src_ip,dis_ip,max_bw,max_token):
        '''ask for help'''
        print "==========================="
        print "[send help]"
        print ("network_commun.send_help() triggered, in_switch:", in_switch, "out_switch:", out_switch, "src_ip:", src_ip, "dst_ip:", dis_ip, "max_bw:", max_bw, "max_token:", max_token)
        print "[send help]"
        print "==========================="

        if((src_ip,dis_ip) not in self.help_list.keys()):
            self.help_list.setdefault((src_ip,dis_ip),[1,time()])
        else:
            self.help_list[src_ip,dis_ip][0]=(300 if self.help_list[src_ip,dis_ip][0]>300 else self.help_list[src_ip,dis_ip][0]*2)
            self.help_list[src_ip,dis_ip][1]=time()

        
        data_json=json.dumps({"command":"Help",
        "Domain":switch_domain[CONF.ofp_tcp_listen_port],
        "in_switch":in_switch,
        "out_switch":out_switch,
        "src_ip":src_ip,"dis_ip":dis_ip,'max_bw':max_bw,'max_token':max_token}, sort_keys=True)
        #add topic for xsub
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