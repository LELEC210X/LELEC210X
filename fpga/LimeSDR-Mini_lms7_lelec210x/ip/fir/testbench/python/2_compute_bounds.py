
# References:
# https://nl.mathworks.com/help/dsp/ug/concepts-and-terminology.html
# https://nl.mathworks.com/help/dsp/ug/fixed-point-precision-rules-for-avoiding-overflow-in-fir-filters.html

import numpy as np

# We use two's complement numbers
sign = 1

# Input bitwidth
# 12-bit determined by LMS7002M protocol
nbit_sig = 12

# /!\ Assumption about input signal format : bounded between -1 and 0.9995
# In practice this assumption is always satisfied as we do not care about measuring the input signal amplitude, 
# we only care about its frequency for demodulation
qbit_in_sig = 11
x_min = -2 ** (nbit_sig - sign - qbit_in_sig)
x_max = 2 ** (nbit_sig - sign - qbit_in_sig) - 2 ** (-qbit_in_sig)

# Import taps
try:
    taps = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_float.txt",sep=",")
except(FileNotFoundError):
    print("\nTaps are not generated, run taps_gen.py first!\n")
    exit()

# Compute Min/Max values of the taps
taps_pos = np.sum(taps * (taps > 0))
taps_neg = np.sum(taps * (taps < 0))
taps_max = np.max(taps)
taps_min = np.min(taps)

print("Scaling 'None': taps_max\t:", taps_max)
print("Scaling 'None': taps_min\t:", taps_min)

# The FPGA FIR IP lets you choose the fractional bit width
# We fix it to .7 to limit FPGA utilization
qbit_taps = 7

# It further allows to choose between two modes of quantization : Scaling 'None' or 'Auto'
# a) No scaling
# Integer part determined by the maximum of absolute values
pbit_taps = np.ceil(np.max((np.max((np.log2(-taps_min),0)),np.max((np.log2(taps_max),0)))))
nbit_taps = int(sign + pbit_taps + qbit_taps)
print("Scaling 'None': taps format\t: Q{}.{} - range: [{},{}]".format(nbit_taps-qbit_taps,qbit_taps, -2**(pbit_taps), 2**(pbit_taps)-2**(-qbit_taps)))

# b) With scaling : the coefficients are normalized between -1 and 1, so the representation is always Q1.<qbit_taps>
if (taps_max > -taps_min):
    s = (1.0 - 2**(-qbit_taps)) / taps_max
else:
    s = -1.0 / taps_min

print("")
print("Scaling 'Auto': taps_max\t:", taps_max*s)
print("Scaling 'Auto': taps_min\t:", taps_min*s)

print("Scaling 'Auto': taps format\t: Q{}.{} - range: [{},{}]".format(1,qbit_taps, -1.0, 1.0 - 2**(-qbit_taps)))
print("Scaling 'Auto': scaling factor\t: {}".format(s))

# Compute Min/Max values for the filtered signal
y_max = taps_pos * x_max + taps_neg * x_min
y_min = taps_neg * x_max + taps_pos * x_min

print("")
print("Scaling 'None': y_max\t\t:", y_max)
print("Scaling 'None': y_min\t\t:", y_min)

pbit_out_sig = np.ceil(np.max((np.max((np.log2(-y_min),0)),np.max((np.log2(y_max),0)))))
qbit_out_sig = int(nbit_sig - sign - pbit_out_sig)
print("Scaling 'None': y format\t: Q{}.{} - range: [{},{}]".format(nbit_sig-qbit_out_sig,qbit_out_sig, -2**(nbit_sig-qbit_out_sig-1), 2**(nbit_sig-qbit_out_sig-1)-2**(-qbit_out_sig)))

print("")
print("Scaling 'Auto': y_max\t\t:", y_max*s)
print("Scaling 'Auto': y_min\t\t:", y_min*s)

pbit_out_sig_scaled = np.ceil(np.max((np.max((np.log2(-y_min*s),0)),np.max((np.log2(y_max*s),0)))))
qbit_out_sig_scaled = int(nbit_sig - sign - pbit_out_sig_scaled)

print("Scaling 'Auto': y format\t: Q{}.{} - range: [{},{}]".format(nbit_sig-qbit_out_sig_scaled,qbit_out_sig_scaled, -2**(nbit_sig-qbit_out_sig_scaled-1), 2**(nbit_sig-qbit_out_sig_scaled-1)-2**(-qbit_out_sig_scaled)))