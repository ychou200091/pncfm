from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from time import sleep, ctime
from time import time as current_time
import time
import os
from mininet.term import makeTerms
import log.real_bw as real_bw

from algorithms import flow_info

import os
file_path = flow_info.real_bw_log_file_path
c0_port = 6633
c1_port = 6634 
c2_port = 6635
tc_bw=10
try:
    if os.path.isfile(file_path):
        os.remove(file_path)
        print("File deleted.")
    else:
        print("File does not exist.")
except:
    print("File does not exist.")

def MininetTopo():
    real_bw.init()

    simulation_start_time = current_time()
    net = Mininet (topo=None, build=False)

    
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=c0_port)

    c1=net.addController(name='c1',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=c1_port)

    c2=net.addController(name='c2',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=c2_port)


    
    info('Create Switch node\n')
    s1 = net.addSwitch('s1',protocols=["OpenFlow13"],datapath='user')
    s2 = net.addSwitch('s2',protocols=["OpenFlow13"],datapath='user')
    s3 = net.addSwitch('s3',protocols=["OpenFlow13"],datapath='user')
    s4 = net.addSwitch('s4',protocols=["OpenFlow13"],datapath='user')

    s5 = net.addSwitch('s5',protocols=["OpenFlow13"],datapath='user')
    s6 = net.addSwitch('s6',protocols=["OpenFlow13"],datapath='user')
    s7 = net.addSwitch('s7',protocols=["OpenFlow13"],datapath='user')
    s8 = net.addSwitch('s8',protocols=["OpenFlow13"],datapath='user')

    s9 = net.addSwitch('s9',protocols=["OpenFlow13"],datapath='user')
    s10 = net.addSwitch('s10',protocols=["OpenFlow13"],datapath='user')
    s11 = net.addSwitch('s11',protocols=["OpenFlow13"],datapath='user')
    s12 = net.addSwitch('s12',protocols=["OpenFlow13"],datapath='user')

    s13 = net.addSwitch('s13',protocols=["OpenFlow13"],datapath='user')
    s14 = net.addSwitch('s14',protocols=["OpenFlow13"],datapath='user')
    s15 = net.addSwitch('s15',protocols=["OpenFlow13"],datapath='user')
    s16 = net.addSwitch('s16',protocols=["OpenFlow13"],datapath='user')
    s17 = net.addSwitch('s17',protocols=["OpenFlow13"],datapath='user')
    s18 = net.addSwitch('s18',protocols=["OpenFlow13"],datapath='user')    

    info('Create Host node\n')
    h1 = net.addHost('h1', ip='10.0.0.1',mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2',mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3',mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='10.0.0.4',mac='00:00:00:00:00:04')
    h5 = net.addHost('h5', ip='10.0.0.5',mac='00:00:00:00:00:05')
    h6 = net.addHost('h6', ip='10.0.0.6',mac='00:00:00:00:00:06')
    h7 = net.addHost('h7', ip='10.0.0.7',mac='00:00:00:00:00:07')
    h8 = net.addHost('h8', ip='10.0.0.8',mac='00:00:00:00:00:08')
    h9 = net.addHost('h9', ip='10.0.0.9',mac='00:00:00:00:00:09')
    h10= net.addHost('h10', ip='10.0.0.10',mac='00:00:00:00:00:0A')
    h11= net.addHost('h11', ip='10.0.0.11',mac='00:00:00:00:00:0B')
    h12= net.addHost('h12', ip='10.0.0.12',mac='00:00:00:00:00:0C')
    h13= net.addHost('h13', ip='10.0.0.13',mac='00:00:00:00:00:0D')
    h14= net.addHost('h14', ip='10.0.0.14',mac='00:00:00:00:00:0E')
    h15= net.addHost('h15', ip='10.0.0.15',mac='00:00:00:00:00:0F')
    
    info('Add links\n')
    
    #domain 1 switch link
    net.addLink(s1, s2, 1, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s1, s3, 2, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s2, s3, 2, 2,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s2, s4, 3, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    
    #domain 1 host
    net.addLink(s1, h1, 4, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s3, h2, 3, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s4, h3, 5, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s4, h4, 6, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s1, h5, 5, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s4, h6, 7, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s3, h14, 4, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s4, h15, 8, 0,cls=TCLink,bw=tc_bw,use_tbf=True)

    #domain 2 switch link
    net.addLink(s5, s6, 1, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s5, s7, 2, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s7, s8, 2, 2,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s6, s8, 2, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    #net.addLink(s5, s8, 3, 3,bw=10)


    #domain 2 host
    net.addLink(s5, h7, 4, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s6, h8, 4, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s6, h13, 5, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s7, h9, 5, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s8, h10,6, 0,cls=TCLink,bw=tc_bw,use_tbf=True)
    #domain 3 switch link
    net.addLink(s9, s10, 1, 1)
    net.addLink(s9, s11, 2, 1)
    net.addLink(s10, s11, 2, 2)
    net.addLink(s10, s12, 3, 1)
    net.addLink(s11, s12, 3, 2)

    #domain 3 host
    net.addLink(s11, h11, 5, 0)
    net.addLink(s12, h12, 3, 0)
    
    #domain link (D1D2)
    net.addLink(s1, s13, 3, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s13, s7, 2, 3,cls=TCLink,bw=tc_bw,use_tbf=True)
    #modify
    net.addLink(s4, s14, 4, 1,cls=TCLink,bw=tc_bw,use_tbf=True)
    net.addLink(s14, s8, 2, 5,cls=TCLink,bw=tc_bw,use_tbf=True)

    #domain link (D1D3)
    net.addLink(s4, s15, 3, 1,cls=TCLink,bw=tc_bw)
    net.addLink(s15, s9, 2, 3,cls=TCLink,bw=tc_bw)

    net.addLink(s4, s16, 2, 1,cls=TCLink,bw=tc_bw)
    net.addLink(s16, s11, 2, 4,cls=TCLink,bw=tc_bw)

    #domain link (D2D3)
    net.addLink(s6, s17, 3, 1)
    net.addLink(s17, s10, 2, 4)

    net.addLink(s8, s18, 4, 1)
    net.addLink(s18, s9, 2, 4)
    # apply_qdisc_all(net, rate='10mbit', burst='10kb', limit=150) # apply tbf + pfifo to interfaces
    # run_cmd_on_switch_intfs(net)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s4').start([c0])

    net.get('s5').start([c1])
    net.get('s6').start([c1])
    net.get('s7').start([c1])
    net.get('s8').start([c1])
    
    net.get('s9').start([c2])
    net.get('s10').start([c2])
    net.get('s11').start([c2])
    net.get('s12').start([c2])

    net.get('s13').start([c0])
    net.get('s14').start([c1])
    net.get('s15').start([c2])
    net.get('s16').start([c0])
    net.get('s17').start([c2])
    net.get('s18').start([c1])
    
    info( '*** Post configure switches and hosts\n')    
    '''CLI(net)
    net.stop()'''

    for i in range(1,15):
        tmp=net.get('h'+str(i))
        print ('ethtool -K h'+str(i)+'-eth0 tx off')
        tmp.cmd('ethtool -K h'+str(i)+'-eth0 tx off')

    sleep(5)
    if not test_pingall_with_retries(net, retries=3, delay=2):
        net.stop()
        sys.exit(1)  # Exit the program if pingAll fails 3 times
    #p1=h2.cmd('iperf -s -u -i 5 > ./log/'+h2.name+'.out&')
    #h1.popen('iperf -s -u -i 5 >> h1')
    #h6.popen('iperf -s -u -i 5 >> h6')
    #h3.popen('iperf -s -u -i 5 >> h3')
    #h4.popen('iperf -s -u -i 5 >> h4')
    #h5.popen('iperf -s -u -i 5 >> h5') 
    print current_time(),ctime()
    #iperf_single( hosts=(h3,h2), udpBw='9M', period=100, port=5001)
    #sleep(0.5)
    #iperf_single( hosts=(h4,h2), udpBw='9M', period=100, port=5001)
    real_bw.init()
    time_start = current_time()
    log_text =  "[Simulation Starts] Test: %s, %s, Mode: %s" % (flow_info.running_test_num, flow_info.case, flow_info.mode_text[flow_info.CURRENT_MODE]) 
    append_to_log_file(flow_info.file_root,"Assist_congestion_log.txt",log_text)
    iperf_used_ports = []
    while True:
        try:
            cur_time = current_time()
            t = int(cur_time - time_start)
            real_bw.log_bandwidth(real_bw.prev_bytes)
            
            if t%5 == 0:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print "Time : ", t, "Time: ", timestamp

            for flow in flow_info.iperf_flow_info.keys():
                timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                if t == flow_info.iperf_flow_info[flow]["start_time"]:
                    flow_data = flow_info.iperf_flow_info[flow]
                    src = net.get(flow[0])
                    dst = net.get(flow[1])
                    iperf_single( hosts=(src,dst), udpBw=flow_data["bw"], period=flow_data["period"], iperf_used_ports =iperf_used_ports)
                    print flow[0], flow[1],"bw:", flow_data["bw"], "period:",flow_data["period"]
                    real_bw.log_bandwidth(real_bw.prev_bytes, msg = flow[0] + "-" + flow[1])

                    #print "Assist_congestion_log_location: ", flow_info.file_root
                    flow_ip = flow_info.iperf_flow_info[flow]["src_ip"], flow_info.iperf_flow_info[flow]["dst_ip"]
                    log_text = "[Flow_start] Time: %s, flow: %s, bw: %s, profit: %s, duration: %s" % (
                        timestamp_str, flow_ip, flow_info.flow_bw[flow_ip], flow_info.flow_profit[flow_ip],flow_data["period"]
                    )
                    print  log_text
                    append_to_log_file(flow_info.file_root,"Assist_congestion_log.txt", log_text )

            sleep(1)
            if t==flow_info.simulation_end_time:
                break
        except KeyboardInterrupt:
            print("Logging stopped.")
            os.system ("sudo mn -c")
    # play notification sound at the end of simulation
    os.system("ffplay -nodisp -autoexit ringtone.mp3")
    
    CLI(net)
    net.stop()
import random
def iperf_single(hosts=None, udpBw='10M', period=60, port=5001, iperf_used_ports= None):
        """Run iperf between two hosts using UDP.
           hosts: list of hosts; if None, uses opposite hosts
           returns: results two-element array of server and client speeds"""
        if iperf_used_ports == None:
            return 
        assert len( hosts ) == 2
        client, server = hosts
        filename = client.name[1:]+'_'+server.name[1:]+ '.out'
        port = 0
        while True:
            port = random.randint(5000,8000)
            if port not in iperf_used_ports:
                iperf_used_ports.append(port)
                break
        #print( '*** Iperf: testing bandwidth between ' )
        #print( "%s and %s\n" % ( client.name, server.name ) )
        iperfArgs = 'iperf -u '
        bwArgs = '-b ' + udpBw + ' '
        
        ''' command line example
        "iperf -u -s -e -i -5 >> ./log/CHFM/1_3.out&"
        "iperf -u -c 10.0.0.1 -b 10M -i 5 -e -t 60 >> ./log/cleant1_3.out&"
        '''
        server.cmd( iperfArgs +"-s -e -i 5 -p " + str(port)+ " >./log/"+flow_info.log_root+"/"+filename+"&")
        client.cmd( iperfArgs +' -c ' + server.IP() + ' ' + bwArgs +'-i 5'+ ' -e -t '+ str(period) +" -p " + str(port) + '&')
        # client.cmd(
        #     iperfArgs +' -c ' + server.IP() + ' ' + bwArgs
        #     +'-i 5'+ ' -e -t '+ str(period) +' >> ./log/' + 'client' + filename +'&')

def test_pingall_with_retries(net, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        print("\n[INFO] Attempt ",attempt, " of ",retries," - Running pingAll...")
        result = net.pingAll(timeout='1')  # Returns packet loss %
        if result == 0.0:
            print("[SUCCESS] All hosts reachable!")
            return True
        else:
            print("[WARNING] PingAll failed with " ,result,"% packet loss. Retrying in ",delay," seconds...")
            time.sleep(delay)

    print("[ERROR] pingAll failed after multiple retries. Stopping simulation.")
    return False


def append_to_log_file(file_root, filename, content):
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

def apply_tbf_pfifo(iface, rate='10mbit', burst='15kb', limit=1000):
    """
    Apply pfifo inside tbf on the given interface.
    """
    # Delete any existing qdisc
    cmd = "sudo tc qdisc del dev {} root ".format(iface)
    print(cmd)
    os.system(cmd)
    # sudo tc qdisc del dev s1-eth1 root
    # sudo tc qdisc add dev s1-eth1 root handle 1: tbf rate 10mbit burst 15kb limit 1000
    # sudo tc qdisc add dev s1-eth1 parent 1:1 handle 10: pfifo limit 100
    # Apply tbf with pfifo as child qdisc
    # cmd = (
    #     "tc qdisc add dev {iface} root handle 1: tbf rate {rate} burst {burst} limit {limit} && "
    #     "tc qdisc add dev {iface} parent 1:1 handle 10: pfifo limit {limit}"
    # ).format(iface=iface, rate=rate, burst=burst, limit=limit)
    cmd = "sudo tc qdisc add dev {} root handle 1: tbf rate {} burst {} limit {}".format(iface, rate, burst, limit)
    print(cmd)
    os.system(cmd)
    cmd = "sudo tc qdisc add dev {} parent 1:1 handle 10: pfifo limit {}".format(iface, limit)
    print(cmd)
    os.system(cmd)
    
    #os.system(cmd)


def apply_qdisc_all(net, rate='10mbit', burst='15kb', limit=1000):
    """
    Apply tbf+pfifo to all interfaces of all hosts and switches.
    """
    # Hosts
    # for host in net.hosts:
    #     for intf in host.intfNames():
    #         #iface = '{}-{}'.format(host.name, intf)
    #         iface = intf
    #         apply_tbf_pfifo(iface, rate, burst, limit)
    try:
    # Switches
        for switch in net.switches:
            for intf in switch.intfNames():
                #iface = '{}-{}'.format(switch.name, intf)
                iface = intf 
                if  "lo" in iface:
                    continue
                if intf.startswith("s"):
                    # Extract the number after 's', before '-eth'
                    try:
                        sw_num = int(intf[1:].split('-')[0])
                        #print "sw_num: ",sw_num
                        if sw_num >= 13:
                            continue
                    except Exception as e:
                        # in case of any parsing error (shouldn't happen if input is clean)
                        print e
                        continue
                print "intf:", intf
                apply_tbf_pfifo(iface, rate, burst, limit)
    except Exception as e:
        print "Except: ", e

def run_cmd_on_switch_intfs(net, switch_id_limit=13, rate="10mbit", pfifo_limit=100):
    """
    Configure HTB + PFIFO on each switch interface in a Mininet network.
    Only switches with ID <= switch_id_limit are affected.
    
    Commands are executed individually. Output is printed for each step.

    :param net: Mininet network object
    :param switch_id_limit: maximum switch ID to include (default: 13)
    :param rate: bandwidth rate for HTB (e.g., '10mbit')
    :param pfifo_limit: queue size in packets for pfifo
    """
    for sw in net.switches:
        sw_name = sw.name
        try:
            sw_id = int(sw_name[1:])
        except ValueError:
            continue

        if sw_id > switch_id_limit:
            continue

        print("Configuring switch: {}".format(sw_name))

        for intf in sw.intfList():
            iface = str(intf)
            if not iface.startswith(sw_name):
                continue  # skip loopback or unrelated interfaces

            print("  Interface: {}".format(iface))

            cmds = [
                "tc qdisc del dev {} root".format(iface),
                "tc qdisc replace dev {} root handle 1: htb default 1".format(iface),
                "tc class replace dev {} parent 1: classid 1:1 htb rate {}".format(iface, rate),
                "tc qdisc replace dev {} parent 1:1 handle 10: pfifo limit {}".format(iface, pfifo_limit)
            ]

            for cmd in cmds:
                print("  [{}] $ {}".format(sw_name, cmd))
                output = sw.cmd(cmd)
                if output.strip():
                    print("    " + output.strip())

            # Display final qdisc state
            result = sw.cmd("tc -s qdisc show dev {}".format(iface))
            print("  Final qdisc:")
            print(result)


if __name__ == '__main__':
    setLogLevel('info')
    MininetTopo()
