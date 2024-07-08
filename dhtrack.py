import argparse
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
from time import sleep

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
            
class TrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)
        
        # Log the announce message
        print(f"Announce received: {params}")
        
        # Respond with an empty peer list (passive behavior)
        response = "d8:completei1e10:incompletei1e8:intervali1800e12:min intervali900e5:peers0:e"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode())

def run_tracker(server_class=HTTPServer, handler_class=TrackerHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting passive tracker on port {port}")
    httpd.serve_forever()

def dht_monitor(hashes_file, cidr_file, db_file):
    # Set up the session and DHT settings
    ses = lt.session()
    ses.listen_on(6881, 6891)
    ses.start_dht()

    while True:
        alerts = ses.pop_alerts()
        for alert in alerts:
            handle_alert(alert)
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="DHT Monitoring and Passive Tracker")
    parser.add_argument('--hashes_file', type=str, required=True, help="File containing info hashes to monitor")
    parser.add_argument('--cidr_file', type=str, required=True, help="File containing CIDR blocks to monitor")
    parser.add_argument('--db_file', type=str, required=True, help="SQLite database file")
    parser.add_argument('--tracker_port', type=int, default=None, help="Port to run the passive tracker on")

    args = parser.parse_args()

    # Start the DHT monitoring thread
    dht_thread = threading.Thread(target=dht_monitor, args=(args.hashes_file, args.cidr_file, args.db_file))
    dht_thread.daemon = True
    dht_thread.start()

    # Optionally start the passive tracker server
    if args.tracker_port:
        tracker_thread = threading.Thread(target=run_tracker, args=(HTTPServer, TrackerHandler, args.tracker_port))
        tracker_thread.daemon = True
        tracker_thread.start()

    # Keep the main thread alive
    while True:
        sleep(1)

if __name__ == "__main__":
    main()       
          


