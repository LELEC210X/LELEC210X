#include <stdio.h>
#include <stdint.h>

void process_array(int32_t* input, int32_t* output, int length) {
    // Example processing: multiply each element by 2
    for(int i = 0; i < length; i++) {
        output[i] = input[i] * 2;
    }
}

int main() {
    int32_t input [1000];  // Max size buffer
    int32_t output[1000]; // Max size buffer
    int length;
    
    // Read length
    fread(&length, sizeof(int), 1, stdin);
    
    // Read input array
    fread(input, sizeof(int32_t), length, stdin);
    
    //////////////////////////////////////////

    // Process array
    process_array(input, output, length);
    
    //////////////////////////////////////////

    // Write output array
    fwrite(output, sizeof(int32_t), length, stdout);
    
    return 0;
}