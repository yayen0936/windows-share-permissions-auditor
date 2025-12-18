import subprocess
import time

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
SERVER = "LAB-DEWEY"

# ---------------------------------------------------------------------
# Helper: Run PowerShell Command
# ---------------------------------------------------------------------
def run_powershell(ps_command: str, description: str):
    print("=" * 80)
    print(f"[ {description} on {SERVER} ]")
    print("=" * 80)

    start = time.time()

    proc = subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = proc.communicate()
    runtime = round(time.time() - start, 2)

    print(f"\n[+] Completed: {description} (Runtime: {runtime}s)")
    if stdout:
        print(stdout)
    if stderr:
        print(f"[!] Errors:\n{stderr}")

# ---------------------------------------------------------------------
# NTFS REMEDIATION
# ---------------------------------------------------------------------
def remediate_ntfs():
    ps_script = r'''
# --------------------------------------------------
# Paths
# --------------------------------------------------
$Paths = @{
    "E:\Backups"                = "ITSADLAB\System Administrator"
    "E:\IT"                     = "ITSADLAB\System Administrator"
    "E:\Public"                 = "ITSADLAB\System Administrator"
    "E:\ITSC-203 - Scripting"   = "itsadlab\Students"
}

# --------------------------------------------------
# Groups to remove (NTFS)
# --------------------------------------------------
$RemoveGroups = @(
    "BUILTIN\Users",
    "NT AUTHORITY\Authenticated Users",
    "itsadlab\Domain Users",
    "itsadlab\Users"
)

foreach ($Path in $Paths.Keys) {

    $TargetGroup = $Paths[$Path]

    Write-Host ""
    Write-Host "Processing NTFS permissions for: $Path" -ForegroundColor Cyan

    $acl = Get-Acl $Path

    foreach ($group in $RemoveGroups) {
        $rules = $acl.Access | Where-Object { $_.IdentityReference -eq $group }
        foreach ($rule in $rules) {
            $acl.RemoveAccessRule($rule)
            Write-Host " - Removed NTFS permission: $group"
        }
    }

    $newRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $TargetGroup,
        "Modify",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )

    $acl.AddAccessRule($newRule)
    Write-Host " - Added NTFS permission: $TargetGroup (RW)"

    Set-Acl -Path $Path -AclObject $acl

    Write-Host "Current NTFS Permissions:"
    (Get-Acl $Path).Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType -AutoSize
}

Write-Host "`nNTFS permission update completed." -ForegroundColor Green
'''
    run_powershell(ps_script, "NTFS Remediation")

# ---------------------------------------------------------------------
# SMB REMEDIATION
# ---------------------------------------------------------------------
def remediate_smb():
    ps_script = r'''
$SysAdminGroup = "ITSADLAB\System Administrator"
$StudentsGroup = "ITSADLAB\Students"

$SharePermissions = @{
    "Backups"              = $SysAdminGroup
    "IT"                   = $SysAdminGroup
    "Public"               = $SysAdminGroup
    "ITSC-203 - Scripting" = $StudentsGroup
}

foreach ($ShareName in $SharePermissions.Keys) {

    Write-Host ""
    Write-Host "Processing SMB Share: $ShareName" -ForegroundColor Cyan

    Get-SmbShareAccess -Name $ShareName -ErrorAction SilentlyContinue |
    Where-Object { $_.AccountName -eq "Everyone" } |
    ForEach-Object {
        Revoke-SmbShareAccess -Name $ShareName -AccountName "Everyone" -Force
        Write-Host " - Removed: Everyone"
    }

    $Group = $SharePermissions[$ShareName]

    Grant-SmbShareAccess `
        -Name $ShareName `
        -AccountName $Group `
        -AccessRight Change `
        -Force

    Write-Host " - Granted: $Group (RW)"

    Write-Host "Current SMB Permissions:"
    Get-SmbShareAccess -Name $ShareName |
    Format-Table AccountName, AccessRight -AutoSize
}

Write-Host "`nSMB permission update completed." -ForegroundColor Green
'''
    run_powershell(ps_script, "SMB Remediation")

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    print(f"=== Starting NTFS + SMB Remediation on {SERVER} ===\n")

    remediate_ntfs()
    remediate_smb()

    print(f"\n=== Remediation Complete on {SERVER} ===")

if __name__ == "__main__":
    main()