#!/usr/bin/env python


import sys

import matplotlib.pyplot as plt
import numpy as np

filename = str(sys.argv[1])

SNR_list = []
packet_received_list = []
packet_error_list = []
CFO_list = []

static_CFO_corr = 6000

with open(filename, encoding="ISO-8859-1") as openfileobject:
    for line in openfileobject:
        # SYNCHRONIZATION MESSAGE
        if line[0:6] == "[SYNC]":
            # print(line)
            if line[0:21] == "[SYNC] Estimated SNR:":  # recover estimated SNR
                try:
                    SNR = float(line[22:28])
                except:
                    SNR = float(line[22:26])
                # print(SNR)
                SNR_list.append(SNR)

            elif line[0:28] == "[SYNC] New preamble detected":  # recover estimated CFO
                possibility_prev = ""
                for possibility in line.split():
                    try:
                        number = float(possibility.replace(",", "."))
                        if not (
                            possibility_prev == "@"
                        ):  # since several numbers in the same line, make sure extract CFO
                            CFO_list.append(number)
                            # print(number)
                    except ValueError:
                        pass
                    possibility_prev = possibility

        # PER MESSAGE
        elif line[0:4] == "--- ":
            # print(line)
            list_int = [int(s) for s in line.split() if s.isdigit()]
            packet_received_list.append(list_int[0])
            packet_error_list.append(list_int[1])
            # PER = list_int[1]/list_int[0]
            # print(PER)
            # PER_list.append(PER)


CFO_list = np.array(CFO_list) + static_CFO_corr

SNR_mean = np.mean(SNR_list)
SNR_std = np.std(SNR_list)

print("SNR mean", SNR_mean)
print("SNR std", SNR_std)
print("Packets received", packet_received_list[-1])
print("Packet errors", packet_error_list[-1])


plt.figure()
plt.hist(CFO_list, 50)
plt.show()
