import numpy as np
<<<<<<< refs/remotes/upstream/main
from scipy.signal import firwin
from plot_utils import *

# Parameters
B   = 50e3
OSR = 8
cutoff  = 150e3
numtaps = 31

# Filter taps
fs   = OSR*B
print(fs)
taps = firwin(numtaps,cutoff,fs=fs)

# Save taps in txt file
np.savetxt('fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_float.txt',taps,newline=",")
=======
from plot_utils import *
from scipy.signal import firwin

# Parameters
B = 50e3
OSR = 8
cutoff = 2 * B
numtaps = 31

# Filter taps
fs = OSR * B
taps = firwin(numtaps, cutoff, fs=fs)

# Save taps in txt file
np.savetxt(
    "fpga/LimeSDR-Mini_lms7_lelec210x/ip/fir/testbench/mentor/taps_float.txt",
    taps,
    newline=",",
)
>>>>>>> Revert "enlever le chain de argu"

# Show Impulse response
plot_time([taps], ["Low-pass filter"], fs)

# Show Frequency response
plot_freq([taps], ["Low-pass filter"], fs)

<<<<<<< refs/remotes/upstream/main
plt.show()
=======
plt.show()
>>>>>>> Revert "enlever le chain de argu"
