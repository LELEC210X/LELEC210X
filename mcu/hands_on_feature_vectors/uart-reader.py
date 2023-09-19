# -*- coding: utf-8 -*-
"""
uart-reader.py 
ELEC PROJECT - 210x
"""
import serial
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

PRINT_PREFIX  = "DF:HEX:"
FREQ_SAMPLING = 10200
MELVEC_LENGTH = 20
N_MELVECS     = 16

dt = np.dtype(np.uint16).newbyteorder('<')

def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX):])
    else:
        print(line)
        return None
    
def reader():
    ser = serial.Serial(port='/dev/ttyACM0',baudrate=115200)
    while True:
        line = ""
        while not line.endswith('\n'):
            line += ser.read_until(b'\n', size=2*N_MELVECS*MELVEC_LENGTH).decode("ascii")
            print(line)
        line = line.strip()
        buffer = parse_buffer(line)
        if buffer is not None:
            buffer_array = np.frombuffer(buffer, dtype=dt)
            
            yield buffer_array
            
def plot_specgram(specgram, ax, is_mel=False, title=None, xlabel='Time index', ylabel='Frequency [Hz]', cmap='jet', cb=True, tf=None, invert=True):
    """Plot a spectrogram (2D matrix) in a chosen axis of a figure.
    Inputs:
        - specgram = spectrogram (2D array)
        - ax       = current axis in figure
        - title    
        - xlabel
        - ylabel
        - cmap
        - cb       = show colorbar if True
        - tf       = final time in xaxis of specgram
    """

    if (tf is None):
        tf = specgram.shape[1]

    if (is_mel):
        ylabel='Frequency [Mel]'
        im = ax.imshow(specgram, cmap=cmap, aspect='auto', extent=[0,tf,specgram.shape[0],0])
    else:
        im = ax.imshow(specgram, cmap=cmap, aspect='auto', extent=[0,tf,int(specgram.size/tf),0])
    if (invert):
        ax.invert_yaxis()

    fig = plt.gcf()
    if (cb):
        fig.colorbar(im, ax=ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    return None
    
if __name__ == '__main__':
    
    print('uart-reader launched...\n')
    
    input_stream = reader()
    msg_counter = 0
    
    for melvec in input_stream:
        msg_counter += 1
        
        print('MEL Spectrogram #{}'.format(msg_counter))
        
        f,ax = plt.subplots(1,1,figsize=(10,5))
        plot_specgram(melvec.reshape((N_MELVECS,MELVEC_LENGTH)).T,ax,is_mel=True,title='MEL Spectrogram #{}'.format(msg_counter))
        plt.draw()
        plt.pause(0.001)
        plt.clf()
