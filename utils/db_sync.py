## Usage
# python db_sync.py pull - to pull from supabase to local
# python db_sync.py push - to push from local to supabase

import os
import subprocess
import argparse
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_config(url):
    """Parse postgres URL into components."""
    result = urlparse(url)
    return {
        'host': result.hostname,
        'port': result.port or 5432,
        'user': result.username,
        'password': result.password,
        'database': result.path.lstrip('/')
    }

def run_cmd(cmd, env=None):
    """Run a shell command and handle errors."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=env
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error executing command: {cmd}")
            print(f"Error message: {stderr.decode('utf-8')}")
            return False
        return True
    except Exception as e:
        print(f"An exception occurred: {e}")
        return False

def confirm(message):
    """Ask the user to confirm an action."""
    question = f"{message} [y/N]: "
    sys.stdout.write(question)
    choice = input().lower()
    return choice == 'y'

def sync_db(source_url, target_url, schema='public'):
    """Sync data from source to target."""
    if not source_url or not target_url:
        print("Error: Source or Target URL not found in .env")
        return

    source = get_db_config(source_url)
    target = get_db_config(target_url)

    print(f"\n--- Syncing Database ---")
    print(f"Source: {source['host']}:{source['port']} ({source['database']})")
    print(f"Target: {target['host']}:{target['port']} ({target['database']})")
    print(f"Schema: {schema}")

    if not confirm("WARNING: This will overwrite data on the TARGET database. Proceed?"):
        print("Sync cancelled.")
        return

    # Set password for target psql
    env = os.environ.copy()
    
    # Dump from source
    print(f"Step 1: Dumping from source...")
    dump_env = env.copy()
    if source['password']:
        dump_env['PGPASSWORD'] = source['password']
    
    # -c for clean (drop before create), --if-exists, -n for schema
    dump_cmd = f"pg_dump -h {source['host']} -p {source['port']} -U {source['user']} -n {schema} -c --if-exists {source['database']}"
    
    # Set password for target
    print(f"Step 2: Restoring to target...")
    restore_env = env.copy()
    if target['password']:
        restore_env['PGPASSWORD'] = target['password']
    
    restore_cmd = f"psql -h {target['host']} -p {target['port']} -U {target['user']} -d {target['database']}"

    # Pipe dump directly to restore for efficiency
    full_cmd = f"{dump_cmd} | {restore_cmd}"
    
    # Note: We combine environments for the pipe
    combined_env = env.copy()
    if source['password']:
        combined_env['PGPASSWORD'] = source['password'] # Wait, this won't work perfectly for two different passwords in one pipe easily with one env var
    
    # Better to store dump in a temp file or run separately
    temp_file = "db_dump_temp.sql"
    try:
        print(f"Extracting source schema and data to {temp_file}...")
        if run_cmd(f"{dump_cmd} > {temp_file}", env=dump_env):
            print(f"Applying dump to target...")
            if run_cmd(f"{restore_cmd} < {temp_file}", env=restore_env):
                print("\nSUCCESS: Database sync complete!")
            else:
                print("\nFAILURE: Could not apply dump to target.")
        else:
            print("\nFAILURE: Could not dump from source.")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(description="SkillStack Database Sync Utility")
    parser.add_argument("action", choices=["push", "pull"], help="push (local -> supabase) or pull (supabase -> local)")
    parser.add_argument("--schema", default="public", help="Database schema to sync (default: public)")

    args = parser.parse_args()

    local_url = os.getenv("LOCAL_DATABASE_URL")
    supabase_url = os.getenv("SUPABASE_DATABASE_URL")

    if args.action == "pull":
        sync_db(supabase_url, local_url, args.schema)
    elif args.action == "push":
        sync_db(local_url, supabase_url, args.schema)

if __name__ == "__main__":
    main()