import numpy as np
from matplotlib import pyplot as plt

# Input values
ninput = 64
input_array = np.zeros((2*ninput,))
input_array[:2] = 0.9999

# Quantize
nbit = 12
qbit = 11
input_array_q_interleaved = np.floor(input_array * (2 ** qbit)).astype(np.int32)
input_array_q_interleaved = np.bitwise_and(input_array_q_interleaved, 0x0fff) # Overflow

# Deinterleave
input_array_q = np.zeros((ninput,)).astype(np.int32)
for i in range(ninput):
  input_array_q[i] = (input_array_q_interleaved[2*i] << nbit) | (input_array_q_interleaved[2*i+1])

# Save
np.savetxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/input_float.txt",input_array)
np.savetxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/input_fpga.txt",input_array_q,fmt="%.6x")
