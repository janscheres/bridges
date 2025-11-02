#!/usr/bin/env python3

import numpy as np
from scipy.io.wavfile import write
import sys
import subprocess

def sonify_string(raw_input_string, output_filename="output.wav"):
    sample_rate = 44100
    duration_per_char = 0.2
    base_freq = 220.0

    audio_data = np.array([], dtype=np.int16)

    for char in raw_input_string:
        ascii_val = ord(char)
        frequency = base_freq + (ascii_val * 2)
        
        t = np.linspace(0., duration_per_char, int(sample_rate * duration_per_char), endpoint=False)
        amplitude = np.iinfo(np.int16).max * 0.5
        tone = amplitude * np.sin(2. * np.pi * frequency * t)
        
        audio_data = np.concatenate((audio_data, tone.astype(np.int16)))

    write(output_filename, sample_rate, audio_data)

    try:
        subprocess.run(["aplay", output_filename], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Playback failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sonify_string(sys.argv[1])
    else:
        sonify_string("Hello!")
