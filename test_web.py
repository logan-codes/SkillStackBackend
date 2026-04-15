import subprocess

result = subprocess.run(
    'curl -s -o /dev/null -w "%{http_code}" https://supabase.com',
    capture_output=True,
    shell=True,
    timeout=10,
)
print("Supabase website status:", result.stdout.decode().strip() or "OK")
