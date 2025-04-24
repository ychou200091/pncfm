
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from time import sleep, time, ctime

def MininetTopo():
    net = Mininet (topo=None, build=False)

    
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=6633)

    c1=net.addController(name='c1',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=6634)

    c2=net.addController(name='c2',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=6635)


    
    info('Create Switch node\n')
    s1 = net.addSwitch('s1',protocols=["OpenFlow13"],datapath='kernel')
    s2 = net.addSwitch('s2',protocols=["OpenFlow13"],datapath='kernel')
    s3 = net.addSwitch('s3',protocols=["OpenFlow13"],datapath='kernel')
    s4 = net.addSwitch('s4',protocols=["OpenFlow13"],datapath='kernel')

    s5 = net.addSwitch('s5',protocols=["OpenFlow13"],datapath='kernel')
    s6 = net.addSwitch('s6',protocols=["OpenFlow13"],datapath='kernel')
    s7 = net.addSwitch('s7',protocols=["OpenFlow13"],datapath='kernel')
    s8 = net.addSwitch('s8',protocols=["OpenFlow13"],datapath='kernel')

    s9 = net.addSwitch('s9',protocols=["OpenFlow13"],datapath='kernel')
    s10 = net.addSwitch('s10',protocols=["OpenFlow13"],datapath='kernel')
    s11 = net.addSwitch('s11',protocols=["OpenFlow13"],datapath='kernel')
    s12 = net.addSwitch('s12',protocols=["OpenFlow13"],datapath='kernel')

    s13 = net.addSwitch('s13',protocols=["OpenFlow13"],datapath='kernel')
    s14 = net.addSwitch('s14',protocols=["OpenFlow13"],datapath='kernel')
    s15 = net.addSwitch('s15',protocols=["OpenFlow13"],datapath='kernel')
    s16 = net.addSwitch('s16',protocols=["OpenFlow13"],datapath='kernel')
    s17 = net.addSwitch('s17',protocols=["OpenFlow13"],datapath='kernel')
    s18 = net.addSwitch('s18',protocols=["OpenFlow13"],datapath='kernel')    

    info('Create Host node\n')
    h1 = net.addHost('h1', ip='10.0.0.1',mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2',mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3',mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='10.0.0.4',mac='00:00:00:00:00:04')
    h5 = net.addHost('h5', ip='10.0.0.5',mac='00:00:00:00:00:05')
    h6 = net.addHost('h6', ip='10.0.0.6',mac='00:00:00:00:00:06')
    h7 = net.addHost('h7', ip='10.0.0.7',mac='00:00:00:00:00:07')
    h8 = net.addHost('h8', ip='10.0.0.8',mac='00:00:00:00:00:08')
    #modify
    h9 =net.addHost('h9', ip='10.0.0.9',mac='00:00:00:00:00:09')
    h10=net.addHost('h10', ip='10.0.0.10',mac='00:00:00:00:00:0A')
    info('Add links\n')

    # set system datapath
    # print( "Set sw datapath to system")
    # for sw in net.switches:
    #     print sw
    #     sw.cmd('ovs-vsctl set Bridge ',sw, 'datapath_type=system')
    # print( "verify sw datapath changes")
    #domain 1 switch link
    net.addLink(s1, s2, 1, 1,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s1, s3, 2, 1,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s2, s3, 2, 2,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s2, s4, 3, 1,cls=TCLink,bw=10,use_tbf=True)
    
    #domain 1 host
    net.addLink(s1, h1, 4, 0,cls=TCLink,bw=10,use_tbf=True )
    net.addLink(s3, h2, 3, 0,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s4, h3, 5, 0,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s4, h4, 6, 0,cls=TCLink,bw=10,use_tbf=True)

    #domain 2 switch link
    net.addLink(s5, s6, 1, 1,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s5, s7, 2, 1,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s7, s8, 2, 2,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s6, s8, 2, 1,cls=TCLink,bw=10,use_tbf=True)
    #net.addLink(s5, s8, 3, 3,bw=10)


    #domain 2 host
    net.addLink(s5, h5, 4, 0,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s6, h6, 4, 0,cls=TCLink,bw=10,use_tbf=True)
    #modify
    net.addLink(s7, h9,4,0,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s8, h10,6,0,cls=TCLink,bw=10,use_tbf=True)
    #domain 3 switch link
    net.addLink(s9, s10, 1, 1)
    net.addLink(s9, s11, 2, 1)
    net.addLink(s10, s11, 2, 2)
    net.addLink(s10, s12, 3, 1)
    net.addLink(s11, s12, 3, 2)

    #domain 3 host
    net.addLink(s11, h7, 5, 0)
    net.addLink(s12, h8, 3, 0)
    
    #domain link (D1D2)
    net.addLink(s1, s13, 3, 1,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s13, s7, 2, 3,cls=TCLink,bw=10,use_tbf=True)
    #modify
    net.addLink(s4, s14, 4, 1,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s14, s8, 2, 5,cls=TCLink,bw=10,use_tbf=True)

    #domain link (D1D3)
    net.addLink(s4, s15, 3, 1,cls=TCLink,bw=10)
    net.addLink(s15, s9, 2, 3,cls=TCLink,bw=10)

    net.addLink(s4, s16, 2, 1,cls=TCLink,bw=10)
    net.addLink(s16, s11, 2, 4,cls=TCLink,bw=10)

    #domain link (D2D3)
    net.addLink(s6, s17, 3, 1)
    net.addLink(s17, s10, 2, 4)

    net.addLink(s8, s18, 4, 1)
    net.addLink(s18, s9, 2, 4)
    # for sw in net.switches:
    #     print(sw.cmd('ovs-vsctl get Bridge ',sw,' datapath_type'))  
    
    info( '*** Starting network\n')
    net.build()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0]) # start target switch 's1' to connect to controller c0
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

    for i in range(1,11):
        tmp=net.get('h'+str(i))
        print ('ethtool -K h'+str(i)+'-eth0 tx off')
        tmp.cmd('ethtool -K h'+str(i)+'-eth0 tx off')
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    MininetTopo()

