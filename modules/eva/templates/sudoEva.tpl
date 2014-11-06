# User alias specification
User_Alias      EVAADMINS = eva
#Host_Alias      EVAHOSTS = 127.0.0.1,localhost,eva
Cmnd_Alias      EVACMDS = /sbin/ip, /sbin/arp, /usr/bin/virt-inspector, /usr/bin/virsh, /usr/bin/virt-*, /usr/bin/qemu-*
#
# Commands
#
EVAADMINS       ALL = NOPASSWD: EVACMDS
