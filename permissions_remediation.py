import subprocess

# ---------------------------------------------------------------------
# Global Configuration
# ---------------------------------------------------------------------
server = "LAB-DEWEY"

DOMAIN = "ITSADLAB"

SYSTEM_ADMIN_GROUP = f"{DOMAIN}\\System Administrator"
STUDENTS_GROUP = f"{DOMAIN}\\Students"

SYSTEM_ACCOUNT = "SYSTEM"                 # FIXED
ADMIN_GROUP = "BUILTIN\\Administrators"

FOLDER_ACCESS_MAP = {
    r"E:\Backups": SYSTEM_ADMIN_GROUP,
    r"E:\IT": SYSTEM_ADMIN_GROUP,
    r"E:\Public": SYSTEM_ADMIN_GROUP,
    r"E:\ITSC-203 - Scripting": STUDENTS_GROUP,
}

# ---------------------------------------------------------------------
class FileShareRemediator:
    def __init__(self):
        self.server = server

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

        out, err = proc.communicate()
        if out:
            print(out)
        if err:
            print(f"[!] Errors:\n{err}")

    # -------------------------------
    # SMB Share Remediation (FIXED)
    # -------------------------------
    def remediate_smb_shares(self):
        ps_command = rf'''
$map = @{{
    "Backups" = "{SYSTEM_ADMIN_GROUP}"
    "IT" = "{SYSTEM_ADMIN_GROUP}"
    "Public" = "{SYSTEM_ADMIN_GROUP}"
    "ITSC-203 - Scripting" = "{STUDENTS_GROUP}"
}}

foreach ($share in Get-SmbShare | Where-Object {{ $map.ContainsKey($_.Name) }}) {{

    # Remove broad access
    Get-SmbShareAccess -Name $share.Name |
        Where-Object {{
            $_.AccountName -in @("Everyone","Authenticated Users","BUILTIN\\Users")
        }} |
        ForEach-Object {{
            Revoke-SmbShareAccess -Name $share.Name -AccountName $_.AccountName -Force
        }}

    # REPLACE admin access (no duplicates)
    Set-SmbShareAccess -Name $share.Name -AccountName "{ADMIN_GROUP}" -AccessRight Full -Force
    Set-SmbShareAccess -Name $share.Name -AccountName "{SYSTEM_ACCOUNT}" -AccessRight Full -Force

    # Folder-specific RW group
    Grant-SmbShareAccess -Name $share.Name `
        -AccountName $map[$share.Name] `
        -AccessRight Change `
        -Force
}}
'''
        self.run_powershell(ps_command, "SMB Share Remediation")

    # -------------------------------
    # NTFS Remediation (unchanged)
    # -------------------------------
    def remediate_ntfs(self):
        for folder, rw_group in FOLDER_ACCESS_MAP.items():

            subprocess.run(["icacls", folder, "/remove", "Everyone", "/T", "/C"])
            subprocess.run(["icacls", folder, "/remove", "Authenticated Users", "/T", "/C"])
            subprocess.run(["icacls", folder, "/remove", "BUILTIN\\Users", "/T", "/C"])

            subprocess.run(["icacls", folder, "/grant:r", f"{SYSTEM_ACCOUNT}:(OI)(CI)F", "/T", "/C"])
            subprocess.run(["icacls", folder, "/grant", f"{ADMIN_GROUP}:(OI)(CI)F", "/T", "/C"])

            subprocess.run([
                "icacls", folder,
                "/grant", f"{rw_group}:(OI)(CI)M",
                "/C"
            ])

    def run_full_remediation(self):
        self.remediate_smb_shares()
        self.remediate_ntfs()


def main():
    FileShareRemediator().run_full_remediation()


if __name__ == "__main__":
    main()
