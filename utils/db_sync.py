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
    """Run a shell command and FAIL HARD on error."""
    print(f"\n>>> Running: {cmd}\n")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=env
    )

    stdout, stderr = process.communicate()

    if stdout:
        print(stdout.decode())

    if process.returncode != 0:
        err_msg = stderr.decode()
        print(err_msg)
        raise RuntimeError(f"Command failed: {cmd}\nError: {err_msg}")

    return True


def confirm(message):
    """Ask the user to confirm an action."""
    choice = input(f"{message} [y/N]: ").lower()
    return choice == 'y'


def sync_db(source_url, target_url, schema='public'):
    """Sync data from source to target with full overwrite."""
    if not source_url or not target_url:
        print("Error: Source or Target URL not found in .env")
        return

    source = get_db_config(source_url)
    target = get_db_config(target_url)

    print("\n--- Syncing Database ---")
    print(f"Source: {source['host']}:{source['port']} ({source['database']})")
    print(f"Target: {target['host']}:{target['port']} ({target['database']})")
    print(f"Schema: {schema}")

    if not confirm("⚠️ WARNING: This will COMPLETELY WIPE the target database schema. Proceed?"):
        print("Sync cancelled.")
        return

    env = os.environ.copy()

    # ---------- STEP 1: DUMP ----------
    print("\nStep 1: Dumping source database...")

    dump_env = env.copy()
    if source['password']:
        dump_env['PGPASSWORD'] = source['password']

    dump_cmd = f"""
    pg_dump
    -h {source['host']}
    -p {source['port']}
    -U {source['user']}
    -n {schema}
    --clean
    --if-exists
    --no-owner
    --no-privileges
    {source['database']}
    """.strip().replace("\n", " ")

    temp_file = "db_dump_temp.sql"

    run_cmd(f"{dump_cmd} > {temp_file}", env=dump_env)

    # ---------- STEP 2: DROP SCHEMA ----------
    print("\nStep 2: Dropping existing schema on target...")

    restore_env = env.copy()
    if target['password']:
        restore_env['PGPASSWORD'] = target['password']

    drop_cmd = f"""
    psql
    -h {target['host']}
    -p {target['port']}
    -U {target['user']}
    -d {target['database']}
    -v ON_ERROR_STOP=1
    -c "DROP SCHEMA {schema} CASCADE; CREATE SCHEMA {schema};"
    """.strip().replace("\n", " ")

    run_cmd(drop_cmd, env=restore_env)

    # ---------- STEP 3: RESTORE ----------
    print("\nStep 3: Restoring dump to target...")

    restore_cmd = f"""
    psql
    -h {target['host']}
    -p {target['port']}
    -U {target['user']}
    -d {target['database']}
    -v ON_ERROR_STOP=1
    """.strip().replace("\n", " ")

    run_cmd(f"{restore_cmd} < {temp_file}", env=restore_env)

    # ---------- CLEANUP ----------
    if os.path.exists(temp_file):
        os.remove(temp_file)

    print("\n✅ SUCCESS: Database sync completed with FULL overwrite.")


def main():
    parser = argparse.ArgumentParser(description="Database Sync Utility")
    parser.add_argument("action", choices=["push", "pull"], help="push (local → remote) or pull (remote → local)")
    parser.add_argument("--schema", default="public", help="Schema to sync (default: public)")

    args = parser.parse_args()

    local_url = os.getenv("LOCAL_DATABASE_URL")
    supabase_pull_url = os.getenv("SUPABASE_PULL_URL", os.getenv("SUPABASE_DATABASE_URL"))
    supabase_push_url = os.getenv("SUPABASE_PUSH_URL", os.getenv("SUPABASE_DATABASE_URL"))

    if args.action == "pull":
        print(f"Using Supabase Pull URL for {args.action}...")
        try:
            sync_db(supabase_pull_url, local_url, args.schema)
        except RuntimeError as e:
            if "permission denied for sequence" in str(e):
                print("\n❌ Permission Denied Error Detected:")
                print("Your pull role lacks permission to read sequence values in Supabase.")
                print("Please run the following SQL command in your Supabase SQL Editor:")
                print(f"  GRANT SELECT ON ALL SEQUENCES IN SCHEMA {args.schema} TO current_pull_role;")
            else:
                raise
    elif args.action == "push":
        if not os.getenv("SUPABASE_PUSH_URL") and os.getenv("SUPABASE_DATABASE_URL"):
            print("⚠️ NOTE: Using SUPABASE_DATABASE_URL for pushing. If your role (e.g., dev1) is read-only, this will fail!")
            print("To fix this, define SUPABASE_PUSH_URL in your .env file with an admin-level postgres connection string.")
        print(f"Using Supabase Push URL for {args.action}...")
        try:
            sync_db(local_url, supabase_push_url, args.schema)
        except RuntimeError as e:
            if "permission denied" in str(e).lower() or "must be owner" in str(e).lower():
                print("\n❌ Permission Denied Error Detected during Push:")
                print("Your role does not have sufficient privileges to overwrite the database schema on Supabase.")
                print("Make sure your SUPABASE_PUSH_URL uses a role with push permissions (like the default 'postgres' user).")
            else:
                raise

if __name__ == "__main__":
    main()