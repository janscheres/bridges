#!/usr/bin/env python3

import subprocess
import hashlib

def main():
    try:
        raw_input_string = input("Enter a string: ")
        print(f"Keyboard: Input '{raw_input_string}' to RAM (Address: {hex(id(raw_input_string))}, SHA256: {hashlib.sha256(raw_input_string.encode()).hexdigest()}).")
        input("Press Enter to continue...")

        cpu_processed_string = raw_input_string.upper()
        print(f"RAM (Address: {hex(id(raw_input_string))}): Sending '{raw_input_string}' to CPU.")
        input("Press Enter to continue...")
        print(f"CPU: Sending '{cpu_processed_string}' to GPU (SHA256: {hashlib.sha256(cpu_processed_string.encode()).hexdigest()}).")
        input("Press Enter to continue...")

        with subprocess.Popen(
            ["./cpu2gpu"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ) as p:
            gpu_output_string, stderr_data = p.communicate(input=cpu_processed_string)

            if p.returncode != 0:
                print(f"Error: {stderr_data}")
            else:
                print(f"GPU: Sending '{gpu_output_string.strip()}' to RAM (Address: {hex(id(gpu_output_string))}, SHA256: {hashlib.sha256(gpu_output_string.encode()).hexdigest()}).")
                input("Press Enter to continue...")
                final_file = "fromssd.txt"
                with open(final_file, "w") as f:
                    f.write(gpu_output_string)
                print(f"RAM (Address: {hex(id(gpu_output_string))}): Writing '{gpu_output_string.strip()}' to SSD ({final_file}).")
                input("Press Enter to continue...")

                subprocess.run(["python3", "ssd2nic2display.py"])

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
