import requests
import argparse
import random
import string
import time

def generate_random_peer_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def send_announce_request(info_hash, peer_id, port, ip, tracker_url):
    params = {
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': port,
        'event': 'started',
        'ip': ip
    }
    response = requests.get(tracker_url, params=params)
    return response

def main(info_hash, peer_id, port, ip, num_requests, tracker_url):
    for _ in range(num_requests):
        peer_id = generate_random_peer_id() if peer_id is None else peer_id
        response = send_announce_request(info_hash, peer_id, port, ip, tracker_url)
        print(f"Sent announce: {response.url} - Status: {response.status_code}")
        time.sleep(random.uniform(1, 5))  # Random delay between requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof Tracker Announce Requests")
    parser.add_argument("--info_hash", required=True, help="Info hash of the torrent")
    parser.add_argument("--peer_id", help="Peer ID (random if not specified)")
    parser.add_argument("--ip", required=True, help="IP address to announce")
    parser.add_argument("--port", type=int, required=True, help="Port number")
    parser.add_argument("--num_requests", type=int, default=1, help="Number of requests to send")
    parser.add_argument("--tracker_url", default="http://tracker.example.com/announce", help="Tracker announce URL")
    
    args = parser.parse_args()
    main(args.info_hash, args.peer_id, args.port, args.ip, args.num_requests, args.tracker_url)
