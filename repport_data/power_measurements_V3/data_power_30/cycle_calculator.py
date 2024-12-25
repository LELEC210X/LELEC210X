import numpy as np

# Data for "Print FV"
print_fv_cycles = [
    13617390, 13604951, 13718503, 13686416, 13558655, 13587794, 13568988,
    13576194, 13569421
]

# Data for "Encode packet"
encode_packet_cycles = [
    4387050, 4386941, 4387543, 4386771, 4356264, 4356709, 4356692, 4357060
]

# Data for "Send packet"
send_packet_cycles = [
    6579560, 6581921, 6583737, 6582547, 6583266, 6583886, 6582337, 6583807
]

# Data for "CBC MAC"
cbc_mac_cycles = [
    4356264, 4356709, 4356692, 4357060
]

# Data for "Spec shift 1"
spec_shift_1_cycles = [
    3677, 3730, 3731, 3677, 3677, 3677, 3677
]

# Data for "Remove DC component spec"
remove_dc_component_cycles = [
    14892, 14949, 14893, 14892, 14892, 14893, 14892
]

# Data for "Spec mult step 1"
spec_mult_step_1_cycles = [
    3943, 3944, 4002, 3945, 3943, 3943, 3943
]

# Data for "RFFT init"
rfft_init_cycles = [
    86, 86, 86, 86, 86, 86, 86
]

# Data for "RFFT"
rfft_cycles = [
    24002, 24004, 24005, 23941, 23943, 23945, 23943
]

# Data for "Absmax spec"
absmax_spec_cycles = [
    17722, 17368, 17369, 17400, 17469, 15265, 15216
]

# Data for "Complex magnitude"
cmplex_magnitude_cycles = [
    4590, 4944, 4945, 5003, 4946, 4944, 11460, 7748
]

# Data for "Denormalization"
denormalization_cycles = [
    6504, 6446, 6447, 6446, 6446, 6447, 6503, 6446
]

# Data for "Fast matrix mult"
fast_matrix_mult_cycles = [
    20940, 20939, 20888, 20885, 20883, 20941, 20945
]

# Data for "Packet memset"
packet_memset_cycles = [
    237, 237, 237, 237
]

def print_stats(name, cycles):
    print(f"\n{name} Statistics:")
    print(f"Mean: {np.mean(cycles):.2f}")
    print(f"Std Dev: {np.std(cycles):.2f}")
    print(f"Min: {np.min(cycles)}")
    print(f"Max: {np.max(cycles)}")

# Print statistics for each list
print_stats("Print FV", print_fv_cycles)
print_stats("Encode packet", encode_packet_cycles)
print_stats("Send packet", send_packet_cycles)
print_stats("CBC MAC", cbc_mac_cycles)
print_stats("Spec shift 1", spec_shift_1_cycles)
print_stats("Remove DC component", remove_dc_component_cycles)
print_stats("Spec mult step 1", spec_mult_step_1_cycles)
print_stats("RFFT init", rfft_init_cycles)
print_stats("RFFT", rfft_cycles)
print_stats("Absmax spec", absmax_spec_cycles)
print_stats("Complex magnitude", cmplex_magnitude_cycles)
print_stats("Denormalization", denormalization_cycles)
print_stats("Fast matrix mult", fast_matrix_mult_cycles)
print_stats("Packet memset", packet_memset_cycles)