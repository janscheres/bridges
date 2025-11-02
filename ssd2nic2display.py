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

def receiver_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        s.settimeout(5)

        try:
            conn, addr = s.accept()
            with conn:
                socket_received_bytes = conn.recv(1024)
                if socket_received_bytes:
                    received_string = socket_received_bytes.decode()
                    print(f"Display: Receiving '{received_string.strip()}' from NIC (SHA256: {hashlib.sha256(received_string.encode()).hexdigest()}). Generating QR code.")
                    display_string_as_qrcode(received_string)
        except socket.timeout:
            print("Receiver timeout.")
        except Exception as e:
            print(f"Receiver error: {e}")

def sender_main(file_path):
    try:
        with open(file_path, 'r') as f:
            string_to_send = f.read()
        print(f"SSD: Reading '{string_to_send.strip()}' to RAM (Address: {hex(id(string_to_send))}, SHA256: {hashlib.sha256(string_to_send.encode()).hexdigest()}).")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    os.environ["DATA_TO_LOG"] = string_to_send
    print(f"RAM (Address: {hex(id(string_to_send))}): Writing '{string_to_send.strip()}' to Environment Variable (DATA_TO_LOG).")

    data_from_env = os.environ["DATA_TO_LOG"]
    print(f"Environment Variable: Reading '{data_from_env.strip()}' to RAM (Address: {hex(id(data_from_env))}, SHA256: {hashlib.sha256(data_from_env.encode()).hexdigest()}).")

    time.sleep(0.5)

    try:
        print(f"RAM (Address: {hex(id(data_from_env))}): Sending '{data_from_env.strip()}' to NIC.")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(data_from_env.encode('utf-8'))
    except ConnectionRefusedError:
        print("Connection refused.")
    except Exception as e:
        print(f"Sender error: {e}")

if __name__ == "__main__":
    receiver = threading.Thread(target=receiver_thread)
    receiver.start()
    
    sender_main(SSD_FILE_PATH)
    
    receiver.join()
