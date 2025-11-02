# DataBridges

**Tagline:** Storing and transferring data where and how you shouldn't.

## Description
DataBridges is a visualization tool that demystifies the complex inner workings of your machine. It traces a simple string from your keyboard through various hardware and software components, providing detailed logs, SHA256 hashing for data integrity, and a final QR code representation. This project makes the invisible visible and offers a unique, educational look into the world of data flow.

## How to Run

Follow these steps to set up and run the DataBridges project:

### Prerequisites

*   **Python 3**: Ensure you have Python 3 installed on your system.
*   **C Compiler**: A C compiler (like GCC) is required to compile the `cpu2gpu.c` program.
*   **OpenCL**: The `cpu2gpu` program uses OpenCL to interact with the GPU. You will need to have the OpenCL headers and a runtime library installed.
*   **`qrcode` Python Library**: This library is used to generate the QR codes.

### Installation

1.  **Install `qrcode`**: Open your terminal and run the following command to install the `qrcode` library:
    ```bash
    pip install qrcode[pil]
    ```

### Permissions

Before running the scripts, you need to grant execute permissions to the `kyb2cpu.py` and `compilecpu2gpu.sh` files:

```bash
chmod +x kyb2cpu.py
chmod +x compilecpu2gpu.sh
```

### Execution

1.  **Compile the C program**: First, compile the `cpu2gpu.c` program by running the compilation script:
    ```bash
    ./compilecpu2gpu.sh
    ```
    This will create an executable file named `cpu2gpu`.

2.  **Run the main script**: Now, execute the main Python script:
    ```bash
    ./kyb2cpu.py
    ```

3.  **Enter a string**: The script will prompt you to "Enter a string:". Type your desired text and press Enter.

The console will display a detailed log of the data's journey through the various components, and a QR code image will be generated and opened, representing the final state of your data.
