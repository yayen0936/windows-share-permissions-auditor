from pypsrp.client import Client
import os
import datetime

# ---------------------------------------------------------------------
# Global Configuration
# ---------------------------------------------------------------------
SERVER = "LAB-DEWEY"
LOCAL_SCRIPT = r"C:\Scripts\file_share_permissions.py"
REMOTE_SCRIPT = r"C:\Scripts\file_share_permissions.py"
REMOTE_BASE_DIR = r"C:\Scripts"
REMOTE_LOG_DIR = r"C:\Scripts\logs"
PYTHON_PATH = r"C:\Scripts\path\python.exe"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
timestamp_str = str(timestamp)
LOCAL_LOG = fr"C:\Scripts\logs\audit_{SERVER}_{timestamp_str}.txt"
REMOTE_LOG = fr"{REMOTE_LOG_DIR}\audit.txt"

# ---------------------------------------------------------------------
# Class Definition
# ---------------------------------------------------------------------
class RemoteAuditor:
    def __init__(self, server, python_path, local_script, remote_script, remote_base, remote_log_dir):
        """Initialize RemoteAuditor with target server and paths."""
        self.server = server
        self.python_path = python_path
        self.local_script = local_script
        self.remote_script = remote_script
        self.remote_base = remote_base
        self.remote_log_dir = remote_log_dir
        self.remote_log = os.path.join(remote_log_dir, "audit.txt")
        self.local_log = fr"C:\Scripts\logs\audit_{server}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.client = None

    # -------------------------------
    # Step 1: Connect to Remote Server
    # -------------------------------
    def connect(self):
        print(f"[+] Connecting to {self.server} via Kerberos ...")
        self.client = Client(self.server, auth="kerberos", ssl=False, cert_validation=False)
        print("[+] Connection established.\n")

    # -------------------------------
    # Step 2: Ensure Remote Directories Exist
    # -------------------------------
    def ensure_remote_directory(self, path):
        print(f"[+] Ensuring directory exists: {path}")
        self.client.execute_ps(f"New-Item -ItemType Directory -Path '{path}' -Force | Out-Null")
        print("[+] Directory verified.\n")

    # -------------------------------
    # Step 3: Transfer Local Script
    # -------------------------------
    def transfer_script(self):
        if not os.path.exists(self.local_script):
            raise FileNotFoundError(f"Local file not found: {self.local_script}")

        print(f"[+] Sending {os.path.basename(self.local_script)} to {self.remote_script} ...")
        self.client.copy(self.local_script, self.remote_script)
        print("[+] Script successfully transferred.\n")

    # -------------------------------
    # Step 4: Execute Script Remotely
    # -------------------------------
    def execute_remote_script(self):
        print(f"[+] Executing {os.path.basename(self.remote_script)} on {self.server} ...")

        command = (
            f"& '{self.python_path}' -u '{self.remote_script}' "
            f"| Out-File -FilePath '{self.remote_log}' -Encoding utf8 -Force"
        )

        stdout, stderr, rc = self.client.execute_ps(command)
        print("[+] Execution complete. Return code:", rc)

        if stderr and hasattr(stderr, "error"):
            print("[!] Remote error output:")
            for err in stderr.error:
                print(err)

        verify_cmd = f"Test-Path '{self.remote_log}'"
        result, _, _ = self.client.execute_ps(verify_cmd)
        if "True" not in result:
            print(f"[!] Remote log file not created at {self.remote_log}.")
            print("STDOUT:\n", stdout)
            return False

        print("[+] Remote log file verified.\n")
        return True

    # -------------------------------
    # Step 5: Fetch Remote Log
    # -------------------------------
    def fetch_remote_log(self):
        print(f"[+] Retrieving remote log from {self.server} ...")
        os.makedirs(os.path.dirname(self.local_log), exist_ok=True)

        try:
            self.client.fetch(self.remote_log, self.local_log)
            print(f"[+] Retrieved remote log -> {self.local_log}\n")
        except Exception as e:
            print(f"[!] Could not fetch log file ({self.remote_log}). {e}")

    # -------------------------------
    # Full Workflow
    # -------------------------------
    def run_full_audit(self):
        print(f"=== Remote Audit: {self.server} ===\n")

        self.connect()
        self.ensure_remote_directory(self.remote_base)
        self.ensure_remote_directory(self.remote_log_dir)
        self.transfer_script()

        success = self.execute_remote_script()
        if success:
            self.fetch_remote_log()
        else:
            print("[!] Skipping log fetch due to execution failure.\n")

        print("=== Audit complete ===\n")

# ---------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------
def main():
    auditor = RemoteAuditor(
        server=SERVER,
        python_path=PYTHON_PATH,
        local_script=LOCAL_SCRIPT,
        remote_script=REMOTE_SCRIPT,
        remote_base=REMOTE_BASE_DIR,
        remote_log_dir=REMOTE_LOG_DIR,
    )

    auditor.run_full_audit()

if __name__ == "__main__":
    main()