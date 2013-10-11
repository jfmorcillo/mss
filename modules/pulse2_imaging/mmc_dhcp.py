from IPy import IP
from mmc.plugins.network.tools import numToDottedQuad, dottedQuadToNum
from mmc.plugins.network import getSubnets, setSubnetStatement, addSubnet, setSubnetAuthoritative, addPool, getPoolsRanges
from optparse import OptionParser

def mmc_pxe_configure(interface, ipaddr, netmask):
    net = numToDottedQuad(dottedQuadToNum(netmask) & dottedQuadToNum(ipaddr))

    if not getSubnets(net):
        bitlength = reduce(lambda x, y: x + (y + 1)/32, map(int, netmask.split(".")), 0)
        addSubnet(net, bitlength, "Pulse2 Subnet");

    if not getPoolsRanges(net):
        ips = IP('%s/%s' % (ipaddr, netmask), make_net=True)
        for ip in ips:
            if not str(ip) == ipaddr and not str(ip).endswith('0'):
                start = str(ip)
                break
        for nb in (50, 25, 10, 5):
            try:
                end = str(ips[nb])
                break
            except:
                pass
        if start and end:
            addPool(net, "Imaging pool", start, end)

    # Configure pxe
    setSubnetStatement(net, "filename", "\"/bootloader/pxe_boot\"")
    setSubnetStatement(net, "next-server", ipaddr)
    #/bootloader/pxe_boot
    setSubnetAuthoritative(net)


if __name__ == "__main__":
        # Get options
    parser = OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to configure")
    parser.add_option("-a", "--address", dest="ipaddr", help="Network address")
    parser.add_option("-n", "--netmask", dest="netmask", help="Netmask")
    (options, args) = parser.parse_args()

    mmc_pxe_configure(options.interface, options.ipaddr, options.netmask)
