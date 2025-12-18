import subprocess  # used to execute PowerShell and system commands

# ---------------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------------
server = "LAB-DEWEY"
folder_path = "E:\\"
student_folder = r"E:\ITSC-203 - Scripting"
student_group = "Students"
admin_group = "Administrators"
system_account = "SYSTEM"


# ---------------------------------------------------------------------
# class: defines a blueprint for remediating SMB shares and NTFS permissions
# ---------------------------------------------------------------------
class FileShareRemediator:
    def __init__(self):
        self.server = server
        self.folder_path = folder_path

    # -------------------------------
    # function: runs a PowerShell command
    # -------------------------------
    def run_powershell(self, ps_command, description):
        print("=" * 80)
        print(f"[ {description} on {self.server} ]")
        print("=" * 80)

        command = f'powershell -NoProfile -Command "{ps_command}"'

        proc = subprocess.Popen(
            command,
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
        ps_command = rf'''
        $remove = @(
            "Everyone",
            "Authenticated Users",
            "BUILTIN\Users"
        )

        Get-SmbShare | Where-Object {{ $_.Name -notlike "*$" }} | ForEach-Object {{
            $share = $_.Name
            Write-Host "Processing share: $share"

            foreach ($r in $remove) {{
                try {{
                    Revoke-SmbShareAccess -Name $share -AccountName $r -Force -ErrorAction Stop
                }} catch {{}}
            }}

            Grant-SmbShareAccess -Name $share -AccountName "{admin_group}" -AccessRight Full -Force
            Grant-SmbShareAccess -Name $share -AccountName "NT AUTHORITY\SYSTEM" -AccessRight Full -Force
        }}

        # Grant Students RW access ONLY to ITSC-203 - Scripting share
        if (Get-SmbShare | Where-Object {{ $_.Path -eq "{student_folder}" }}) {{
            $s = (Get-SmbShare | Where-Object {{ $_.Path -eq "{student_folder}" }}).Name
            Grant-SmbShareAccess -Name $s -AccountName "{student_group}" -AccessRight Change -Force
            Write-Host "Granted Students RW access to share: $s"
        }}
        '''
        self.run_powershell(ps_command, "SMB Share Remediation")

    # -------------------------------
    # function: remediate NTFS permissions
    # -------------------------------
    def remediate_ntfs(self):
        print("=" * 80)
        print(f"[ NTFS Remediation on {self.folder_path} ]")
        print("=" * 80)

        # Global lock-down
        subprocess.run(["icacls", self.folder_path, "/remove", "Everyone", "/T", "/C"])
        subprocess.run(["icacls", self.folder_path, "/remove", "Authenticated Users", "/T", "/C"])
        subprocess.run(["icacls", self.folder_path, "/remove", "BUILTIN\\Users", "/T", "/C"])

        subprocess.run(["icacls", self.folder_path, "/grant", "SYSTEM:(OI)(CI)F", "/T", "/C"])
       #subprocess.run(["icacls", self.folder_path, "/grant", "Administrators:(OI)(CI)F", "/T", "/C"])
        subprocess.run(["icacls", self.folder_path, "/grant", "BUILTIN\\Administrators:(OI)(CI)F", "/T", "/C"])

        # Student folder exception
        if subprocess.run(["cmd", "/c", f"if exist \"{student_folder}\" exit 0"], capture_output=True).returncode == 0:
            subprocess.run(["icacls", student_folder, "/grant", f"{student_group}:(OI)(CI)M", "/C"])
            print(f"[+] Granted Students RW access to {student_folder}")

        print("[+] NTFS remediation completed")

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