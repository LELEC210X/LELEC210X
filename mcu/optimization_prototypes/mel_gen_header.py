import numpy as np
from librosa import filters
import os, sys
from typing import List

### Helper functions

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def read_header_file(filename):
    defines = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#define'):
                parts = line.split()
                if len(parts) == 3:
                    key = parts[1]
                    value = parts[2]
                    defines[key] = value
    return defines

### Header generation

def add_imports(header_lines, imports):
    return [
        *header_lines,
        "",
        *imports,
        ""
    ]

def add_guards(header_lines, guard):
    return [
        "/* This file is generated during compilation. Do not modify. */",
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        *header_lines,
        "",
        f"#endif // {guard}"
    ]

def add_triangle_struct(header_lines:List, triangle_max_len:int):
    return [
        *header_lines,
        "",
        "typedef struct mel_trian_t {",
         "    size_t triangle_len;",
         "    size_t idx_offset;",
        f"    const q15_t values[{triangle_max_len}];",
        "} mel_trian_t;",
        "",
        f"#define MEL_TRIANGLE_MAX_LEN {triangle_max_len}",
        ""
    ]

def add_triangle_buffer_struct(header_lines:List, mel_triangles_liners:List):
    return [
        *header_lines,
        "",
        "static const mel_trian_t mel_triangles[] = {",
        *mel_triangles_liners,
        "};",
        ""
    ]

def gen_mel_triangle_liners(triangle_sizes:List, triangle_offsets:List, triangles:List):
    mel_triangles_liners = []
    for i in range(len(triangle_sizes)):
        current_size   = triangle_sizes[i]
        current_offset = triangle_offsets[i]
        current_vals   = triangles[i]

        message = "    {"
        message += f" {current_size:4}, {current_offset:4},"
        message += " {" + ", ".join([f"{x:4}" for x in current_vals]) + "}},"
        mel_triangles_liners.append(message)
        
    return mel_triangles_liners

def gen_trianlge_stuff(f_sample:int, num_fft:int, num_mel:int): # FIX
    mel_filter_bank = filters.mel(sr=f_sample, n_fft=num_fft, n_mels=num_mel)
    # Get max triangle length
    max_triangle_length = np.max(np.sum(mel_filter_bank>0, axis=1))
    # Get triangle sizes
    triangle_sizes = [np.sum(mel_filter_bank[i]>0) for i in range(num_mel)]
    # Get triangle offsets
    triangle_offsets = [np.argmax(mel_filter_bank[i]>0) for i in range(num_mel)]
    # Get triangle values
    mel_triangles = []
    for i in range(num_mel):
        mel_triangles.append([int(x) for x in mel_filter_bank[i]*32767])
        mel_triangles[i] = np.roll(mel_triangles[i], -triangle_offsets[i])
    mel_triangles = [x[:max_triangle_length] for i, x in enumerate(mel_triangles)]
    return mel_triangles, triangle_sizes, triangle_offsets, max_triangle_length

### generate header

def gen_mel_header(f_sample:int, num_fft:int, num_mel:int, header_file:str):
    mel_triangles, triangle_sizes, triangle_offsets, triangle_max_len = gen_trianlge_stuff(f_sample, num_fft, num_mel)
    mel_triangles_liners = gen_mel_triangle_liners(triangle_sizes, triangle_offsets, mel_triangles)

    header_lines = []
    header_lines = add_imports(header_lines, ["#include <arm_math.h>"])
    header_lines = add_triangle_struct(header_lines, triangle_max_len)
    header_lines = add_triangle_buffer_struct(header_lines, mel_triangles_liners)
    header_lines = add_guards(header_lines, "MEL_HEADER_H")

    with open(header_file, 'w') as f:
        f.write('\n'.join(header_lines))

def main():
    f_sample = 16000
    num_fft = 512
    num_mel = 40
    header_file = os.path.join(get_script_path(), "mel_filter_bank.h")
    gen_mel_header(f_sample, num_fft, num_mel, header_file)

### Read and verify header

def read_and_verify_header():
    import matplotlib.pyplot as plt
    from librosa import display
    header_file = os.path.join(get_script_path(), "mel_filter_bank.h")
    buffer = []
    with open(header_file, 'r') as f:
        lines = f.readlines()
        found_line = False
        for line in lines:
            if found_line:
                buffer.append(line)
            if line.startswith("static const mel_trian_t mel_triangles[] = {"):
                found_line = True
            if line.startswith("};"):
                break
    # Translate the buffer into a numpy matrix (only the second part, where the triangles are)
    mel_triangles = []
    for line in buffer:
        line = line.replace("{", "").replace("}", "").replace(",", "").strip().replace(";","")
        values = line.split()
        values = [int(x) for x in values]
        if len(values) > 0:
            mel_triangles.append(values[2:])
    mel_triangles = np.array(mel_triangles)/32767
    # Plot the triangles
    figure, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    im1 = display.specshow(mel_triangles, x_axis='frames', ax=ax1)
    ax1.set_title('Encoded librosa mel filter bank')
    ax1.set_ylabel('Mel filter')
    ax1.set_xlabel('FFT bin')
    figure.colorbar(im1, ax=ax1, orientation='horizontal')

    mel_triangles_filt = filters.mel(sr=16000, n_fft=512, n_mels=40)
    mel_triangles_pushed = np.array([np.roll(x, -np.argmax(x > 0)) for x in mel_triangles_filt])
    mel_triangles_filt = mel_triangles_pushed[:, :np.max(np.sum(mel_triangles_filt > 0, axis=1))]

    im2 = display.specshow(mel_triangles_filt, x_axis='frames', ax=ax2)
    ax2.set_title('Librosa RAW mel filter bank')
    ax2.set_ylabel('Mel filter')
    ax2.set_xlabel('FFT bin')
    figure.colorbar(im2, ax=ax2, orientation='horizontal')

    im3 = display.specshow(np.abs(mel_triangles_filt - mel_triangles), x_axis='frames', ax=ax3, cmap='hot')
    ax3.set_title('Error')
    ax3.set_ylabel('Mel filter')
    ax3.set_xlabel('FFT bin')
    figure.colorbar(im3, ax=ax3, orientation='horizontal')

    plt.show()

# Run the main function if the script is run directly

if __name__ == "__main__":
    main()
    if len(sys.argv) > 1:
        read_and_verify_header()