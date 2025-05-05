import sqlite3

def insert_known_host(mac, ip=None, hostname=None, vendor=None, os=None, notes=None):
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
        INSERT INTO known_hosts (mac, ip, hostname, vendor, os, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(mac) DO UPDATE SET
            ip=excluded.ip,
            hostname=excluded.hostname,
            vendor=excluded.vendor,
            os=excluded.os,
            notes=excluded.notes
    ''', (mac, ip, hostname, vendor, os, notes))
    conn.commit()
    conn.close()
    print(f"[✓] Saved: {mac}")

# Example
if __name__ == "__main__":
    insert_known_host("AA:BB:CC:DD:EE:FF", ip="192.168.1.100", hostname="MyDevice", vendor="Cisco", os="Linux", notes="Lab test device")
