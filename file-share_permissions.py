import subprocess

# Step 1: Get shared folder names and their paths
output = subprocess.check_output("net share", shell=True, text=True)
lines = output.splitlines()
shares = []

for line in lines:
    if ":" in line and "\\" in line:
        parts = line.split()
        if len(parts) >= 2:
            share_name = parts[0]
            share_path = parts[1]
            shares.append((share_name, share_path))

print("Enumerating SMB (share-level) and NTFS (file-level) permissions...\n")

# Step 2: Enumerate Share-level (SMB) permissions
for name, path in shares:
    print("=" * 60)
    print(f"Share Name : {name}")
    print(f"Folder Path: {path}")
    print("=" * 60)
    print("\n[ SMB Share-Level Permissions ]")
    print("-" * 60)
    try:
        ps_command = f"powershell -Command \"Get-SmbShareAccess -Name '{name}' | Select-Object AccountName,AccessRight | Format-Table -AutoSize\""
        smb_acl = subprocess.check_output(ps_command, shell=True, text=True)
        print(smb_acl.strip())
    except Exception as e:
        print(f"Unable to retrieve SMB permissions for {name}: {e}")
    print("")

# Step 3: Enumerate File-level (NTFS) permissions
    print("[ NTFS File-Level Permissions ]")
    print("-" * 60)
    try:
        # /T = traverse subfolders, /C = continue on errors (access denied)
        ntfs_acl = subprocess.check_output(f'icacls "{path}" /T /C', shell=True, text=True, errors='ignore')
        print(ntfs_acl.strip())
    except Exception as e:
        print(f"Unable to retrieve NTFS permissions for {path}: {e}")
    print("\n\n")

# Step 4: Pause before closing
input("Press Enter to close...")