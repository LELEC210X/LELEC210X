# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 11:46:35 2024

@author: gauti
"""
import re

class Packet:
    def __init__(self, estimated_cfo=None, estimated_sto=None, estimated_snr=None, 
                 success=None, ber=None, crc=None):
        self.estimated_cfo = estimated_cfo
        self.estimated_sto = estimated_sto
        self.estimated_snr = estimated_snr
        self.success = success
        self.ber = ber
        self.crc = crc

    def __str__(self):
        # Using 'if available' placeholders for attributes that may be None
        return (
            f"Packet Information:\n"
            f"  - Estimated CFO: {self.estimated_cfo if self.estimated_cfo is not None else 'N/A'} Hz\n"
            f"  - Estimated STO: {self.estimated_sto if self.estimated_sto is not None else 'N/A'} samples\n"
            f"  - Estimated SNR: {self.estimated_snr if self.estimated_snr is not None else 'N/A'} dB\n"
            f"  - Packet Successfully Transmitted: {'Yes' if self.success else 'No' if self.success is False else 'N/A'}\n"
            f"  - Bit Error Rate (BER): {f'{self.ber*100:.2f}%' if self.ber is not None else 'N/A'}\n"
            f"  - CRC Value: {self.crc if self.crc is not None else 'N/A'}\n"
        )
    
    def __repr__(self):
        return self.__str__()


class Noise_Query:
    def __init__(self, rx_gain, lpf_status, final_noise_power_db, noise_std_db):
        self.rx_gain = rx_gain
        self.lpf_status = lpf_status
        self.final_noise_power_db = final_noise_power_db
        self.noise_std_db = noise_std_db

    def __str__(self):
        return (f"RX Gain: {self.rx_gain} dB\n"
                f"LPF Status: {self.lpf_status}\n"
                f"Final Estimated Noise Power: {self.final_noise_power_db} dB\n"
                f"Noise Standard Deviation: {self.noise_std_db} dB\n")
    
    def __repr__(self):
        return self.__str__()


def reformat_txt_file(input_filepath, output_filepath=None):
    if output_filepath is None:
        output_filepath = input_filepath  # Overwrite the input file if no output file is specified

    concatenated_lines = []
    current_line = ""

    with open(input_filepath, 'r') as file:
        for line in file:
            # Check if the line starts with a keyword indicating a new log entry
            if line.startswith("INFO:") or line.startswith("ERROR:"):
                # Append the completed log line if we were building one
                if current_line:
                    concatenated_lines.append(current_line)
                # Start a new line for the new log entry
                current_line = line.strip()
            else:
                # Continue the current line for a multi-line packet
                current_line += " " + line.strip()

    # Add the last line if there's anything left
    if current_line:
        concatenated_lines.append(current_line)

    # Write to the output file
    with open(output_filepath, 'w') as output_file:
        for line in concatenated_lines:
            output_file.write(line + '\n')


def calc_BER(byte_values):
    # Expected byte sequence: values 0 through 99
    expected_values = list(range(100))

    # Limit the comparison to the length of crc_values or 100, whichever is shorter
    comparison_length = min(len(byte_values), len(expected_values))

    # Initialize counters for bit comparisons
    total_bits = 0
    error_bits = 0

    # Compare each byte in crc_values to the corresponding byte in expected_values
    for i in range(comparison_length):
        received_byte = byte_values[i]
        expected_byte = expected_values[i]
        
        # XOR to find differing bits, then count the number of 1s in the result
        differing_bits = received_byte ^ expected_byte
        error_bits += bin(differing_bits).count('1')
        total_bits += 8  # Each byte has 8 bits

    # Calculate BER as the ratio of error bits to total bits
    ber = error_bits / total_bits if total_bits > 0 else 0.0
    return ber


def read_packets_txt(filepath):
    packets = []
    current_packet = None

    # Updated regex patterns
    preamble_pattern = re.compile(r"new preamble detected @ \d+ \(CFO (-?\d+\.\d+) Hz, STO (\d+)\)")
    snr_pattern = re.compile(r"estimated SNR: (\d+\.\d+) dB")
    crc_error_pattern = re.compile(r"incorrect CRC, packet dropped: \[.*\] \(CRC: \[(\d+)\]\)")
    success_pattern = re.compile(r"packet successfully demodulated: \[.*\] \(CRC: \[(\d+)\]\)")

    with open(filepath, 'r') as file:
        for line in file:
            if preamble_match := preamble_pattern.search(line):
                # New packet with CFO and STO detected
                estimated_cfo, estimated_sto = map(float, preamble_match.groups())
                current_packet = Packet(estimated_cfo=estimated_cfo, estimated_sto=int(estimated_sto))
                packets.append(current_packet)

            elif snr_match := snr_pattern.search(line):
                # Estimated SNR
                current_packet.estimated_snr = float(snr_match.group(1))

            elif crc_error_match := crc_error_pattern.search(line):
                # Parse CRC value for error case
                crc_value = int(crc_error_match.group(1))
                current_packet.crc = crc_value
                current_packet.success = False
                # Calculate BER based on comparison to expected sequence [0-99]
                byte_values = [int(byte) for byte in re.findall(r"\d+", crc_error_match.group(0).split(":")[1])]
                current_packet.ber = calc_BER(byte_values)

            elif success_match := success_pattern.search(line):
                # Parse CRC value for successful packet
                crc_value = int(success_match.group(1))
                current_packet.crc = crc_value
                current_packet.success = True
                current_packet.ber = 0  # No errors in a successfully demodulated packet

    return packets

def read_noise_queries_txt(filepath):
    noise_queries = []
    with open(filepath, 'r') as file:
        rx_gain, lpf_status, final_noise_power_db, noise_std_db = None, None, None, None
        for line in file:
            # Capture the RX gain and LPF status
            if "dB LPF" in line:
                match = re.match(r"(\d+) dB LPF (\w+)", line)
                if match:
                    rx_gain = int(match.group(1))
                    lpf_status = match.group(2).lower()

            # Capture the final estimated noise power and noise std in dB
            elif "Final estimated noise power" in line:
                match = re.search(r"Final estimated noise power: .+ \(([-\d.]+)dB, Noise std : ([-\d.]+)", line)
                if match:
                    final_noise_power_db = float(match.group(1))
                    noise_std_db = float(match.group(2))

                # Create a new Noise_Query instance and append it to the list
                if rx_gain and lpf_status and final_noise_power_db is not None and noise_std_db is not None:
                    noise_queries.append(
                        Noise_Query(rx_gain, lpf_status, final_noise_power_db, noise_std_db)
                    )
                    # Reset for the next query
                    rx_gain, lpf_status, final_noise_power_db, noise_std_db = None, None, None, None

    return noise_queries


def main():
    reformat_txt_file("Packets.txt", "Packets_reformatted.txt")
    packets = read_packets_txt("Packets_reformatted.txt")
    noise_queries = read_noise_queries_txt("Noise_queries.txt")
    
    for i, packet in enumerate(packets):
        print(f"packet : {i}")
        print(packet)
    
    for i, noise_query in enumerate(noise_queries):
        print(f"Noise query : {i}")
        print(noise_query)

if __name__ == "__main__":
    main()