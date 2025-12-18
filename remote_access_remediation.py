from pypsrp.client import Client
import os
import datetime
import sys

# ---------------------------------------------------------------------
# Global Configuration
# ---------------------------------------------------------------------
SERVER = "LAB-DEWEY"

PYTHON_PATH = r"C:\Users\Administrator.itsadlab\AppData\Local\Programs\Python\Python314\python.exe"

REMOTE_BASE_DIR = r"C:\Scripts"
REMOTE_LOG_DIR = r"C:\Scripts\logs"

# Remediation script
LOCAL_REMEDIATION_SCRIPT = (
    r"C:\Users\yayen.itsadlab\Documents"
    r"\windows-share-permissions-auditor\permissions_remediation.py"
)
REMOTE_REMEDIATION_SCRIPT = r"C:\Scripts\permissions_remediation.py"


# ---------------------------------------------------------------------
# class: orchestrates remote remediation execution
# ---------------------------------------------------------------------
class RemoteRemediator:
    def __init__(self, server):
        self.server = server
        self.client = None

    # -------------------------------
    # Connect via WinRM (Kerberos)
    # -------------------------------
    def connect(self):
        print(f"[+] Connecting to {self.server} via Kerberos ...")
        self.client = Client(
            self.server,
            auth="kerberos",
            ssl=False,
            cert_validation=False
        )
        print("[+] Connection established.\n")

    # -------------------------------
    # Ensure remote directory exists
    # -------------------------------
    def ensure_remote_directory(self, path):
        print(f"[+] Ensuring directory exists: {path}")
        self.client.execute_ps(
            f"New-Item -ItemType Directory -Path '{path}' -Force | Out-Null"
        )
        print("[+] Directory verified.\n")

    # -------------------------------
    # Transfer remediation script
    # -------------------------------
    def transfer_script(self):
        if not os.path.exists(LOCAL_REMEDIATION_SCRIPT):
            print(f"[!] Local remediation script not found: {LOCAL_REMEDIATION_SCRIPT}")
            sys.exit(1)

        print(
            f"[+] Uploading {os.path.basename(LOCAL_REMEDIATION_SCRIPT)} "
            f"-> {REMOTE_REMEDIATION_SCRIPT}"
        )

        self.client.copy(LOCAL_REMEDIATION_SCRIPT, REMOTE_REMEDIATION_SCRIPT)
        print("[+] Transfer complete.\n")

    # -------------------------------
    # Execute remediation script (CSV OUTPUT)
    # -------------------------------
    def execute_remediation(self, remote_log_csv):
        print(f"[+] Executing permissions_remediation.py on {self.server}")

        command = (
            f"$py = '{PYTHON_PATH}'; "
            f"& $py -u '{REMOTE_REMEDIATION_SCRIPT}' "
            f"| Out-File -FilePath '{remote_log_csv}' -Encoding utf8 -Force"
        )

        stdout, stderr, success = self.client.execute_ps(command)

        print("[+] Remediation execution completed.")
        print("[i] PowerShell success flag:", success)

        if stderr and hasattr(stderr, "error"):
            print("[!] Remote PowerShell errors:")
            for err in stderr.error:
                print(err)

        # Verify CSV log exists
        verify_cmd = f"Test-Path '{remote_log_csv}'"
        result, _, _ = self.client.execute_ps(verify_cmd)

        if "True" not in result:
            print(f"[!] CSV remediation log not created: {remote_log_csv}")
            print("STDOUT:\n", stdout)
            return False

        print("[+] Remote remediation CSV verified.\n")
        return True

    # -------------------------------
    # Fetch remediation CSV
    # -------------------------------
    def fetch_log(self, remote_log_csv, local_log_csv):
        print(f"[+] Downloading remediation CSV from {self.server}")
        os.makedirs(os.path.dirname(local_log_csv), exist_ok=True)

        try:
            self.client.fetch(remote_log_csv, local_log_csv)
            print(f"[+] Remediation CSV saved locally: {local_log_csv}\n")
        except Exception as e:
            print(f"[!] Failed to fetch remediation CSV: {e}")

    # -------------------------------
    # Full remediation workflow
    # -------------------------------
    def run_remediation(self):
        print(f"=== Remote Remediation for {self.server} ===\n")

        self.connect()
        self.ensure_remote_directory(REMOTE_BASE_DIR)
        self.ensure_remote_directory(REMOTE_LOG_DIR)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        remote_log_csv = f"{REMOTE_LOG_DIR}\\remediation.csv"

        local_log_csv = os.path.join(
            r"C:\Users\yayen.itsadlab\documents\windows-share-permissions-auditor\logs",
            f"remediation_{self.server}_{timestamp}.csv"
        )

        self.transfer_script()
        if self.execute_remediation(remote_log_csv):
            self.fetch_log(remote_log_csv, local_log_csv)

        print("=== Remediation Complete ===\n")


# ---------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------
def main():
    remediator = RemoteRemediator(SERVER)
    remediator.run_remediation()


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"[!] Script failed: {e}")
        sys.exit(1)
