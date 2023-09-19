import numpy as np
from matplotlib import pyplot as plt
from numpy.core.numeric import zeros_like

# Dequantize
nbit = 12
qbit = 11

def twos_complement(value,bits):
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

output_array   = np.loadtxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/mentor/output_python.txt")
output_array_fused_q = np.loadtxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/mentor/output_fpga.txt",delimiter="\n",converters={0:lambda s: int(s,16)}).astype(np.int32)
output_array_q = np.zeros((2*len(output_array_fused_q),))
for i in range(len(output_array_fused_q)):
  output_array_q[2*i]   = twos_complement((output_array_fused_q[i] >> nbit) & ((1 << nbit)-1),nbit)
  output_array_q[2*i+1] = twos_complement(output_array_fused_q[i] & ((1 << nbit)-1),nbit)

output_array_q = (output_array_q.astype(np.float)) * (2**(-qbit))

# Fix
output_array_q = np.concatenate((np.zeros((2*37,)), output_array_q[:-2]))

# Plot result
sig_list_list = [
  [output_array[::2], output_array_q[::2], np.abs(output_array[::2] - output_array_q[::2])],
  [output_array[1::2], output_array_q[1::2], np.abs(output_array[1::2] - output_array_q[1::2])]
]
label_list_list = [
  ['python real','fpga real','diff'],
  ['python imag','fpga imag','diff']
]
style_list_list = [
  ['-','--','.'],
  ['-','--','.']
]

f,ax = plt.subplots(len(sig_list_list),1,sharex=True)
for i, sig_list_label_list_style_list in enumerate(zip(sig_list_list,label_list_list,style_list_list)):
  for sig,label,style in zip(*sig_list_label_list_style_list):
      ax[i].plot(np.arange(0,sig.shape[-1]),sig,style,label=label)

  ax[i].legend()

plt.show()

pass