import subprocess  # used to execute PowerShell and system commands

# ---------------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------------
server = "LAB-DEWEY"
folder_path = "E:\\"  # root path for NTFS remediation

# ---------------------------------------------------------------------
# class: defines a blueprint for remediating SMB shares and NTFS permissions
# ---------------------------------------------------------------------
class FileShareRemediator:
    def __init__(self):
        """Initialize remediator using global server and folder path."""
        self.server = server
        self.folder_path = folder_path

    # -------------------------------
    # function: runs a PowerShell command
    # -------------------------------
    def run_powershell(self, ps_command, description):
        print("=" * 80)
        print(f"[ {description} on {self.server} ]")
        print("=" * 80)

        proc = subprocess.Popen(
            ps_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output, error = proc.communicate()

        if output:
            print(output)
        if error:
            print(f"[!] Errors:\n{error}")

    # -------------------------------
    # function: remediate SMB share permissions
    # -------------------------------
    def remediate_smb_shares(self):
        ps_command = r'''
        $remove = @(
            "Everyone",
            "Authenticated Users",
            "BUILTIN\Users"
        )

        Get-SmbShare | Where-Object { $_.Name -notlike "*$" } | ForEach-Object {
            $share = $_.Name
            Write-Host "Processing share: $share"

            foreach ($r in $remove) {
                try {
                    Revoke-SmbShareAccess -Name $share -AccountName $r -Force -ErrorAction Stop
                    Write-Host "  Removed: $r"
                } catch {}
            }

            Grant-SmbShareAccess -Name $share -AccountName "BUILTIN\Administrators" -AccessRight Full -Force
            Grant-SmbShareAccess -Name $share -AccountName "NT AUTHORITY\SYSTEM" -AccessRight Full -Force
        }
        '''
        self.run_powershell(ps_command, "SMB Share Remediation")

    # -------------------------------
    # function: remediate NTFS permissions
    # -------------------------------
    def remediate_ntfs(self):
        print("=" * 80)
        print(f"[ NTFS Remediation on {self.folder_path} ]")
        print("=" * 80)

        # Remove broad identities
        subprocess.run(
            ["icacls", self.folder_path, "/remove", "Everyone", "/T", "/C"],
            capture_output=True
        )
        subprocess.run(
            ["icacls", self.folder_path, "/remove", "Users", "/T", "/C"],
            capture_output=True
        )
        subprocess.run(
            ["icacls", self.folder_path, "/remove", "Authenticated Users", "/T", "/C"],
            capture_output=True
        )

        # Grant SYSTEM and Administrators full control
        subprocess.run(
            ["icacls", self.folder_path, "/grant", "SYSTEM:(OI)(CI)F", "/T", "/C"],
            capture_output=True
        )
        subprocess.run(
            ["icacls", self.folder_path, "/grant", "Administrators:(OI)(CI)F", "/T", "/C"],
            capture_output=True
        )

        print("[+] NTFS remediation completed")

    # -------------------------------
    # function: performs full remediation workflow
    # -------------------------------
    def run_full_remediation(self):
        print(f"=== Starting Permissions Remediation for {self.server} ===\n")

        self.remediate_smb_shares()
        self.remediate_ntfs()

        print(f"\n=== Remediation Complete for {self.server} ===\n")


# ---------------------------------------------------------------------
# function: main entry point
# ---------------------------------------------------------------------
def main():
    remediator = FileShareRemediator()
    remediator.run_full_remediation()

# entry point
if __name__ == "__main__":
    main()