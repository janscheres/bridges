#!/usr/bin/env python3

import socket
import os
import threading
import time
import sys
import subprocess
from PIL import Image, ImageDraw

SSD_FILE_PATH = os.path.abspath("fromssd.txt")
HOST = '127.0.0.1'
PORT = 8081
IMAGE_FILE = "/tmp/pixel_display.png"

def display_string_as_pixels(final_data_string):
    sanitized_string = final_data_string.strip()
    
    if not sanitized_string:
        return

    PIXEL_BLOCK_SIZE = 10
    NUM_COMPONENTS_PER_CHAR = 3
    
    img_width = len(sanitized_string) * NUM_COMPONENTS_PER_CHAR * PIXEL_BLOCK_SIZE
    img_height = PIXEL_BLOCK_SIZE
    
    img = Image.new('RGB', (img_width, img_height), color='black')
    draw = ImageDraw.Draw(img)
    
    x_offset = 0
    
    for i, char in enumerate(sanitized_string):
        ascii_val = ord(char)
        
        color_r = (ascii_val, 50, 50)
        x_start_r, x_end_r = x_offset, x_offset + PIXEL_BLOCK_SIZE
        draw.rectangle([x_start_r, 0, x_end_r, img_height], fill=color_r)
        
        g_val_index = (i * 30) % 256
        color_g = (50, g_val_index, 50)
        x_start_g, x_end_g = x_end_r, x_end_r + PIXEL_BLOCK_SIZE
        draw.rectangle([x_start_g, 0, x_end_g, img_height], fill=color_g)

        color_b = (50, 50, 150)
        x_start_b, x_end_b = x_end_g, x_end_g + PIXEL_BLOCK_SIZE
        draw.rectangle([x_start_b, 0, x_end_b, img_height], fill=color_b)
        
        x_offset = x_end_b

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
                    display_string_as_pixels(received_string)
        except socket.timeout:
            print("Receiver timeout.")
        except Exception as e:
            print(f"Receiver error: {e}")

def sender_main(file_path):
    try:
        with open(file_path, 'r') as f:
            string_to_send = f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    time.sleep(0.5)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(string_to_send.encode('utf-8'))
    except ConnectionRefusedError:
        print("Connection refused.")
    except Exception as e:
        print(f"Sender error: {e}")

if __name__ == "__main__":
    receiver = threading.Thread(target=receiver_thread)
    receiver.start()
    
    sender_main(SSD_FILE_PATH)
    
    receiver.join()
