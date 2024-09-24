import numpy as np
from scipy.signal import convolve
from plot_utils import *

# Parameters
B = 50e3
OSR = 8
fs = OSR*B

# Input
try:
  input_array = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/input_float.txt",sep="\n")
except(FileNotFoundError):
    print("\nInputs are not generated, run input_gen.py first!\n")
    exit()

# Filter u
try:
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
