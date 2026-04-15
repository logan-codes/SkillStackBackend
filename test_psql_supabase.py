import subprocess
import os

os.environ["PGPASSWORD"] = "xKSP5CQyudoqH85y"
cmd = 'psql -h db.doqbkbfepnukkreimzki.supabase.co -p 5432 -U postgres -d postgres -c "SELECT 1"'
result = subprocess.run(cmd, capture_output=True, shell=True, timeout=15)
print("Exit code:", result.returncode)
print("Output:", result.stdout.decode()[:500] if result.stdout else "")
print("Error:", result.stderr.decode()[:500] if result.stderr else "")
