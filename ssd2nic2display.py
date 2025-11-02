#!/usr/bin/env python3

import socket
import os
import threading
import time
import sys
import subprocess
from PIL import Image
import qrcode
import hashlib
import random
import base64

SSD_FILE_PATH = os.path.abspath("fromssd.txt")
HOST = '127.0.0.1'
PORT = 8081
IMAGE_FILE = "/tmp/qrcode_display.png"

def display_string_as_qrcode(final_data_string):
    sanitized_string = final_data_string.strip()
    
    if not sanitized_string:
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(sanitized_string)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(IMAGE_FILE)
    
    try:
        subprocess.Popen(["xdg-open", IMAGE_FILE])
    except FileNotFoundError:
        print("Could not open image. 'xdg-open' command not found.")

def sender_main(file_path):
    try:
        with open(file_path, 'r') as f:
            string_to_send = f.read()
        print(f"SSD: Reading '{string_to_send.strip()}' to RAM (Address: {hex(id(string_to_send))}, SHA256: {hashlib.sha256(string_to_send.encode()).hexdigest()}).")
        input("Press Enter to continue...")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    # Simulate SSD Wear and Tear
    if random.random() < 0.5: # 50% chance of corruption
        char_index_to_corrupt = random.randint(0, len(string_to_send) - 2)
        bit_to_flip = 1 << random.randint(0, 7)
        corrupted_char = ord(string_to_send[char_index_to_corrupt]) ^ bit_to_flip
        string_to_send = string_to_send[:char_index_to_corrupt] + chr(corrupted_char) + string_to_send[char_index_to_corrupt+1:]
        print(f"!!! SSD Wear and Tear Simulation: Flipped a bit in the data. New data: '{string_to_send.strip()}' (SHA256: {hashlib.sha256(string_to_send.encode()).hexdigest()}) !!!")
        input("Press Enter to continue...")

    encoded_string = base64.b64encode(string_to_send.encode()).decode()
    os.environ["DATA_TO_LOG"] = encoded_string
    print(f"RAM (Address: {hex(id(string_to_send))}): Writing '{encoded_string}' (Base64 encoded) to Environment Variable (DATA_TO_LOG).")
    input("Press Enter to continue...")

    data_from_env_encoded = os.environ["DATA_TO_LOG"]
    decoded_string = base64.b64decode(data_from_env_encoded).decode()
    print(f"Environment Variable: Reading '{data_from_env_encoded}' and decoding to '{decoded_string.strip()}' in RAM (Address: {hex(id(decoded_string))}, SHA256: {hashlib.sha256(decoded_string.encode()).hexdigest()}).")
    input("Press Enter to continue...")

    # Simulate Packet Loss and Reordering
    packets = []
    for i, char in enumerate(decoded_string):
        packets.append(f"{i}:{char}")
    
    random.shuffle(packets)
    if random.random() < 0.5: # 50% chance of packet loss
        dropped_packet_index = random.randint(0, len(packets) - 1)
        print(f"!!! NIC Simulation: Dropping packet {packets[dropped_packet_index]} !!!")
        packets.pop(dropped_packet_index)
        input("Press Enter to continue...")

    time.sleep(0.5)

    try:
        print(f"RAM (Address: {hex(id(decoded_string))}): Sending packets to NIC: {packets}")
        input("Press Enter to continue...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall("\n".join(packets).encode('utf-8'))
    except ConnectionRefusedError:
        print("Connection refused.")
    except Exception as e:
        print(f"Sender error: {e}")

def receiver_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        s.settimeout(None)

        try:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode('utf-8')
                packets = data.split('\n')
                print(f"Display: Receiving packets from NIC: {packets}")
                input("Press Enter to continue...")

                # Reassemble packets
                reassembled_string = ""
                received_packets = {}
                for packet in packets:
                    if ':' in packet:
                        seq, char = packet.split(':', 1)
                        received_packets[int(seq)] = char
                
                for i in range(len(packets) + 1):
                    if i in received_packets:
                        reassembled_string += received_packets[i]
                    else:
                        reassembled_string += "_" # Indicate missing packet

                print(f"Display: Reassembled string: '{reassembled_string.strip()}' (SHA256: {hashlib.sha256(reassembled_string.encode()).hexdigest()}). Generating QR code.")
                input("Press Enter to continue...")
                display_string_as_qrcode(reassembled_string)
        except socket.timeout:
            print("Receiver timeout.")
        except Exception as e:
            print(f"Receiver error: {e}")

if __name__ == "__main__":
    receiver = threading.Thread(target=receiver_thread)
    receiver.start()
    
    sender_main(SSD_FILE_PATH)
    
    receiver.join()
