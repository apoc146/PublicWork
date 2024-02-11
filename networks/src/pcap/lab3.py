import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from scapy.all import *




def getPartA(pcapFileName):
    
    packets = rdpcap(pcapFileName) 
    # dhcp_packets = [pkt for pkt in packets if DHCP in pkt]
    dhcpAckPackets = [pkt for pkt in packets if DHCP in pkt and pkt[DHCP].options[0][1] == 5]

    # Iterate through DHCP ACK packets and print relevant information
    routerIP=0
    macAdd="ff"
    for pkt in dhcpAckPackets:
        options=pkt[DHCP].options
        for opt in options:
            if(opt[0] == 'router'):
                routerIP=opt[1]
        break
    # print(routerIP)

    ## get arp packets
    arp_ack_packets = [pkt for pkt in packets if ARP in pkt and pkt[ARP].op == 2 and pkt[ARP].psrc == routerIP]
    for pkt in arp_ack_packets:
        macAdd=pkt[ARP].hwsrc
        break
    # print(macAdd)
    print("CASE A:")
    print("IPAddr:", routerIP)
    print("MACAddr:", macAdd)

def getPartB(pcapFileName,website):
    destIp = None
    packets = rdpcap(pcapFileName) 
    dns_packets = [pkt for pkt in packets if DNS in pkt]

    for pck in dns_packets:
        if pck.haslayer(DNSRR) and pck[DNSRR].rrname.decode("utf-8").lower().startswith(website):
            destIp= pck["DNS"].an.rdata
            break
    
    print("CASE B:")
    print("IPAddr-DEST:", destIp)

def getPartC(pcapFile,website):
    packets = rdpcap(pcapFile)

    ## first get dest ip
    destIp = None
    dns_packets = [pkt for pkt in packets if DNS in pkt]

    for pck in dns_packets:
        if pck.haslayer(DNSRR) and pck[DNSRR].rrname.decode("utf-8").lower().startswith(website):
            destIp= pck["DNS"].an.rdata
            break

    websiteIP=destIp
    tcp_packets = [pkt for pkt in packets if pkt.haslayer(TCP)]
    print("CASE C:")
    count=0
    for pck in tcp_packets:
        if pck.haslayer(TCP):
            if( count==0 and pck[IP].dst == websiteIP and pck[TCP].flags.S==True and pck[TCP].flags.A==False):
                print("IPAddr-SRC:",pck["IP"].src)
                print("IPAddr-DEST:",pck["IP"].dst)
                print("Port-DEST:",pck["TCP"].dport)
                print("SYN: 1")
                print("ACK: 0")
                count+=1
                continue
            
            if( count==1 and pck[IP].src == websiteIP and pck[TCP].flags.S==True and pck[TCP].flags.A==True):
                print("IPAddr-SRC:",pck["IP"].src)
                print("IPAddr-DEST:",pck["IP"].dst)
                print("Port-DEST:",pck["TCP"].sport)
                print("SYN: 1")
                print("ACK: 1")
                count+=1
                continue
            
            if( count==2 and pck[IP].dst == websiteIP and pck[TCP].flags.S==False and pck[TCP].flags.A==True):
                print("IPAddr-SRC:",pck["IP"].src)
                print("IPAddr-DEST:",pck["IP"].dst)
                print("Port-DEST:",pck["TCP"].dport)
                print("SYN: 0")
                print("ACK: 1")
                count+=1
                continue
        if count==3:
            break

if __name__=="__main__":
    args = sys.argv
    file_name = args[2]

    if args[1] == "A":
        getPartA(file_name)
    elif args[1] == "B":
        getPartB(file_name, args[3])
    elif args[1] == "C":
        getPartC(file_name, args[3])
    elif args[1] == "ALL":
        getPartA(file_name)
        getPartB(file_name, args[3])
        getPartC(file_name, args[3])
    else:
        print("Please enter the correct args")