# Run this script when you want to start or restart openvsiwtch(OVS)

/etc/init.d/openvswitch-switch start
sudo pkill ovs-vswitchd
sudo pkill ovsdb-server

sudo rm -f ~/usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema

ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach --log-file
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach 

# check if the above process exists.
pgrep -fl ovsdb-server
pgrep -fl ovs-vswitchd
