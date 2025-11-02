#!/bin/bash
gcc cpu2gpu.c -o cpu2gpu -I /usr/include/CL -lOpenCL
./cpu2gpu
ls -l /tmp/fromgpu.txt
