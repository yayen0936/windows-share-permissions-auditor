from pypsrp.client import Client

import os
import datetime

SERVER = "LAB-DEWEY"
LOCAL_SCRIPT = r"C:\Scripts\file_share_permissions.py"
REMOTE_SCRIPT = r"C:\Scripts\file_share_permissions.py"
REMOTE_BASE_DIR = r"C:\Scripts"
REMOTE_LOG_DIR = r"C:\Scripts\logs"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOCAL_LOG = fr"C:\Scripts\logs\audit_{SERVER}_{timestamp}.txt"
REMOTE_LOG = fr"{REMOTE_LOG_DIR}\audit.txt"

PYTHON_PATH = r"C:\Scripts\python.exe"

def connect_to_server(server_name):
    # Connect to target server using Kerberos authentication
    print(f"[+] Connecting to {server_name} via Kerberos ...")
    client = Client(server_name, auth="kerberos", ssl=False, cert_validation=False)
    print("[+] Connection established.\n")
    return client

def ensure_remote_directory(client, path):
    # Ensure target directory exists on the remote server
    print(f"[+] Ensuring directory exists: {path}")
    client.execute_ps(f"New-Item -ItemType Directory -Path '{path}' -Force | Out-Null")
    print("[+] Directory verified.\n")

def transfer_script(client, local_path, remote_path):
    # Transfer local script to remote server
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")

    print(f"[+] Sending {os.path.basename(local_path)} to {remote_path} ...")
    client.copy(local_path, remote_path)
    print("[+] Script successfully transferred.\n")

def execute_remote_script(client, script_path, log_path):
    # Execute the transferred script remotely and save output to a log file
    print(f"[+] Executing {os.path.basename(script_path)} on {SERVER} ...")

    command = (
        f"& '{PYTHON_PATH}' -u '{script_path}' "
        f"| Out-File -FilePath '{log_path}' -Encoding utf8 -Force"
    )

    stdout, stderr, rc = client.execute_ps(command)
    print("[+] Execution complete. Return code:", rc)

    # Decode stderr properly if any
    if stderr and hasattr(stderr, "error"):
        print("[!] Remote error output:")
        for err in stderr.error:
            print(err)

    # Verify that the remote log file exists
    verify_cmd = f"Test-Path '{log_path}'"
    result, _, _ = client.execute_ps(verify_cmd)
    if "True" not in result:
        print(f"[!] Remote log file was not created at {log_path}. Skipping fetch.")
        print("STDOUT:\n", stdout)
        return False

    print("[+] Remote log file verified.\n")
    return True

def fetch_remote_log(client, remote_log, local_log):
    # Download the output log from the server to the client
    print(f"[+] Retrieving remote log from {SERVER} ...")
    os.makedirs(os.path.dirname(local_log), exist_ok=True)

    try:
        client.fetch(remote_log, local_log)
        print(f"[+] Retrieved remote log -> {local_log}\n")
    except Exception as e:
        print(f"[!] Could not fetch log file ({remote_log}). {e}")

def main():
    print(f"=== Remote Audit: {SERVER} ===\n")

    # Step 1: Connect to remote server
    client = connect_to_server(SERVER)

    # Step 2: Ensure directories exist
    ensure_remote_directory(client, REMOTE_BASE_DIR)
    ensure_remote_directory(client, REMOTE_LOG_DIR)

    # Step 3: Transfer audit script
    transfer_script(client, LOCAL_SCRIPT, REMOTE_SCRIPT)

    # Step 4: Execute script remotely
    success = execute_remote_script(client, REMOTE_SCRIPT, REMOTE_LOG)

    # Step 5: Retrieve log file from server (only if success)
    if success:
        fetch_remote_log(client, REMOTE_LOG, LOCAL_LOG)
    else:
        print("[!] Skipping log fetch because remote execution failed.\n")

    print("=== Audit complete ===\n")

if __name__ == "__main__":
    main()