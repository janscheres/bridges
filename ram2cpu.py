import os
import time

RAM_FILE = "/dev/shm/fromkeyboard.txt"
CPU_FILE = "/tmp/fromcpu.txt"


print(f"Read from {RAM_FILE}...")
with open(RAM_FILE, 'r') as f:
    hello = f.read()

print(f"String in RAM: '{hello.strip()}'")

print("Perform operation on CPU (.upper()):")
upper = hello.upper()

print(f"Saving CPU output, {upper} to {CPU_FILE}...")
with open(CPU_FILE, 'w') as f:
    f.write(upper)

os.system(f"ls -l {CPU_FILE}")

os.system("chmod +x ./compilecpu2gpu.sh")
os.system("./compilecpu2gpu.sh")
