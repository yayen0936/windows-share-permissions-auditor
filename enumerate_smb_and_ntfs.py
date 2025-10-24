import subprocess

# Step 1: get shared folder names
output = subprocess.check_output("net share", shell=True, text=True)
lines = output.splitlines()
shares = []

for line in lines:
    if ":" in line and "\\" in line:
        parts = line.split()
        if len(parts) >= 1:
            share_name = parts[0]
            shares.append(share_name)

print("Enumerating SMB (share-level) permissions...\n")

# Step 2: get SMB permissions using PowerShell
for share in shares:
    print(f"=== Share: {share} ===")
    try:
        ps_command = f"powershell -Command \"Get-SmbShareAccess -Name '{share}' | Select-Object AccountName,AccessRight | Format-Table -AutoSize\""
        smb_acl = subprocess.check_output(ps_command, shell=True, text=True)
        print(smb_acl.strip())
    except Exception as e:
        print(f"Unable to retrieve SMB permissions for {share}: {e}")
    print("")  # blank line between shares

# Step 3: pause before closing
input("\nPress Enter to close...")