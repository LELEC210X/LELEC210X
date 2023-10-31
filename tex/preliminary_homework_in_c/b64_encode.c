#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/*char * b64_encode(char *bytes) {
	char* output = malloc(strlen(bytes)+sizeof(bytes[0]));
	//This functions only copies the bytes into a new array
	//TODO : Implement encoding here
	memcpy(output,bytes,strlen(bytes)+sizeof(bytes[0]));
	return output;
}*/

char * b64_encode(char *bytes) {
	uint32_t encoding_length = 4*strlen(bytes)/3
	char* output = malloc(encoding_length*sizeof(bytes[0]));
	//This functions only copies the bytes into a new array
	//TODO : Implement encoding here
	memcpy(output,bytes,strlen(bytes)*sizeof(bytes[0]));
	return output;
}

int main(int argc, char *argv[])
{
	if (argc>=2) {
		char* encoded_bytes;
		encoded_bytes = b64_encode(argv[1]);
		printf(encoded_bytes);
		printf("\n");
	}
	return EXIT_SUCCESS;
}
