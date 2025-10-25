import subprocess

def get_smb_share():
    server = "LAB-DEWEY"
    ps_command = f'powershell -Command "Get-SmbShare -CimSession {server}"'
    output = subprocess.check_output(ps_command, shell=True, text=True)
    print(output)

def enumerate_smb_permissions(share_name):
    try:
        ps_command = f"powershell -Command \"Get-SmbShareAccess -Name '{share_name}' | Select-Object AccountName,AccessRight | Format-Table -AutoSize\""
        smb_acl = subprocess.check_output(ps_command, shell=True, text=True)
        return smb_acl.strip()
    except Exception as e:
        return f"Unable to retrieve SMB permissions for {share_name}: {e}"


def enumerate_ntfs_permissions(folder_path):
    try:
        ntfs_acl = subprocess.check_output(f'icacls "{folder_path}" /T /C', shell=True, text=True, errors='ignore')
        return ntfs_acl.strip()
    except Exception as e:
        return f"Unable to retrieve NTFS permissions for {folder_path}: {e}"


def main():
    get_smb_share()

    print("Enumerating SMB (share-level) and NTFS (file-level) permissions for E:\\ drive shares...\n")

    for name, path in shares:
        print("=" * 60)
        print(f"Share Name : {name}")
        print(f"Folder Path: {path}")
        print("=" * 60)

        print("\n[ SMB Share-Level Permissions ]")
        print("-" * 60)
        print(enumerate_smb_permissions(name))

        print("\n[ NTFS File-Level Permissions ]")
        print("-" * 60)
        print(enumerate_ntfs_permissions(path))
        print("\n\n")

if __name__ == "__main__":
    main()