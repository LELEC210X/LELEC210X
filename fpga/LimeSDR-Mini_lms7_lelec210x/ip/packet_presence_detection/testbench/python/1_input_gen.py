import numpy as np
from matplotlib import pyplot as plt

# Input values
startSample = 400
endSample   = 400
pattern     = 30
activeSample= 70
npacket     = 5

amplitude_packet = np.array([0.005,     0.01,   0.05,   0.1,    0.5])
noise_std        = np.array([0.00005,   0.0001, 0.005,  0.001,  0.005,])


n_input_packet = (startSample+activeSample+pattern+endSample)
n_endPacket    = (startSample+activeSample+pattern)
ninput         = n_input_packet*npacket
input_array = np.zeros((2*ninput,)) # Interleaved I/Q
print(len(input_array)/2)
for i in range(npacket):
  print((i*n_input_packet*2 + startSample*2))
  input_array[(i*n_input_packet*2)                :( i   *n_input_packet*2 + startSample*2)] = np.random.randn(2*startSample) * noise_std[i]
  input_array[(i*n_input_packet*2 + startSample*2):( i   *n_input_packet*2 + startSample*2+pattern*2)] = amplitude_packet[i]*1.25
  input_array[(i*n_input_packet*2 + startSample*2+pattern*2):(i*n_input_packet*2 + n_endPacket*2)    ] = (np.random.randint(0,2,2*activeSample) * 2 - 1) *  amplitude_packet[i]
  input_array[(i*n_input_packet*2 + n_endPacket*2)          :((i+1)*n_input_packet*2)                ] = np.random.randn(2*endSample) * noise_std[i]
  

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
np.savetxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/packet_presence_detection/testbench/mentor/input_fpga.txt",input_array_q,fmt="%.6x")

def twos_complement(value,bits):
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value


output_array_fused_q = np.loadtxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/packet_presence_detection/testbench/mentor/input_fpga.txt",delimiter=" ",converters={0:lambda s: int(s,16)}).astype(np.int32)
output_array_q = np.zeros((len(output_array_fused_q),),dtype=np.complex64)
for i in range(len(output_array_fused_q)):
  output_array_q[i ]  = twos_complement((output_array_fused_q[i] >> nbit) & ((1 << nbit)-1),nbit) +1j* twos_complement(output_array_fused_q[i] & ((1 << nbit)-1),nbit)



output_array_q = (output_array_q) * (2**(-qbit))

plt.figure()
plt.plot(np.arange(len(output_array_q)),np.abs(output_array_q))
plt.show()