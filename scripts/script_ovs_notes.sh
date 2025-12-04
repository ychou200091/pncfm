# this scripts has commands I found along the way, they may or may not be useful.

# --------------
#remove the old ovs
kill `cd /usr/local/var/run/openvswitch && cat ovsdb-server.pid ovs-vswitchd.pid`
aptitude remove openvswitch-common openvswitch-datapath-dkms openvswitch-controller openvswitch-pki openvswitch-switch -y
# this script include commands to reinstall openvswitch 
rmmod openvswitch

#install the new ovs
cd ovs
./boot.sh
./configure #--with-linux=/lib/modules/`uname -r`/build
sudo make
sudo make install
export PATH=$PATH:/usr/local/share/openvswitch/scripts

#start the new ovs
/etc/init.d/openvswitch-switch start
ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach --log-file
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach 

# --------------
# CHECK IF OVS is correctly installed
# helper scripts
modprobe gre
insmod datapath/linux/openvswitch.ko
make modules_install
modprobe openvswitch
# --------------
#disable openvswitch controller
/etc/init.d/openvswitch-controller stop
update-rc.d openvswitch-controller disable
# --------------
#start the new ovs
/etc/init.d/openvswitch-switch start
ovsdb-tool create /usr/local/etc/openvswitch/conf.db /usr/local/share/openvswitch/vswitch.ovsschema
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach --log-file
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach 
