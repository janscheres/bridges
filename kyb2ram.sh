#!/bin/bash

FILE="/dev/shm/fromkeyboard.txt"

read -p "Enter 'Hello World' string: " input

echo "$input" > $FILE

echo "Written to ram"
ls -l $FILE

python ./ram2cpu.py
