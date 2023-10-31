import numpy as np
<<<<<<< refs/remotes/upstream/main
from scipy.signal import convolve
from plot_utils import *
=======
from plot_utils import *
from scipy.signal import convolve
>>>>>>> Revert "enlever le chain de argu"

# Parameters
B = 50e3
OSR = 8
<<<<<<< refs/remotes/upstream/main
fs = OSR*B

# Input
try:
  input_array = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/input_float.txt",sep="\n")
except(FileNotFoundError):
=======
fs = OSR * B

# Input
try:
    input_array = np.fromfile(
        "fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/input_float.txt",
        sep="\n",
    )
except FileNotFoundError:
>>>>>>> Revert "enlever le chain de argu"
    print("\nInputs are not generated, run input_gen.py first!\n")
    exit()

# Filter u
try:
<<<<<<< refs/remotes/upstream/main
    taps = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_float.txt",sep=",")
except(FileNotFoundError):
    print("\nTaps are not generated, run taps_gen.py first!\n")
    exit()
    
# Output
input_array = input_array.reshape((int(len(input_array)/2),2))
output_array = np.zeros_like(input_array)
output_array[:,0] = convolve(input_array[:,0], taps, mode="full")[:input_array.shape[0]]
output_array[:,1] = convolve(input_array[:,1], taps, mode="full")[:input_array.shape[0]]
output_array = output_array.flatten()
np.savetxt('fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/output_float.txt',output_array,newline=",")
=======
    taps = np.fromfile(
        "fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_float.txt",
        sep=",",
    )
except FileNotFoundError:
    print("\nTaps are not generated, run taps_gen.py first!\n")
    exit()

# Output
input_array = input_array.reshape((int(len(input_array) / 2), 2))
output_array = np.zeros_like(input_array)
output_array[:, 0] = convolve(input_array[:, 0], taps, mode="full")[
    : input_array.shape[0]
]
output_array[:, 1] = convolve(input_array[:, 1], taps, mode="full")[
    : input_array.shape[0]
]
output_array = output_array.flatten()
np.savetxt(
    "fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/output_float.txt",
    output_array,
    newline=",",
)
>>>>>>> Revert "enlever le chain de argu"
