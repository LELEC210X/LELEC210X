import numpy as np
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
    print("\nInputs are not generated, run input_gen.py first!\n")
    exit()

# Compute scaling factor
nbit = 8
qbit = 7
taps_max = np.max(taps)
taps_min = np.min(taps)
if (taps_max > -taps_min):
    s = (2**(nbit-qbit-1)-2**(-qbit)) / taps_max
else:
    s = -2**(nbit-qbit-1) / taps_min

# Output
nbit = 12
qbit = 9
output_array = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/output_float.txt",sep=",")

def twos_complement(value,bits):
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

output_array_fused_q = np.loadtxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/output_fpga.txt",delimiter="\n",converters={0:lambda s: int(s,16)}).astype(np.int32)
output_array_q = np.zeros((2*len(output_array_fused_q),))
for i in range(len(output_array_fused_q)):
  output_array_q[2*i]   = twos_complement((output_array_fused_q[i] >> nbit) & ((1 << nbit)-1),nbit)
  output_array_q[2*i+1] = twos_complement(output_array_fused_q[i] & ((1 << nbit)-1),nbit)

# Dequantize
output_array_fq = (output_array_q.astype(float)) * (2**(-qbit)) / s

# Show Impulse response
output_array    = output_array.reshape((int(len(output_array)/2),2))
output_array_fq = output_array_fq.reshape((int(len(output_array_fq)/2),2))

plot_time([output_array[:,0], output_array[:,1], output_array_fq[:,0], output_array_fq[:,1],], ["F32 Real", "F32 Imag", "Q{}.{} Real".format(nbit-qbit,qbit), "Q{}.{} Imag".format(nbit-qbit,qbit)], fs)

# Show Frequency response
plot_freq([output_array[:,0] + 1j*output_array[:,1], output_array_fq[:,0] + 1j*output_array_fq[:,1],], ["F32", "Q{}.{}".format(nbit-qbit,qbit)], fs, os=4)

plt.show()
