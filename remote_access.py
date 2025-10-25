from pypsrp.client import Client
import os        # module: used for path operations and directory handling
import datetime
import sys       # module: used for exit control and program termination

# ---------------------------------------------------------------------
# Global Configuration
# ---------------------------------------------------------------------
SERVER = "LAB-DEWEY"
LOCAL_SCRIPT = r"C:\Scripts\file_share_permissions.py"
REMOTE_SCRIPT = r"C:\Scripts\file_share_permissions.py"
REMOTE_BASE_DIR = r"C:\Scripts"
REMOTE_LOG_DIR = r"C:\Scripts\logs"
PYTHON_PATH = r"C:\Users\Administrator.itsadlab\AppData\Local\Programs\Python\Python314\python.exe"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
timestamp_str = str(timestamp)  # casting: converting timestamp into string format
LOCAL_LOG = fr"C:\Scripts\logs\audit_{SERVER}_{timestamp_str}.txt"
REMOTE_LOG = fr"{REMOTE_LOG_DIR}\audit.txt"

# ---------------------------------------------------------------------
# class: defines a blueprint for remote auditing operations
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
    # function: connects to a remote server using Kerberos authentication
    # -------------------------------
    def connect(self):
        print(f"[+] Connecting to {self.server} via Kerberos ...")
        self.client = Client(self.server, auth="kerberos", ssl=False, cert_validation=False)
        print("[+] Connection established.\n")

    # -------------------------------
    # function: ensures that the required directory exists on the remote server
    # -------------------------------
    def ensure_remote_directory(self, path):
        print(f"[+] Ensuring directory exists: {path}")
        self.client.execute_ps(f"New-Item -ItemType Directory -Path '{path}' -Force | Out-Null")  # file handling: creates directory remotely
        print("[+] Directory verified.\n")

    # -------------------------------
    # function: transfers the Python script from local to remote server
    # -------------------------------
    def transfer_script(self):
        if not os.path.exists(self.local_script):  # module os: checks for local file existence
            print(f"[!] Local file not found: {self.local_script}")
            sys.exit(1)  # module sys: exits if file is missing

        print(f"[+] Sending {os.path.basename(self.local_script)} to {self.remote_script} ...")
        self.client.copy(self.local_script, self.remote_script)  # file handling: uploads local file to remote server
        print("[+] Script successfully transferred.\n")

    # -------------------------------
    # function: executes the script remotely using PowerShell
    # -------------------------------
    def execute_remote_script(self):
        print(f"[+] Executing {os.path.basename(self.remote_script)} on {self.server} ...")

        command = (
            f"$py = '{self.python_path}'; "
            f"& $py -u '{self.remote_script}' "
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
        return True  # file handling: ensures remote log file exists

    # -------------------------------
    # function: downloads the remote log file to local system
    # -------------------------------
    def fetch_remote_log(self):
        print(f"[+] Retrieving remote log from {self.server} ...")
        os.makedirs(os.path.dirname(self.local_log), exist_ok=True)  # module os: creates local log directory if missing

        try:
            self.client.fetch(self.remote_log, self.local_log)  # file handling: retrieves remote log to local system
            print(f"[+] Retrieved remote log -> {self.local_log}\n")
        except Exception as e:
            print(f"[!] Could not fetch log file ({self.remote_log}). {e}")

    # -------------------------------
    # function: performs the full workflow for the remote audit
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
# function: main entry point of the program
# ---------------------------------------------------------------------
def main():
    # class object: creates an instance of RemoteAuditor
    auditor = RemoteAuditor(
        server=SERVER,
        python_path=PYTHON_PATH,
        local_script=LOCAL_SCRIPT,
        remote_script=REMOTE_SCRIPT,
        remote_base=REMOTE_BASE_DIR,
        remote_log_dir=REMOTE_LOG_DIR,
    )

    auditor.run_full_audit()  # function call: runs the full audit process

# entry point: ensures script runs only when executed directly
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)  # module sys: exits the program successfully
    except Exception as e:
        print(f"[!] Script failed: {e}")
        sys.exit(1)  # module sys: exits the program with error status
