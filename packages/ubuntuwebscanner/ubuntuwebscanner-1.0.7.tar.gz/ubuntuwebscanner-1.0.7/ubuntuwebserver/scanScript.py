import nmap

nm = nmap.PortScanner()
nm.scan(hosts='192.168.1.0/24', arguments='-sn')  # Ping scan

for host in nm.all_hosts():
    print(f"Host: {host} ({nm[host].hostname()}) | MAC: {nm[host]['addresses'].get('mac', 'N/A')}")
