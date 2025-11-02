#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <CL/cl.h>

const char *kernel_source = 
"__kernel void reverse_string(__global char *str, const int len) {\n"
"    int i = get_global_id(0);\n"
"    if (i < len / 2) {\n"
"        char tmp = str[i];\n"
"        str[i] = str[len - 1 - i];\n"
"        str[len - 1 - i] = tmp;\n"
"    }\n"
"}\n";

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
    cl_program program;
    cl_kernel kernel;

    err = clGetPlatformIDs(1, &platform, NULL);
    checkError(err, "clGetPlatformIDs");
    err = clGetDeviceIDs(platform, CL_DEVICE_TYPE_DEFAULT, 1, &device, NULL);
    checkError(err, "clGetDeviceIDs");

    context = clCreateContext(NULL, 1, &device, NULL, NULL, &err);
    checkError(err, "clCreateContext");

    queue = clCreateCommandQueue(context, device, 0, &err);
    checkError(err, "clCreateCommandQueue");

    program = clCreateProgramWithSource(context, 1, &kernel_source, NULL, &err);
    checkError(err, "clCreateProgramWithSource");

    err = clBuildProgram(program, 1, &device, NULL, NULL, NULL);
    if (err != CL_SUCCESS) {
        size_t log_size;
        clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, 0, NULL, &log_size);
        char *log = (char *)malloc(log_size);
        clGetProgramBuildInfo(program, device, CL_PROGRAM_BUILD_LOG, log_size, log, NULL);
        fprintf(stderr, "Kernel build error: %s\n", log);
        free(log);
        exit(1);
    }

    kernel = clCreateKernel(program, "reverse_string", &err);
    checkError(err, "clCreateKernel");

    cl_mem transfer_buffer = clCreateBuffer(context, CL_MEM_READ_WRITE, string_len, NULL, &err);
    checkError(err, "clCreateBuffer");

    err = clEnqueueWriteBuffer(queue, transfer_buffer, CL_TRUE, 0, string_len, cpu_input_string, 0, NULL, NULL);
    checkError(err, "clEnqueueWriteBuffer");

    err = clSetKernelArg(kernel, 0, sizeof(cl_mem), &transfer_buffer);
    checkError(err, "clSetKernelArg - buffer");
    int len = string_len;
    err = clSetKernelArg(kernel, 1, sizeof(int), &len);
    checkError(err, "clSetKernelArg - len");

    size_t global_work_size = string_len;
    err = clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &global_work_size, NULL, 0, NULL, NULL);
    checkError(err, "clEnqueueNDRangeKernel");

    char *gpu_output_string = (char*)malloc(string_len + 1);
    
    err = clEnqueueReadBuffer(queue, transfer_buffer, CL_TRUE, 0, string_len, gpu_output_string, 0, NULL, NULL);
    checkError(err, "clEnqueueReadBuffer");

    gpu_output_string[string_len] = '\0';

    printf("%s\n", gpu_output_string);

    free(gpu_output_string);
    clReleaseMemObject(transfer_buffer);
    clReleaseKernel(kernel);
    clReleaseProgram(program);
    clReleaseCommandQueue(queue);
    clReleaseContext(context);

    return 0;
}

