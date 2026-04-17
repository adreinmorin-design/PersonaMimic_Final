import subprocess
import os
import sys

# DATABASE_URL_REMOTE = "postgresql://postgres:MimicEngine_2026_Industrial!@34.21.53.147:5432/postgres?sslmode=require"
REMOTE_HOST = "34.21.53.147"
REMOTE_USER = "postgres"
REMOTE_DB = "postgres"
REMOTE_PASS = "MimicEngine_2026_Industrial!"

LOCAL_NAMESPACE = "persona-mimic"
LOCAL_POD = "postgres-0"
LOCAL_USER = "mimic"
LOCAL_DB = "personamimic"

def run_migration():
    print(f"--- STARTING NEURAL DATA MIGRATION ---")
    
    # Set remote password for pg_dump
    os.environ["PGPASSWORD"] = REMOTE_PASS
    
    # 1. Verification: Is the local pod ready?
    check_pod = subprocess.run(
        ["kubectl", "get", "pod", LOCAL_POD, "-n", LOCAL_NAMESPACE],
        capture_output=True, text=True
    )
    if "Running" not in check_pod.stdout:
        print(f"Error: Local pod {LOCAL_POD} is not running. Please run 'kubectl apply -f k8s/' first.")
        sys.exit(1)

    print(f"[1/2] Dumping remote data from {REMOTE_HOST}...")
    
    # 2. Pipe Dump to Restore
    # Note: We use -c (clean) to drop objects before creating them in the new DB, 
    # but since this is a fresh DB we just need the dump.
    dump_cmd = [
        "pg_dump", 
        "-h", REMOTE_HOST, 
        "-U", REMOTE_USER, 
        "-d", REMOTE_DB,
        "--no-owner", "--no-privileges"
    ]
    
    restore_cmd = [
        "kubectl", "exec", "-i", LOCAL_POD, "-n", LOCAL_NAMESPACE, "--", 
        "psql", "-U", LOCAL_USER, "-d", LOCAL_DB
    ]

    try:
        p1 = subprocess.Popen(dump_cmd, stdout=subprocess.PIPE)
        p2 = subprocess.run(restore_cmd, stdin=p1.stdout, capture_output=True, text=True)
        p1.stdout.close()
        
        if p2.returncode == 0:
            print("[2/2] Data Sync complete. Local Neural Hive is now persistent.")
        else:
            print(f"Restore Error: {p2.stderr}")
            
    except Exception as e:
        print(f"Migration Failed: {e}")

if __name__ == "__main__":
    run_migration()
