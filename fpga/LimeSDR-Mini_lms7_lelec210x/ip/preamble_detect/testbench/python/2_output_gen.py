import numpy as np
from scipy.signal import convolve
from matplotlib import pyplot as plt

# Input
input_array = np.fromfile("fpga/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/mentor/input_python.txt",sep="\n")

# Preamble detector parameters
qbit = 11
filter_len = 32
threshold = float(int(20480) * (2**(-qbit)))
passthrough_length = 100

# Preamble Detector
input_real_array = input_array[::2]
input_imag_array = input_array[1::2]
magnitude_array = np.sqrt(input_real_array ** 2 + input_imag_array ** 2)
running_sum_array = convolve(magnitude_array, np.ones((filter_len,)), mode="full")[:len(magnitude_array)]

output_array = np.zeros_like(input_array)
counter = 0
passthrough = False
for i in range(len(output_array)//2):
    if passthrough:
        output_array[2*i:2*(i+1)] = input_array[2*i:2*(i+1)]
        counter += 1
    else:
        output_array[2*i:2*(i+1)] = 0

    if counter == passthrough_length:
        counter = 0
        passthrough = False
    if (running_sum_array[i] > threshold):
        passthrough = True

output_real_array = output_array[::2]
output_imag_array = output_array[1::2]

np.savetxt("fpga/LimeSDR-Mini_lms7_lelec210x/ip/preamble_detect/testbench/mentor/output_python.txt",output_array)

# Plot result
sig_list1 = [input_real_array, input_imag_array, output_real_array, output_imag_array]
label_list1 = ['input real','input imag','output real','output imag']
sig_list2 = [running_sum_array, np.ones_like(running_sum_array) * threshold]
label_list2 = ['running sum','threshold']

f, ax = plt.subplots(2,1,sharex=True)
for i,sig_label in enumerate(zip(sig_list1, label_list1)):
    sig,label = sig_label
    ax[0].plot(np.arange(0,sig.shape[-1]),sig,'-' if (i % 2 == 0) else '--',label=label)
    
ax[0].set_ylabel("Amplitude")
ax[0].legend()

for sig,label in zip(sig_list2, label_list2):
    ax[1].plot(np.arange(0,sig.shape[-1]),sig,label=label)
    
ax[1].set_xlabel("Time [s]")
ax[1].set_ylabel("Amplitude")
ax[1].legend()

plt.show()