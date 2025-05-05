#!/usr/bin/env python3

import shutil
import psutil
import os
import platform
import subprocess

def check_command(cmd):
    return shutil.which(cmd) is not None

def main():
    print("=== UbuntuWebScanner Diagnostic ===")

    # Environment
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.system()} {platform.release()}")

    # Dependencies
    for tool in ['nmap', 'sqlite3', 'curl', 'ping']:
        print(f"{tool}: {'✓ found' if check_command(tool) else '✗ missing'}")

    # Network
    print("IP configuration:")
    os.system("ip a" if shutil.which("ip") else "ifconfig")

    # CPU, Memory, Disk
    print(f"\nCPU Usage: {psutil.cpu_percent()}%")
    print(f"Memory: {psutil.virtual_memory().percent}% used")
    print(f"Disk: {psutil.disk_usage('/').percent}% used")

if __name__ == '__main__':
    main()
