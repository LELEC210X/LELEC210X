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

def load_array(fileName, nbit, qbit):
    array_fused_q= np.loadtxt(fileName,delimiter=" ",converters={0:lambda s: int(s,16)}).astype(np.int32)
    array_q = np.zeros((len(array_fused_q),),dtype = np.complex64)
    for i in range(len(array_fused_q)):
      array_q[i ]  = twos_complement((array_fused_q[i] >> nbit) & ((1 << nbit)-1),nbit) + 1j *twos_complement(array_fused_q[i] & ((1 << nbit)-1),nbit)
    return (array_q) * (2**(-qbit))


output_array = load_array("fpga/LimeSDR-Mini_lms7_lelec210x/ip/packet_presence_detection/testbench/mentor/output_fpga.txt", nbit, qbit)
input_array  = load_array("fpga/LimeSDR-Mini_lms7_lelec210x/ip/packet_presence_detection/testbench/mentor/input_fpga.txt", nbit, qbit)


fig, ax = plt.subplots(2,1,figsize=(12,8))
ax[0].plot(np.arange(len(output_array)), np.real(output_array) , label = "Output of Packet Presence Detection")
ax[0].plot(np.arange(len(input_array)),  np.real(input_array)  , label = "Input  of Packet Presence Detection")
ax[0].set_ylabel("Real part")

ax[1].plot(np.arange(len(output_array)), np.imag(output_array) )
ax[1].plot(np.arange(len(input_array)),  np.imag(input_array)  )
ax[1].set_ylabel("Imaginary part")

ax[1].set_xlabel("Sample number")
ax[0].legend()
plt.show()
pass