#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

char * b64_decode(char *encoding) {
	char* output = malloc(strlen(encoding)*sizeof(encoding[0]));
	//This functions only copies the bytes into a new array
	//TODO : Implement decoding here
	memcpy(output,bytes,strlen(encoding)*sizeof(encoding[0]));
	return output;
}

int main(int argc, char *argv[])
{
	if (argc>=2) {
		char* decoded_bytes;
		decoded_bytes = b64_decode(argv[1]);
		printf(decoded_bytes);
		printf("\n");
	}
	return EXIT_SUCCESS;
}
