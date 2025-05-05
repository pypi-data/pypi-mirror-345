import sqlite3
import nmap
from datetime import datetime

def update_os_in_db(ip, mac, os_info):
    conn = sqlite3.connect("known_hosts.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS known_hosts (
            mac TEXT PRIMARY KEY,
            ip TEXT,
            hostname TEXT,
            vendor TEXT,
            os TEXT,
            notes TEXT
        )
    ''')
    c.execute('''
        INSERT INTO known_hosts (mac, ip, os)
        VALUES (?, ?, ?)
        ON CONFLICT(mac) DO UPDATE SET os=excluded.os
    ''', (mac, ip, os_info))
    conn.commit()
    conn.close()

def deep_scan():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-O')  # OS detection
    for host in nm.all_hosts():
        ip = host
        mac = nm[host]['addresses'].get('mac', 'N/A')
        os_info = "N/A"
        if 'osmatch' in nm[host] and nm[host]['osmatch']:
            os_info = nm[host]['osmatch'][0]['name']
        if mac != "N/A":
            update_os_in_db(ip, mac, os_info)
            print(f"[✓] {ip} ({mac}) -> {os_info}")

if __name__ == "__main__":
    print(f"Started deep scan at {datetime.now()}")
    deep_scan()
