import psutil
import ipaddress

def get_local_subnet():
    for iface_name, iface_addrs in psutil.net_if_addrs().items():
        for addr in iface_addrs:
            if addr.family.name == 'AF_INET' and not iface_name.startswith("lo"):
                ip = addr.address
                netmask = addr.netmask
                if ip and netmask:
                    try:
                        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                        print(f"[INFO] Computed local subnet: {network}")
                        return str(network)
                    except Exception as e:
                        print(f"[ERROR] Failed to calculate subnet: {e}")
    return "127.0.0.1/32"

NETWORK_RANGE = "192.168.1.0/24"
DATABASE_PATH = "known_hosts.db"
LOG_FILE = "flask.log"
ERROR_LOG_FILE = "app_errors.log"
SUBNET = get_local_subnet()
SCAN_INTERVAL = 30  # in minutes
DEBUG_MODE = False
TEST_MODE = False
