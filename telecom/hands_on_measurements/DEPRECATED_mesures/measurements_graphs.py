# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 16:14:12 2024

@author: gauti
"""

import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import sys

# custom imports
sys.path.append("../../hands_on_simulation/")
from sim import plot_BER_PER
from chain import Chain, BasicChain
sys.path.remove("../../hands_on_simulation/")
from read_measurements import Packet, Noise_Query, reformat_txt_file, read_packets_txt, read_noise_queries_txt


def plot_graphs(chain: Chain, packets: list[Packet], noise_queries: list[Noise_Query], save=True, show=True, **kwargs):
    
    # Read file:
    try:
        filename = kwargs['filename']
        data = np.loadtxt(f"../../hands_on_simulation/data/{filename}.csv", delimiter=",", skiprows=1)
    except:
        raise FileNotFoundError(f"No such data file found: ../../hands_on_simulation/data/{kwargs['filename']}.csv\nPlease call the function with filename=valid_filename")
        
    SNRs_dB = data[:,0].astype(int)
    BER = data[:,2]
    PER = data[:,3]
    
    measured_SNRs_db = []
    measured_BER = []
    measured_crc = []
    min_SNR = len(chain.snr_range)
    for i, packet in enumerate(packets):
        measured_SNRs_db.append(packet.estimated_snr)
        measured_BER.append(packet.ber)
        measured_crc.append(255*(int(packet.crc==195)))
        if packet.success:
            min_SNR = min(min_SNR, packet.estimated_snr)
        
        
    plot_kwargs = dict(figsize=(8,6), layout="constrained")
    cmap = plt.colormaps["RdYlGn"]
    
    BER_fig, PER_fig, BER_ax, _, PER_ax, _ = plot_BER_PER(chain, SNRs_dB, BER, PER, **plot_kwargs)
    BER_ax.scatter(measured_SNRs_db, measured_BER, marker='x', color=cmap(measured_crc), label="Measured packets\nRed = wrong CRC")
    BER_ax.legend(loc=3)
    

    # pc = PatchCollection(backgrounds, facecolor=facecolor, alpha=alpha)
    PER_ax.add_patch(Rectangle((PER_ax.get_xlim()[0], PER_ax.get_ylim()[0]), min_SNR, PER_ax.get_ylim()[1], facecolor="r", alpha=.3))
    PER_ax.add_patch(Rectangle((min_SNR, PER_ax.get_ylim()[0]), PER_ax.get_xlim()[1], PER_ax.get_ylim()[1], facecolor="g", alpha=.3, label="Successfully transmitted packet measured"))
    PER_ax.legend(loc=3)
    
    if save:
        if not os.path.exists("graphs"):
            os.makedirs("graphs")
        BER_fig.savefig(f"graphs/BER_n_{chain.n_packets}_p_{chain.payload_len}.pdf", dpi=300)
        PER_fig.savefig(f"graphs/PER_n_{chain.n_packets}_p_{chain.payload_len}.pdf", dpi=300)
    
    if show:
        plt.show()


def main():
    reformat_txt_file("Packets.txt", "Packets_reformatted.txt")
    packets = read_packets_txt("Packets_reformatted.txt")
    noise_queries = read_noise_queries_txt("Noise_queries.txt")

    # It is better to compare with similar simulation parameters and large n_packets 
    chain = BasicChain(bypass_cfo_estimation=False, bypass_preamble_detect=False, bypass_sto_estimation=False)
    # chain = BasicChain(payload_len=800, n_packets=100_000, cfo_Moose_N=16, bypass_cfo_estimation=False, bypass_preamble_detect=False, bypass_sto_estimation=False)
    
    filename = f"sim_p_{chain.payload_len}_n_{chain.n_packets}_" + \
            f"pre_det_{'OFF' if chain.bypass_preamble_detect else 'ON'}_" + \
            f"cfo_est_{'OFF' if chain.bypass_cfo_estimation else f'ON(N={chain.cfo_Moose_N},range={chain.cfo_range:.0f})'}_" + \
            f"sto_est_{'OFF' if chain.bypass_sto_estimation else 'ON'}"
    
    plot_graphs(chain, packets, noise_queries, filename=filename)

if __name__ == "__main__":
    main()