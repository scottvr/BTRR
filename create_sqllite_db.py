import sqlite3

# connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('monitoring.db')
c = conn.cursor()

# create info_hash table if it doesn't exist 
c.execute('''CREATE TABLE IF NOT EXISTS hashes (info_hash TEXT PRIMARY KEY)''')

# create table for CIDR blocks if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS cidr_blocks (cidr TEXT PRIMARY KEY)''')

# Populate the CIDR blocks table
# Edit this toncontain IP addresses or networks in CIDR notation
cidr_blocks = [
    "192.168.0.0/24",
    "10.0.0.0/8",
    "172.16.0.0/12",
]

for cidr in cidr_blocks:
    try:
        c.execute("INSERT INTO cidr_blocks (cidr) VALUES (?)", (cidr,))
    except sqlite3.IntegrityError:
        pass

conn.commit()
