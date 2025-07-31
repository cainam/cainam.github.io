#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # Forward all arguments to the system python3
    result = subprocess.run(["/usr/bin/python3"] + sys.argv[1:], check=False)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
