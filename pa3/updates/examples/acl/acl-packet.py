import nox.lib.core as core
from nox.lib.core import Component
from nox.lib.netinet.netinet import datapathid
from frenetic_net import *
from update import update, per_packet_update
from policy import Rule, SwitchConfiguration, NetworkPolicy
from nox.lib.packet.ethernet import ethernet
from nox.lib.packet.ipv4 import ipv4

from twisted.python import log

import logging

logger = logging.getLogger('nox.coreapps.examples.acl-nox')

""" Simple ACL example from HotNets paper w/ three filter switches, an ingress and an egress switch. The ingress switch is connected to trusted and untrusted hosts and the egress switch is connected to an internal server. Trusted hosts are allowed arbitrary access to the server, and untrusted hosts are allowed only web and ARP access to the server. Trusted and untrusted hosts are known only by their physical port on the ingress switch. Initially, trusted traffic is filtered on switch leftFilter, and trusted traffic is routed through middleFilter and rightFilter. Then, some untrusted traffic is migrated to middleFilter and trusted traffic is pushed onto rightFilter.

Topology is in acl-topo.py

Run the example by first installing the example:

    $ cp acl-packet.py noxcore/src/nox/coreapps/examples/
    $ cp update.py noxcore/src/nox/coreapps/examples/

Tell NOX about the example:
   $ cd noxcore/src/nox/coreapps/examples/
   $ vim Makefile.am
   add update.py,acl-packet.py to NOX_RUNTIMEFILES

   $ vim meta.xml
   Add these entries:

    <component>
       <name>update</name>
        <dependency>
             <name>python</name>
        </dependency>
        <python>nox.coreapps.examples.update</python>
    </component>

    <component>
        <name>acl-packet</name>
        <dependency>
            <name>python</name>
        </dependency>
        <dependency>
            <name>update</name>
        </dependency>
        <python>nox.coreapps.examples.acl-packet</python>
    </component>

Rebuild NOX
    $ cd ~/noxcore/build
    $ make
  
Start up the topology:
    sudo mn --custom /home/openflow/acl-topo-nx.py --topo mytopo

Then start up the example:
    ./nox_core -v -i ptcp:6633  acl-packet

Start pinging continuously from h22 or h23 to test the seamless update:
   mininet> h22 ping h30

"""

    
def host_to_ip(hostid):
    return "10.0.0." + str(hostid)

ingress = 1
egress = 2
leftFilter = 10
middleFilter = 11
rightFilter = 12
server = 30

host0 = 1 # host_to_ip(20)
host1 = 2 # host_to_ip(21)
host2 = 3 # host_to_ip(22)
host3 = 4 # host_to_ip(22)

host0_ip = host_to_ip(20)
host1_ip = host_to_ip(21)
host2_ip = host_to_ip(22)
host3_ip = host_to_ip(23)
serverIP = host_to_ip(server)

ingress_port_map = { host0 : 1,
                    host1 : 2,
                    host2: 3,
                    host3: 4,                    
                    leftFilter : 5,
                    middleFilter : 6,
                    rightFilter : 7}

port_to_ingress = {leftFilter : 1,
                   middleFilter : 1,
                   rightFilter : 1}

port_to_egress = { leftFilter : 2,
                  middleFilter : 2,
                  rightFilter : 2}


ingress_config_1 = SwitchConfiguration( [ Rule( {core.IN_PORT : host0},
                                                 [ forward(ingress_port_map[leftFilter]) ]),
                                          Rule( {core.IN_PORT : host1},
                                                 [ forward(ingress_port_map[leftFilter]) ]),
                                          Rule( {core.IN_PORT : host2},
                                                 [ forward(ingress_port_map[middleFilter]) ]),
                                          Rule( {core.IN_PORT : host3},
                                                 [ forward(ingress_port_map[rightFilter]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host0_ip},
                                                 [ forward(ingress_port_map[host0]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host1_ip},
                                                 [ forward(ingress_port_map[host1]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host2_ip},
                                                 [ forward(ingress_port_map[host2]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host3_ip},
                                                 [ forward(ingress_port_map[host3]) ]),
                                          # ARP
                                          Rule( {core.DL_TYPE : ethernet.ARP_TYPE, core.IN_PORT : ingress_port_map[leftFilter]},
                                                 [ forward(ingress_port_map[host0]),
                                                   forward(ingress_port_map[host1]),
                                                   forward(ingress_port_map[host2]),
                                                   forward(ingress_port_map[host3]) ]),
                                          ])
                                                 
leftFilter_config_1 = SwitchConfiguration( [ Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_PROTO : ipv4.TCP_PROTOCOL, core.TP_DST : 80, core.IN_PORT : 1},
                                                    [ forward(2) ]),
                                             Rule( {core.DL_TYPE : ethernet.ARP_TYPE, core.IN_PORT : 1},
                                                    [ forward(2) ]),                                                    
                                             Rule( {core.IN_PORT : 2},
                                                    [ forward(1) ])
                                           ])
                                                 
middleFilter_config_1 = SwitchConfiguration( [ Rule( {core.IN_PORT : 1},
                                                    [ forward(2) ]),
                                               Rule( {core.IN_PORT : 2},
                                                    [ forward(1) ])
                                           ])

rightFilter_config_1 = SwitchConfiguration( [ Rule( {core.IN_PORT : 1},
                                                    [ forward(2) ]),
                                              Rule( {core.IN_PORT : 2},
                                                    [ forward(1) ])
                                           ])

egress_config = SwitchConfiguration( [ Rule( {core.IN_PORT : 1},
                                            [ forward(4) ]),
                                       Rule( {core.IN_PORT : 2},
                                            [ forward(4) ]),
                                       Rule( {core.IN_PORT : 3},
                                            [ forward(4) ]),
                                       Rule( {core.IN_PORT : 4},
                                            [ forward(1) ])
                                     ])
                                            
                                                 
ACL1 = NetworkPolicy({ ingress      : ingress_config_1,
                       leftFilter   : leftFilter_config_1,
                       middleFilter : middleFilter_config_1,
                       rightFilter  : rightFilter_config_1,
                       egress       : egress_config })

                       
ingress_config_2 = SwitchConfiguration( [ Rule( {core.IN_PORT : host0},
                                                 [ forward(ingress_port_map[leftFilter]) ]),
                                          Rule( {core.IN_PORT : host1},
                                                 [ forward(ingress_port_map[middleFilter]) ]),
                                          Rule( {core.IN_PORT : host2},
                                                 [ forward(ingress_port_map[rightFilter]) ]),
                                          Rule( {core.IN_PORT : host3},
                                                 [ forward(ingress_port_map[rightFilter]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host0_ip},
                                                 [ forward(ingress_port_map[host0]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host1_ip},
                                                 [ forward(ingress_port_map[host1]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host2_ip},
                                                 [ forward(ingress_port_map[host2]) ]),
                                          Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_DST : host3_ip},
                                                 [ forward(ingress_port_map[host3]) ]),
                                          # ARP
                                          Rule( {core.DL_TYPE : ethernet.ARP_TYPE, core.IN_PORT : ingress_port_map[leftFilter]},
                                                 [ forward(ingress_port_map[host0]),
                                                   forward(ingress_port_map[host1]),
                                                   forward(ingress_port_map[host2]),
                                                   forward(ingress_port_map[host3]) ])
                                        ])

leftFilter_config_2 = SwitchConfiguration( [ Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_PROTO : ipv4.TCP_PROTOCOL, core.TP_DST : 80, core.IN_PORT : 1},
                                                    [ forward(2) ]),
                                             Rule( {core.DL_TYPE : ethernet.ARP_TYPE, core.IN_PORT : 1},
                                                    [ forward(2) ]),                                                      
                                             Rule( {core.IN_PORT : 2},
                                                    [ forward(1) ])
                                           ])

middleFilter_config_2 = SwitchConfiguration( [ Rule( {core.DL_TYPE : ethernet.IP_TYPE, core.NW_PROTO : ipv4.TCP_PROTOCOL, core.TP_DST : 80, core.IN_PORT : 1},
                                                    [ forward(2) ]),
                                               Rule( {core.DL_TYPE : ethernet.ARP_TYPE, core.IN_PORT : 1},
                                                    [ forward(2) ]),                                                      
                                               Rule( {core.IN_PORT : 2},
                                                    [ forward(1) ])
                                             ])

rightFilter_config_2 = SwitchConfiguration( [ Rule( {core.IN_PORT : 1},
                                                    [ forward(2) ]),
                                              Rule( {core.IN_PORT : 2},
                                                    [ forward(1) ])
                                           ])

ACL2 = NetworkPolicy({ ingress      : ingress_config_2,
                       leftFilter   : leftFilter_config_2,
                       middleFilter : middleFilter_config_2,
                       rightFilter  : rightFilter_config_2,
                       egress       : egress_config })


class ACL_Packet(Component):

    def __init__(self, ctxt):
        global inst
        Component.__init__(self, ctxt)

    def install(self):
        global inst
        inst = self.resolve(update)
        print ACL1.convert_to_nox_policy()
        per_packet_update(ACL1, edge_switches=[ingress,egress])
        self.post_callback(10, self.move_to_ACL2)                

    def getInterface(self):
        return str("ACL Packet")

    def move_to_ACL2(self):
       print 'Moving to ACL2'
       per_packet_update(ACL2, edge_switches=[ingress, egress])


def getFactory():
    class Factory:
        def instance(self, ctxt):
            return ACL_Packet(ctxt)
   
    return Factory()
