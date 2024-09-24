import numpy as np
from plot_utils import *

# Parameters
nbit = 8
qbit = 7

# Import taps
try:
    taps = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_float.txt",sep=",")
except(FileNotFoundError):
    print("\nTaps are not generated, run taps_gen.py first!\n")
    exit()

# Quantize (naive: scaling none)
taps_q = np.fix(taps * 2**(qbit)).astype(np.int32) # Round towards zero
np.savetxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_fixed_none.txt",taps_q,fmt="%d")

# Quantize (normalized: scaling auto)
taps_max = np.max(taps)
taps_min = np.min(taps)

# Scaling factor
if (taps_max > -taps_min):
    s = (2**(nbit-qbit-1)-2**(-qbit)) / taps_max
else:
    s = -2**(nbit-qbit-1) / taps_min

taps_n = taps * s
taps_nq = np.fix(taps_n * 2**(qbit)).astype(np.int32)
np.savetxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_fixed_auto.txt",taps_nq,fmt="%d")

# Dequantize
taps_fq = (taps_q.astype(float)) * (2**(-qbit))

taps_nfq = (taps_nq.astype(float)) * (2**(-qbit)) / s

# Show Impulse response
numtaps = taps.shape[-1]
B = 50e3
OSR = 8
fs = OSR*B
plot_time([taps, taps_fq, taps_nfq], ["F32","Q{}.{} scaling 'none'".format(nbit-qbit,qbit),"Q{}.{} scaling 'auto'".format(nbit-qbit,qbit)], fs)

# Show Frequency response
plot_freq([taps, taps_fq, taps_nfq], ["F32","Q{}.{} scaling 'none'".format(nbit-qbit,qbit),"Q{}.{} scaling 'auto'".format(nbit-qbit,qbit)], fs, os=1000)

plt.show()