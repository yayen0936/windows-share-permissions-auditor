import subprocess

SERVER = "LAB-DEWEY"

def get_smb_share():
    ps_command = f'powershell -NoProfile -Command "Get-SmbShare -CimSession {SERVER}"'
    try:
        output = subprocess.check_output(ps_command, shell=True, text=True, stderr=subprocess.STDOUT)
        print("=" * 80)
        print(f"[ SMB Shares on {SERVER} ]")
        print("=" * 80)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to get SMB shares from {SERVER}:")
        print(e.output)

def get_share_acl():
    ps_command = (
        f'powershell -NoProfile -Command "Get-SmbShare -CimSession {SERVER} | '
        f'ForEach-Object {{ Get-SmbShareAccess -Name $_.Name -CimSession {SERVER} }}"'
    )
    try:
        output = subprocess.check_output(ps_command, shell=True, text=True, stderr=subprocess.STDOUT)
        print("=" * 80)
        print(f"[ SMB Share-Level ACLs on {SERVER} ]")
        print("=" * 80)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to get Share ACLs from {SERVER}:")
        print(e.output)


def get_ntfs_acl():
    folder_path = "E:\\Test"

    ps_command = (
        f'powershell -NoProfile -Command "'
        f'Invoke-Command -ComputerName {SERVER} {{ '
        f', (Get-Item \'{folder_path}\') + (Get-ChildItem \'{folder_path}\' -Recurse -ErrorAction SilentlyContinue) | '
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
        f'}} | Format-Table -AutoSize '
        f'}}"'
    )

    try:
        output = subprocess.check_output(ps_command, shell=True, text=True, stderr=subprocess.STDOUT)
        print("=" * 80)
        print(f"[ NTFS File-Level ACLs on {SERVER} ({folder_path}) ]")
        print("=" * 80)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to get NTFS ACLs from {SERVER}:")
        print(e.output)

def main():
    print(f"Enumerating SMB and NTFS permissions for {SERVER}...\n")
    get_smb_share()
    get_share_acl()
    get_ntfs_acl()
    print("\nAudit complete.\n")

if __name__ == "__main__":
    main()