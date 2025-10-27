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

## 🧰 Requirements
- Windows Server 2022  
- Python 3.10 or higher  
- PowerShell (for `Get-SmbShareAccess` command)  
- Administrative privileges recommended  

---

## 🚀 Usage

Run the script directly remotely on Client machine:

```python
python .\remote_access.py