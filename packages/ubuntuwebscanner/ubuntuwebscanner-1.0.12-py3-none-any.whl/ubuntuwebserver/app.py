from flask import Flask, render_template
import nmap
from manuf import manuf
import os
import json
from ubuntuwebserver.config import SUBNET, TEST_MODE  # Make sure TEST_MODE is imported

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
mac_parser = manuf.MacParser()

def scan_network():
    if TEST_MODE:
        print("[TEST MODE] Returning mock scan results.")
        return [{
            'ip': '192.168.1.10',
            'hostname': 'MockHost',
            'mac': 'AA:BB:CC:DD:EE:FF',
            'vendor': 'MockVendor',
            'os': 'MockOS',
            'notes': 'Test device'
        }]
    def load_os_cache():
        try:
            with open("/tmp/os_cache.json") as f:
                data = json.load(f)
                return data.get("os_results", {})
        except Exception:
            return {}
    
    nm = nmap.PortScanner()
    nm.scan(hosts=SUBNET, arguments="-sn")
    hosts = []
    os_cache = load_os_cache()

    for host in nm.all_hosts():
        mac = nm[host]['addresses'].get('mac', 'N/A')
        vendor = mac_parser.get_manuf(mac) if mac != "N/A" else "N/A"
        os_info = os_cache.get(host, "Unknown")
        hosts.append({
            'ip': host,
            'hostname': nm[host].hostname(),
            'mac': mac,
            'vendor': vendor,
            'os': os_info
        })

    return hosts

@app.route("/")
def home():
    results = scan_network()
    return render_template("scan_results.html", results=results)

# ✅ ADD THIS FUNCTION
def main():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Optional: keep this too
if __name__ == "__main__":
    main()
