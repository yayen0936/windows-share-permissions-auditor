import subprocess  # module: used to execute PowerShell commands through the system shell

# ---------------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------------
server = "LAB-DEWEY"
folder_path = "E:\\"  # represents the folder path to scan for permissions

# ---------------------------------------------------------------------
# class: defines a blueprint for auditing SMB shares and NTFS permissions
# ---------------------------------------------------------------------
class FileShareAuditor:
    def __init__(self):
        """Initialize auditor using global server and folder path."""
        self.server = server
        self.folder_path = folder_path

    # -------------------------------
    # function: runs a PowerShell command and handles exceptions
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
    # function: retrieves a list of all SMB shares on the system
    # -------------------------------
    def get_smb_share(self):
        ps_command = 'powershell -NoProfile -Command "Get-SmbShare | Format-Table -AutoSize"'
        self.run_powershell(ps_command, "SMB Shares")

    # -------------------------------
    # function: retrieves the access control lists (ACLs) for each SMB share
    # -------------------------------
    def get_share_acl(self):
        ps_command = (
            'powershell -NoProfile -Command "Get-SmbShare | '
            'ForEach-Object { Get-SmbShareAccess -Name $_.Name | Format-Table -AutoSize }"'
        )
        self.run_powershell(ps_command, "SMB Share-Level ACLs")

    # -------------------------------
    # function: retrieves NTFS permissions for the specified folder path
    # -------------------------------
    def get_ntfs_acl(self):
        ps_command = (
            f'powershell -NoProfile -Command "'
            f', (Get-Item \'{self.folder_path}\') + (Get-ChildItem \'{self.folder_path}\' -Recurse -ErrorAction SilentlyContinue) | '
            f'ForEach-Object {{ '
            f'try {{ '
            f'$acl = Get-Acl $_.FullName; '  # file metadata: reading file ACLs via PowerShell
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
    # function: performs the full SMB and NTFS audit workflow
    # -------------------------------
    def run_full_audit(self):
        print(f"=== Starting File Share and NTFS Audit for {self.server} ===\n")

        self.get_smb_share()    # function call: enumerate SMB shares
        self.get_share_acl()    # function call: get SMB permissions
        self.get_ntfs_acl()     # function call: get NTFS permissions

        print(f"\n=== Audit Complete for {self.server} ===\n")

# ---------------------------------------------------------------------
# function: serves as the main entry point for the script
# ---------------------------------------------------------------------
def main():
    auditor = FileShareAuditor()  # class object: creates an instance of FileShareAuditor
    auditor.run_full_audit()      # function call: runs the full audit workflow

# entry point: ensures the script only runs when executed directly
if __name__ == "__main__":
    main()