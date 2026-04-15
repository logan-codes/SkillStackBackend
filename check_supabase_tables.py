import os
from dotenv import load_dotenv

load_dotenv()
import psycopg2
from urllib.parse import urlparse

url = os.getenv("SUPABASE_DATABASE_URL")
p = urlparse(url)

print(f"Connecting to Supabase: {p.hostname}:{p.port}")

conn = psycopg2.connect(
    host=p.hostname,
    port=p.port,
    user=p.username,
    password=p.password,
    database=p.path.lstrip("/"),
)

cur = conn.cursor()
cur.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"
)
tables = [r[0] for r in cur.fetchall()]

print(f"\nSupabase tables ({len(tables)}):")
for t in tables:
    print(f"  - {t}")

conn.close()
