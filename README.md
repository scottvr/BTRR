# BTRR (The BitTorrent RailRoad) - Falsifying Evidence with Spoofed Announcements

## Overview

This repository contains tools designed to demonstrate and exploit vulnerabilities in BitTorrent tracker and Distributed Hash Table (DHT) systems. Why "BTRR"? Because "Track" and "Forge" bring to mind the Railways, and because 

**railroad:** (verb) - _to convict with undue haste and by means of false charges or insufficient evidence._

By spoofing tracker announce messages and monitoring DHT traffic, we highlight the potential for false evidence of seeding or leeching of torrents to be placed by a malicious actor, and picked up by (unwittingly or otherwise)  those in the business of monitoring peer-to-peer (P2P) networks, for such purposes as DMCA notices (or much more concerning, reporting on evidence of the trading in abuse-related materials.)

## Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [BTForge - Tracker Spoofing Tool](#btforge---tracker-spoofing-tool)
  - [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
- [DHTrack - DHT Monitoring Tool](#dhtrack---dht-monitoring-tool)
  - [Usage](#usage-1)
  - [Command-Line Arguments](#command-line-arguments-1)
- [Database Management](#database-management)
  - [Storing Info Hashes](#storing-info-hashes)
  - [Storing CIDR Blocks](#storing-cidr-blocks)
- [Use Cases](#use-cases)
- [Conclusion](#conclusion)
- [Resources](#resources)


## Introduction

BitTorrent and other P2P networks face challenges from anti-piracy efforts that rely on IP address monitoring. Additionally, sites such as iknowwhatyoudownload.com purport to show the torrents that have been downloaded from an IP address, and take it a step further by categorizing the downloads, allegedly making a claim as to whether a given IP address shares abuse-related content. 

The trouble with DMCA notices has been well-documented, and no one is likely to argue that calling out abuse/illegal materials is a bad thing, however, it is important to point out that these systems can be exploited to fabricate "evidence" that an IP address is trafficking pirated software, leaked confidential material, or illegal and abusive media files.  While it is dubious that a criminal prosecution would commence on only this sort of evidence, an accusation of such deeds appearing on a public website without disclaimer or mention of these issues is troubling as is the apparent lack of conversation or awareness of how easy this forgery is to pull off. 

Although one study addressed this from the DMCA angle (the UW paper listed in [Resources](Resources) - way back in 2008), and does show an example of how an IP address can be specified in a simple http request using wget, there seems to be an absence of code to easily parameterize requests or automate any sort of bulk testing, among other desireable features, discussion after this paper seems nonexistent in the public forum.  

This repository presents two tools:

- **BTForge** - A Tracker Spoofing Tool for sending falsified announce messages to BitTorrent trackers. This is a PoC demonstration for evidence forgery. 
- **DHTrack** - A DHT Monitoring Tool and passive tracker daemon for observing and logging DHT traffic, with the ability to focus only on specific info hashes and CIDR blocks. This was created as a way to validate the forgery PoC, but gathers information about real activity on the BitTorrent network as well, which is the point: there is no way to validate alleged information passed from peer to peer or client to tracker via these announcements. 

## Installation

To install these tools, clone the repository and install dependencies:

```
git clone https://github.com/scottvr/BTRR.git
cd BTRR
pip install -r requirements.txt
```

## libtorrent prerequisite
The libtorrent python bindings do need to be able to find libtorrent in the library path or working directory. 

## BTForge - Tracker Spoofing Tool

v1.0

BTForge sends falsified announce messages to a specified tracker URL to demonstrate the ease of planting false evidence.

### Usage

```
python btforge.py --info_hash abcdef1234567890 --port 6881 --ip 192.168.1.100 --num_requests 10
```

### Command-Line Arguments

- `--info_hash`: The info hash of the torrent (required).
- `--peer_id`: The peer ID (optional, random if not specified).
- `--port`: The port number (required).
- `--ip`: The IP address to announce (required).
- `--num_requests`: The number of requests to send (default: 1).
- `--tracker_url`: The tracker announce URL (default: "http://tracker.example.com/announce")

## DHTrack - DHT Monitoring Tool

v1.0

DHTrack listens for DHT traffic, checking for specific info hashes and CIDR blocks of interest. Results are logged and stored in an SQLite database.

v1.1

- add optional httpserver to serve as passive tracker. Per BitTorrent  protocol, it just returns an empty peer list. The tool does not actually function to facilitate torrent transfers; only serves to collect information such as up/download stats.
- since we're now starting two network daemons, add threading capability. (One process, with two threads, one for the DHT listener and one for the http tracker server for the tracker) 
  
### Usage

```
python dhtrack.py --hashes_file hashes.txt --cidr_file cidr_blocks.txt --db_file dhtrack.db
```

### Command-Line Arguments

- `--hashes_file`: Path to the file containing info hashes to monitor.
- `--cidr_file`: Path to the file containing CIDR blocks to monitor.
- `--db_file`: Path to the SQLite database file.
- `--tracker_port`: (optional) tcp port to bind a passive tracker to, for the purpose of collecting additional information about transfers on the bittorrent network. 

## SQLlite Database 

### Storing Info Hashes

Info hashes are stored in an SQLite database for efficient searching. The database schema includes a table for info hashes:

```sql
CREATE TABLE IF NOT EXISTS info_hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash TEXT UNIQUE NOT NULL
);
```

### Storing CIDR Blocks

CIDR blocks are also stored in the same SQLite database. The schema includes a table for CIDR blocks:

```sql
CREATE TABLE IF NOT EXISTS cidr_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cidr TEXT UNIQUE NOT NULL
);
```
A utility script is provided to help you create and populate the tables with IP addresses or info_hashes you wish to monitor. 


## Use Cases

- **Demonstrating Vulnerabilities**: Show how innocent IP addresses can be implicated in P2P activity using spoofed tracker announces.
- **Monitoring Specific Activity**: Track specific info hashes or IP ranges for research (such as to verify the PoC to show the spoofed information appear in the DHT or for other network security purposes.

## Conclusion

By demonstrating how easily false evidence appearing to show copyright infringement (or worse) can be generated, we aim to encourage improvements in anti-piracy mechanisms and raise awareness about the limitations of IP-based tracking.

## Resources

- [Merriam-Webster definition of "railroad"](https://www.merriam-webster.com/dictionary/railroad#:~:text=%3A%20to%20convict%20with%20undue%20haste,false%20charges%20or%20insufficient%20evidence)
- ["Tracking the Trackers" - University of Washington BitTorrent/DMCA notice Study](http://dmca.cs.washington.edu/)
- [ratio-spoof on GitHub](https://github.com/ap-pauloafonso/ratio-spoof)
- [TorrentFreak Article about iknowwhatyoudownload.com](https://torrentfreak.com/i-know-what-you-download-overwhelmed-by-bogus-dmca-notices-221023/)
```
