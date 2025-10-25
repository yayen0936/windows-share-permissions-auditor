from pypsrp.client import Client

import os

def main():
    # Step 1: Connect to target server via Kerberos authentication
    client = Client("LAB-DEWEY", auth="kerberos", ssl=False, cert_validation=False)

    # Step 2: Ensure target directory exists on the remote server
    client.execute_ps("New-Item -ItemType Directory -Path C:\\Scripts -Force | Out-Null")

    # Step 3: Local Python script to send to the server
    local_script = r"C:\Scripts\file-share_permissions2.py"

    # Step 4: Remote destination path on target server
    remote_script = r"C:\Scripts\file-share_permissions2.py"

    # Step 5: Check if the file exists in the directory
    if not os.path.exists(local_script):
        raise FileNotFoundError(f"Local file not found: {local_script}")

    # Step 6: Send the python script from client to server
    print(f"[+] Sending {os.path.basename(local_script)} to {remote_script} ...")
    client.copy(local_script, remote_script)
    print("[+] Done — python script successfully transferred to remote server.")

    # Step 7: Execute the python script save output to a txt file
    remote_log = r"C:\Scripts\audit.txt"
    print("[+] Executing remote script on LAB-DEWEY ...")
    command = f"& 'C:\\Scripts\\python.exe' -u '{remote_script}' *> '{remote_log}'"
    stdout, stderr, rc = client.execute_ps(command)
    print("[+] Execution complete. Return code:", rc)

    # Step 8: Download the output file and send back to client for analysis
    local_log = r"C:\Scripts\Logs\audit_LAB-DEWEY.txt"
    os.makedirs(os.path.dirname(local_log), exist_ok=True)
    client.fetch(remote_log, local_log)
    print(f"[+] Retrieved remote log -> {local_log}")

if __name__ == "__main__":
    main()