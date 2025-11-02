# The Data's Journey

1.  **Keyboard to RAM**: The user enters a string, which is stored in the keyboard buffer and then written to RAM.

2.  **RAM to CPU**: The string is processed by the CPU (converted to uppercase). This involves transferring the data to the CPU, where the ALU performs the transformation.

3.  **CPU to GPU**: The uppercase string is then written to the GPU's VRAM and reversed using a custom OpenCL kernel.

4.  **GPU to RAM to SSD**: The reversed string is sent back to RAM and then written to a file on the simulated SSD.

5.  **SSD to RAM (with simulated corruption)**: The data is read from the SSD back into RAM. To simulate SSD "wear and tear", a random bit in the data may be flipped, introducing a data corruption that will be detected by the SHA256 hash check.

6.  **RAM to Environment Variable (with Base64 encoding)**: The (potentially corrupted) data is then encoded in Base64 and stored in an environment variable.

7.  **Environment Variable to RAM (with Base64 decoding)**: The data is read from the environment variable and decoded from Base64 back into its original form.

8.  **RAM to NIC (with packet loss/reordering)**: The data is then sent to the Network Interface Card (NIC). To simulate real-world network conditions, the data is split into packets, which are then randomly shuffled and may be "dropped".

9.  **NIC to RAM to Display**: The packets are received from the NIC, reassembled (with placeholders for any missing packets), and then displayed as a QR code.
