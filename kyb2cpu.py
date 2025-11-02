#!/usr/bin/env python3

import subprocess

def main():
    try:
        raw_input_string = input("Enter a string: ")

        subprocess.run(["python3", "string2wav.py", raw_input_string])

        cpu_processed_string = raw_input_string.upper()

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
                final_file = "fromssd.txt"
                with open(final_file, "w") as f:
                    f.write(gpu_output_string)

                subprocess.run(["python3", "ssd2nic2display.py"])

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
