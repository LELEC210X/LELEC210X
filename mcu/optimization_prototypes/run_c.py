import subprocess
import numpy as np
import os, sys
import ctypes
import click

def compile_c_program(path):
    # Compile the C program
    if os.name == 'nt':  # Windows
        compile_command = f"gcc -o {path}/bin/entry.exe {path}/entry.c"
    else:  # Linux
        compile_command = f"gcc -o {path}/bin/entry {path}/entry.c"
    
    result = subprocess.run(compile_command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"Compilation failed: {result.stderr}")

def process_array(path, input_array):
    # Ensure input is numpy array of int32
    input_array = np.array(input_array, dtype=np.int32)
    length = len(input_array)

    # Start the C program
    if os.name == 'nt':
        program_name = f"{path}/bin/entry.exe"
    else:
        program_name = f"{path}/bin/entry"

    process = subprocess.Popen(
        program_name,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Write length and input array to C program
    process.stdin.write(length.to_bytes(4, byteorder='little'))
    process.stdin.write(input_array.tobytes())
    process.stdin.flush()

    # Read output array from C program
    output_data = process.stdout.read(length * 4)  # 4 bytes per int32
    process.wait()

    # Convert bytes to numpy array
    output_array = np.frombuffer(output_data, dtype=np.int32)
    return output_array

@click.command()
@click.argument("code_module_path", type=click.Path(exists=True))
def main(code_module_path):
    # Check if the code module is a directory
    if not os.path.isdir(code_module_path):
        raise Exception("Code module must be a directory")
    
    # Check if the directory contains "c_code" and "python_code" subdirectories
    c_code_dir = os.path.join(code_module_path, "c_code")
    python_code_dir = os.path.join(code_module_path, "python_code")
    if not os.path.isdir(c_code_dir) or not os.path.isdir(python_code_dir):
        raise Exception("Code module must contain 'c_code' and 'python_code' subdirectories")
    
    ##############################

    print(">> Checks passed. Running the code module...")
    print(f">> Code module path: {code_module_path}")

    # Compile the C program
    compile_c_program(c_code_dir)

    # Get data from Python code and pass it to C program by importing the Python code
    python_entry = os.path.join(python_code_dir, "entry.py")
    sys.path.append(python_code_dir)
    entry = __import__("entry")

    # Get data from Python code
    test_array = entry.get_input_data()
    print("Input array:", test_array)

    # Process the array using the C program
    result = process_array(c_code_dir, test_array)
    print("Output array:", result)

    # Pass on the result to the Python code
    entry.process_output_data(result)

if __name__ == "__main__":
    main()