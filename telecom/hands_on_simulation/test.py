"""
Test file, provided to easily check your implementations

/!\ You should comment the last line in basic_chain.py (run_sim(c)) to avoid
launching the full simulation when importing the basic_chain.py file
"""

import numpy as np
from chain import BasicChain
from sim import add_cfo, add_delay

chain = BasicChain()


### Modulation and demodulation
bits = np.array([0, 0, 1, 0, 1, 1, 0])  # choice of bits to send
x_pay = chain.modulate(bits)  # modulated signal with payload
x = x_pay

y, delay = add_delay(
    chain, x, 0
)  # application of ideal channel (if TX and RX oversampling factors are different)


bits_hat = chain.demodulate(y)  # call to demodulation function

print(bits)
print(bits_hat)

# looking at modulated signal...
# plt.figure()
# plt.stem(np.real(y))
# plt.stem(np.unwrap(np.angle(y)))


### CFO correction
cfo_val = 1000

x_pr = chain.modulate(chain.preamble)  # modulated signal containing preamble
x_sync = chain.modulate(chain.sync_word)  # modulated signal containing sync_word
x = np.concatenate((x_pr, x_sync, x_pay))

y, delay = add_delay(chain, x, 0)  # application of ideal channel
y_cfo = add_cfo(chain, y, cfo_val)  # adding CFO
cfo_hat = chain.cfo_estimation(y_cfo)

print(cfo_val)
print(cfo_hat)
