import sqlite3
import ipaddress
import libtorrent as lt
import time

# Connect to the SQLite database
conn = sqlite3.connect('monitoring.db')
c = conn.cursor()

# Function to retrieve CIDR blocks from the database
def get_cidr_blocks():
    c.execute("SELECT cidr FROM cidr_blocks")
    return [row[0] for row in c.fetchall()]

# Function to check if a hash exists in the database
def hash_exists(info_hash):
    c.execute("SELECT 1 FROM hashes WHERE info_hash = ?", (info_hash,))
    return c.fetchone() is not None

# Convert CIDR blocks to a list of IP networks
cidr_blocks = get_cidr_blocks()
ip_networks = [ipaddress.ip_network(cidr) for cidr in cidr_blocks]

# check if an IP address is in the CIDR blocks
def is_ip_in_cidr_blocks(ip):
    ip_addr = ipaddress.ip_address(ip)
    return any(ip_addr in network for network in ip_networks)

def handle_alert(alert):
    if isinstance(alert, lt.dht_announce_alert):
        info_hash = str(alert.info_hash)
        ip = alert.ip
        if hash_exists(info_hash) or is_ip_in_cidr_blocks(ip):
            print(f"Matched Announce: {ip}:{alert.port} for info_hash: {alert.info_hash}")
          
# Set up the session and DHT settings
ses = lt.session()
ses.listen_on(6881, 6891)
ses.start_dht()

while True:
    alerts = ses.pop_alerts()
    for alert in alerts:
        handle_alert(alert)
    time.sleep(1)

