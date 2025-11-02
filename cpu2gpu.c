#include <stdio.h>   // Added to fix errors for FILE, fopen, fprintf, etc.
#include <stdlib.h>  // Added to fix errors for malloc, exit
#include <string.h>  // Added to fix errors for string functions
#include <CL/cl.h>

// --- HARDCODED FILE PATHS ---
#define INPUT_FILE_PATH "/tmp/fromcpu.txt"
#define OUTPUT_FILE_PATH "/tmp/fromgpu.txt"

// ----------------------------------------------------------------------------
// Error checking utility
// ----------------------------------------------------------------------------
void checkError(cl_int err, const char *msg) {
    if (err != CL_SUCCESS) {
        fprintf(stderr, "OPENCL ERROR [%d]: %s\n", err, msg);
        exit(1);
    }
}

// ----------------------------------------------------------------------------
// Main Bridge Function
// ----------------------------------------------------------------------------
int main() {
    // File paths are hardcoded using preprocessor definitions
    const char *input_file = INPUT_FILE_PATH;
    const char *output_file = OUTPUT_FILE_PATH;

    FILE *f_in, *f_out;
    char *input_string = NULL;
    size_t string_len = 0;
    cl_int err;
    
    // --- STEP 1: READ INPUT FILE (Host RAM) ---
    f_in = fopen(input_file, "r");
    if (!f_in) {
        perror("Error reading input file: " INPUT_FILE_PATH);
        return 1;
    }
    fseek(f_in, 0, SEEK_END);
    string_len = ftell(f_in);
    fseek(f_in, 0, SEEK_SET);

    input_string = (char*)malloc(string_len + 1);
    if (!input_string) {
        perror("Memory allocation failed");
        fclose(f_in);
        return 1;
    }
    fread(input_string, 1, string_len, f_in);
    input_string[string_len] = '\0';
    fclose(f_in);

    printf("--- [BRIDGE 5: CPU -> GPU (Memory Transfer Only)] ---\n");
    printf("String read into Host RAM (CPU) from %s: '%s'\n", INPUT_FILE_PATH, input_string);

    // --- STEP 2: OPENCL SETUP (Platform and Device Discovery) ---
    cl_platform_id platform;
    cl_device_id device;
    cl_context context;
    cl_command_queue queue;

    err = clGetPlatformIDs(1, &platform, NULL);
    checkError(err, "clGetPlatformIDs");
    err = clGetDeviceIDs(platform, CL_DEVICE_TYPE_ALL, 1, &device, NULL);
    checkError(err, "clGetDeviceIDs");

    // Using clCreateContext for OpenCL 1.1 compatibility, though PoCL supports 3.0
    context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    checkError(err, "clCreateContext");

    // Using clCreateCommandQueue for OpenCL 1.1 compatibility
    queue = clCreateCommandQueue(context, device, 0, &err);
    checkError(err, "clCreateCommandQueue");
    
    char device_name[128];
    clGetDeviceInfo(device, CL_DEVICE_NAME, 128, device_name, NULL);
    printf("Device Selected (PoCL/iGPU): %s\n", device_name);

    // --- STEP 3: CREATE DEVICE MEMORY BUFFERS ---
    cl_mem transfer_buffer = clCreateBuffer(context, CL_MEM_READ_WRITE,
                                            string_len, NULL, &err);
    checkError(err, "clCreateBuffer (transfer_buffer)");
    
    printf("Device Memory allocated. Buffer ID created.\n");

    // --- STEP 4: TRANSFER DATA (HOST -> DEVICE) ---
    printf("Transferring data from Host RAM -> Device Memory...\n");
    err = clEnqueueWriteBuffer(queue, transfer_buffer, CL_TRUE, 0, string_len, 
                               input_string, 0, NULL, NULL);
    checkError(err, "clEnqueueWriteBuffer");
    printf("Transfer Complete: Data is now in Device Memory.\n");

    // --- STEP 5: TRANSFER DATA BACK (DEVICE -> HOST) ---
    char *output_string = (char*)malloc(string_len + 1);
    
    printf("Transferring data from Device Memory -> Host RAM (Read Back)...\n");
    err = clEnqueueReadBuffer(queue, transfer_buffer, CL_TRUE, 0, string_len, 
                              output_string, 0, NULL, NULL);
    checkError(err, "clEnqueueReadBuffer");

    output_string[string_len] = '\0'; // Null-terminate the output

    printf("Transfer Complete. Data read back to Host RAM: '%s'\n", output_string);

    // --- STEP 6: WRITE OUTPUT FILE (RAM -> /tmp file) ---
    f_out = fopen(output_file, "w");
    if (!f_out) {
        perror("Error writing output file: " OUTPUT_FILE_PATH);
        // Cleanup memory and OpenCL resources before exiting
        free(input_string);
        free(output_string);
        clReleaseMemObject(transfer_buffer);
        clReleaseCommandQueue(queue);
        clReleaseContext(context);
        return 1;
    }
    fprintf(f_out, "%s", output_string);
    fclose(f_out);

    printf("Read-back result saved to %s\n", OUTPUT_FILE_PATH);
    printf("---------------------------------------\n");

    // --- STEP 7: CLEANUP ---
    free(input_string);
    free(output_string);
    clReleaseMemObject(transfer_buffer);
    clReleaseCommandQueue(queue);
    clReleaseContext(context);

    return 0;
}

