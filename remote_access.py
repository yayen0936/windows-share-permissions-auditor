from pypsrp.client import Client

import os

def main():
    # Step 1: Specify the target server
    client = Client("LAB-DEWEY", auth="kerberos", ssl=False, cert_validation=False)

    # Step 2: Ensure target directory exists on the remote server
    client.execute_ps("New-Item -ItemType Directory -Path C:\\Scripts -Force | Out-Null")

    # Step 3: Local Python script you want to send
    local_script = r"C:\Scripts\file-share_permissions.py"

    # Step 4: Remote destination path on target server
    remote_script = r"C:\Scripts\file-share_permissions.py"

    # Step 5: Check if the file exists in the directory
    if not os.path.exists(local_script):
        raise FileNotFoundError(f"Local file not found: {local_script}")

    # Step 6: Send the file from client to server
    print(f"[+] Sending {os.path.basename(local_script)} to {remote_script} ...")
    client.copy(local_script, remote_script)
    print("[+] Done — file successfully copied to remote server.")

if __name__ == "__main__":
    main()