/etc/init.d/openvswitch-switch start
sudo pkill ovs-vswitchd
sudo pkill ovsdb-server

sudo rm -f ~/usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema

ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach --log-file
ovs-vsctl --no-wait init
#ovs-vswitchd --pidfile --detach #

#ovs-vsctl set Open_vSwitch . other_config:n-offload-threads=4
#ovs-vsctl set Open_vSwitch . other_config:n-revalidator-threads=4
#ovs-vsctl set Open_vSwitch . other_config:n-handler-threads=4
ovs-vswitchd --pidfile --detach

# n-offload-threads:  Set this value to the number of threads created to manage  hard‐ware offloads.
# n-handler-threads: number of threads for software datapaths to  use for handling new flows.

# check if the above process exists.
pgrep -fl ovsdb-server
pgrep -fl ovs-vswitchd
