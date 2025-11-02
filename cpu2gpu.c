#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <CL/cl.h>

void checkError(cl_int err, const char *msg) {
    if (err != CL_SUCCESS) {
        fprintf(stderr, "OPENCL ERROR [%d]: %s\n", err, msg);
        exit(1);
    }
}

int main() {
    char cpu_input_string[256];
    size_t string_len;
    cl_int err;

    if (fgets(cpu_input_string, sizeof(cpu_input_string), stdin) == NULL) {
        perror("Error reading from stdin");
        return 1;
    }
    cpu_input_string[strcspn(cpu_input_string, "\n")] = 0;
    string_len = strlen(cpu_input_string);

    cl_platform_id platform;
    cl_device_id device;
    cl_context context;
    cl_command_queue queue;

    err = clGetPlatformIDs(1, &platform, NULL);
    checkError(err, "clGetPlatformIDs");
    err = clGetDeviceIDs(platform, CL_DEVICE_TYPE_DEFAULT, 1, &device, NULL);
    checkError(err, "clGetDeviceIDs");

    context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    checkError(err, "clCreateContext");

    queue = clCreateCommandQueue(context, device, 0, &err);
    checkError(err, "clCreateCommandQueue");

    cl_mem transfer_buffer = clCreateBuffer(context, CL_MEM_READ_WRITE, string_len, NULL, &err);
    checkError(err, "clCreateBuffer");

    err = clEnqueueWriteBuffer(queue, transfer_buffer, CL_TRUE, 0, string_len, cpu_input_string, 0, NULL, NULL);
    checkError(err, "clEnqueueWriteBuffer");

    char *gpu_output_string = (char*)malloc(string_len + 1);
    
    err = clEnqueueReadBuffer(queue, transfer_buffer, CL_TRUE, 0, string_len, gpu_output_string, 0, NULL, NULL);
    checkError(err, "clEnqueueReadBuffer");

    gpu_output_string[string_len] = '\0';

    printf("%s\n", gpu_output_string);

    free(gpu_output_string);
    clReleaseMemObject(transfer_buffer);
    clReleaseCommandQueue(queue);
    clReleaseContext(context);

    return 0;
}

