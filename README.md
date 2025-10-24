# 🛡️ Windows Share Permissions Auditor

This cybersecurity project focuses on developing a **Python-based auditing tool** that tracks and analyzes **misconfigured NTFS and SMB share access control lists (ACLs)** within Windows Server 2022 environments.

---

## 🎯 Objective

The goal of this project is to help IT administrators and security teams identify **overly permissive or high-risk access rights**—for example:
- `Everyone`, `Authenticated Users`, or `Domain Users` with **Modify** or **Full Control** privileges.
- Writable shares that could allow malicious file uploads or ransomware propagation.
- Folders that violate the **principle of least privilege**.

By detecting these configurations early, this tool helps reduce risks such as:
- **Data leakage**
- **Insider misuse**
- **Privilege escalation**
- **Ransomware spread through writable shares**

---

## ⚙️ Features
- Enumerates all shared folders using `net share`
- Collects **SMB share-level permissions** via `Get-SmbShareAccess`
- Collects **NTFS file-level permissions** via `icacls`
- Highlights potential misconfigurations or high-risk permissions
- Generates a structured report for auditing and compliance

---

## 🧰 Requirements
- Windows Server 2022  
- Python 3.10 or higher  
- PowerShell (for `Get-SmbShareAccess` command)  
- Administrative privileges recommended  

---

## 🚀 Usage

Run the script directly on a Windows Server or remotely on Client machine:

```python
python enumerate_smb_and_ntfs.py