import subprocess

# ---------------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------------
server = "LAB-DEWEY"
folder_path = "E:\\"

# ---------------------------------------------------------------------
# Class Definition
# ---------------------------------------------------------------------
class FileShareAuditor:
    def __init__(self):
        """Initialize auditor using global server and folder path."""
        self.server = server
        self.folder_path = folder_path

    # -------------------------------
    # Utility: Run PowerShell Command
    # -------------------------------
    def run_powershell(self, ps_command, description):
        """Execute a PowerShell command and handle errors."""
        print("=" * 80)
        print(f"[ {description} on {self.server} ]")
        print("=" * 80)
        try:
            output = subprocess.check_output(ps_command, shell=True, text=True, stderr=subprocess.STDOUT)
            print(output)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to run: {description}")
            print(e.output)

    # -------------------------------
    # SMB Shares
    # -------------------------------
    def get_smb_share(self):
        ps_command = 'powershell -NoProfile -Command "Get-SmbShare | Format-Table -AutoSize"'
        self.run_powershell(ps_command, "SMB Shares")

    # -------------------------------
    # SMB Share ACLs
    # -------------------------------
    def get_share_acl(self):
        ps_command = (
            'powershell -NoProfile -Command "Get-SmbShare | '
            'ForEach-Object { Get-SmbShareAccess -Name $_.Name | Format-Table -AutoSize }"'
        )
        self.run_powershell(ps_command, "SMB Share-Level ACLs")

    # -------------------------------
    # NTFS ACLs
    # -------------------------------
    def get_ntfs_acl(self):
        ps_command = (
            f'powershell -NoProfile -Command "'
            f', (Get-Item \'{self.folder_path}\') + (Get-ChildItem \'{self.folder_path}\' -Recurse -ErrorAction SilentlyContinue) | '
            f'ForEach-Object {{ '
            f'try {{ '
            f'$acl = Get-Acl $_.FullName; '
            f'foreach ($entry in $acl.Access) {{ '
            f'[PSCustomObject]@{{ '
            f'Path=$_.FullName; '
            f'Identity=$entry.IdentityReference; '
            f'Rights=$entry.FileSystemRights; '
            f'Inheritance=$entry.InheritanceFlags; '
            f'Propagation=$entry.PropagationFlags; '
            f'AccessControl=$entry.AccessControlType '
            f'}} '
            f'}} '
            f'}} catch {{ Write-Host \\"Access denied: $($_.FullName)\\" }} '
            f'}} | Format-Table -AutoSize"'
        )
        self.run_powershell(ps_command, f"NTFS File-Level ACLs ({self.folder_path})")

    # -------------------------------
    # Full Audit Workflow
    # -------------------------------
    def run_full_audit(self):
        print(f"=== Starting File Share and NTFS Audit for {self.server} ===\n")

        self.get_smb_share()
        self.get_share_acl()
        self.get_ntfs_acl()

        print(f"\n=== Audit Complete for {self.server} ===\n")

# ---------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------
def main():
    auditor = FileShareAuditor()
    auditor.run_full_audit()

if __name__ == "__main__":
    main()