import subprocess

output = subprocess.check_output("net share", shell=True, text=True)
print(output)