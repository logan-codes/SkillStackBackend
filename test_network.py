import socket

hostname = "db.doqbkbfepnukkreimzki.supabase.co"
try:
    ip = socket.gethostbyname(hostname)
    print(f"OK - DNS resolution: {hostname} -> {ip}")
except socket.gaierror as e:
    print(f"FAILED - DNS resolution: {e}")
    print("\nThis explains why the sync script cannot connect to Supabase.")
    print("Possible causes:")
    print("  1. No internet connection")
    print("  2. DNS server not configured")
    print("  3. Firewall blocking DNS/port 5432")
    print("  4. Corporate network restrictions")

local_host = "127.0.0.1"
try:
    socket.create_connection((local_host, 5432), timeout=5)
    print(f"OK - Local PostgreSQL (127.0.0.1:5432) is reachable")
except Exception as e:
    print(f"FAILED - Local PostgreSQL: {e}")
