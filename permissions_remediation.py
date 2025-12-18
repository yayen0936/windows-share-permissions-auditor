import subprocess  # used to execute PowerShell and system commands

# ---------------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------------
server = "LAB-DEWEY"

# Explicit remediation targets ONLY (single source of truth)
TARGET_FOLDERS = [
    r"E:\Backups",
    r"E:\IT",
    r"E:\ITSC-203 - Scripting",
    r"E:\Public"
]

# Explicit exception folder (must be in TARGET_FOLDERS)
student_folder = r"E:\ITSC-203 - Scripting"
student_group = "Students"

admin_group = "BUILTIN\\Administrators"
system_account = "SYSTEM"


# ---------------------------------------------------------------------
# class: defines a blueprint for remediating SMB shares and NTFS permissions
# ---------------------------------------------------------------------
class FileShareRemediator:
    def __init__(self):
        self.server = server

    # -------------------------------
    # function: runs a PowerShell command (safe invocation)
    # -------------------------------
    def run_powershell(self, ps_command, description):
        print("=" * 80)
        print(f"[ {description} on {self.server} ]")
        print("=" * 80)

        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_command],
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
    # function: remediate SMB share permissions (FIXED)
    # -------------------------------
    def remediate_smb_shares(self):
        ps_command = rf'''
        $allowedShares = @(
            "Backups",
            "IT",
            "ITSC-203 - Scripting",
            "Public"
        )

        foreach ($share in Get-SmbShare | Where-Object {{ $allowedShares -contains $_.Name }}) {{

            Write-Host "Processing share: $($share.Name)"

            # Remove ALL Everyone ACEs (Allow + Deny)
            Get-SmbShareAccess -Name $share.Name |
                Where-Object {{ $_.AccountName -eq "Everyone" }} |
                ForEach-Object {{
                    Revoke-SmbShareAccess -Name $share.Name -AccountName "Everyone" -Force
                }}

            # Remove other broad groups
            foreach ($acct in @("Authenticated Users", "BUILTIN\Users")) {{
                try {{
                    Revoke-SmbShareAccess -Name $share.Name -AccountName $acct -Force
                }} catch {{}}
            }}

            # Grant baseline admin access
            Grant-SmbShareAccess -Name $share.Name -AccountName "{admin_group}" -AccessRight Full -Force
            Grant-SmbShareAccess -Name $share.Name -AccountName "NT AUTHORITY\SYSTEM" -AccessRight Full -Force
        }}

        # Students RW access ONLY for ITSC-203 - Scripting
        if (Get-SmbShare | Where-Object {{ $_.Path -eq "{student_folder}" }}) {{
            $s = (Get-SmbShare | Where-Object {{ $_.Path -eq "{student_folder}" }}).Name
            Grant-SmbShareAccess -Name $s -AccountName "{student_group}" -AccessRight Change -Force
            Write-Host "Granted Students RW access to share: $s"
        }}
        '''
        self.run_powershell(ps_command, "SMB Share Remediation")

    # -------------------------------
    # function: remediate NTFS permissions (TARGETED ONLY – unchanged)
    # -------------------------------
    def remediate_ntfs(self):
        print("=" * 80)
        print("[ NTFS Remediation – Targeted Folders Only ]")
        print("=" * 80)

        for folder in TARGET_FOLDERS:
            print(f"\n[+] Processing folder: {folder}")

            if subprocess.run(
                ["cmd", "/c", f'if exist "{folder}" exit 0'],
                capture_output=True
            ).returncode != 0:
                print(f"[!] Folder not found, skipping: {folder}")
                continue

            # Remove broad access
            subprocess.run(["icacls", folder, "/remove", "Everyone", "/T", "/C"])
            subprocess.run(["icacls", folder, "/remove", "Authenticated Users", "/T", "/C"])
            subprocess.run(["icacls", folder, "/remove", "BUILTIN\\Users", "/T", "/C"])

            # Grant SYSTEM and Administrators
            subprocess.run(["icacls", folder, "/grant", f"{system_account}:(OI)(CI)F", "/T", "/C"])
            subprocess.run(["icacls", folder, "/grant", f"{admin_group}:(OI)(CI)F", "/T", "/C"])

            # Student exception ONLY for ITSC-203
            if folder == student_folder:
                subprocess.run([
                    "icacls", folder,
                    "/grant:r", f"{student_group}:(OI)(CI)M",
                    "/C"
                ])
                print(f"[+] Granted Students RW access to {folder}")

        print("\n[+] Targeted NTFS remediation completed")

    # -------------------------------
    # function: full remediation workflow
    # -------------------------------
    def run_full_remediation(self):
        print(f"=== Starting Permissions Remediation for {self.server} ===\n")

        self.remediate_smb_shares()
        self.remediate_ntfs()

        print(f"\n=== Remediation Complete for {self.server} ===\n")


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------
def main():
    remediator = FileShareRemediator()
    remediator.run_full_remediation()


if __name__ == "__main__":
    main()
