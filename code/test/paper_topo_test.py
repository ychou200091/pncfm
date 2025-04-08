from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call



def MininetTopo():
    net = Mininet (topo=None, build=False)

    
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=6633)




    
    info('Create Switch node\n')
    s1 = net.addSwitch('s1',protocols=["OpenFlow13"])
    #s2 = net.addSwitch('s2',protocols=["OpenFlow13"],datapath='user')
    #s3 = net.addSwitch('s3',protocols=["OpenFlow13"],datapath='user')
    #s4 = net.addSwitch('s4',protocols=["OpenFlow13"],datapath='user')


    #info('Create Host node\n')
    h1 = net.addHost('h1', ip='10.0.0.1',mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2',mac='00:00:00:00:00:02')
    #h3 = net.addHost('h3', ip='10.0.0.3',mac='00:00:00:00:00:03')
    #h4 = net.addHost('h4', ip='10.0.0.4',mac='00:00:00:00:00:04')

    info('Add links\n')
    #domain 1 switch link
    #net.addLink(s1, s2, 1, 1,cls=TCLink,bw=10)
    #net.addLink(s1, s3, 2, 1,cls=TCLink,bw=10)
    #net.addLink(s2, s3, 2, 2,cls=TCLink,bw=10)
    #net.addLink(s2, s4, 3, 1,cls=TCLink,bw=10)
    
    #domain 1 host
    net.addLink(s1, h1, 1, 0,cls=TCLink,bw=10,use_tbf=True)
    net.addLink(s1, h2, 2, 0,cls=TCLink,bw=10,use_tbf=True)
    #net.addLink(s4, h3, 5, 0,bw=10)
    #net.addLink(s4, h4, 6, 0,bw=10)
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    #net.get('s2').start([c0])
    #net.get('s3').start([c0])
    #net.get('s4').start([c0])
    info( '*** Post configure switches and hosts\n')
   
    #print h1.cmd('iperf -c 10.0.0.2 -u -b 15M -t 50  -c1 %s' % h2.IP())
    #net,startShell()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    MininetTopo()

