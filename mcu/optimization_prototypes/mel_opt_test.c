#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define WIDTH 256
#define HEIGHT 256

// Function to read the bytemap image
unsigned char* read_image(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (!file) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }

    unsigned char* image = (unsigned char*)malloc(WIDTH * HEIGHT);
    fread(image, 1, WIDTH * HEIGHT, file);
    fclose(file);

    return image;
}

// Function to write the bytemap image
void write_image(const char* filename, unsigned char* image) {
    FILE* file = fopen(filename, "wb");
    if (!file) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }

    fwrite(image, 1, WIDTH * HEIGHT, file);
    fclose(file);
}

// Function to apply mel transform
void mel_transform(unsigned char* input, unsigned char* output) {
    for (int i = 0; i < WIDTH * HEIGHT; ++i) {
        // Example mel transform: log(1 + input)
        output[i] = (unsigned char)(log(1 + input[i]) * 255 / log(256));
    }
}

int main() {
    const char* input_filename = "input.bytemap";
    const char* output_filename = "output.bytemap";

    unsigned char* input_image = read_image(input_filename);
    unsigned char* output_image = (unsigned char*)malloc(WIDTH * HEIGHT);

    mel_transform(input_image, output_image);

    write_image(output_filename, output_image);

    free(input_image);
    free(output_image);

    return 0;
}