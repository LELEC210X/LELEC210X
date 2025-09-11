set_global_assignment -entity "packet_presence_detection_tb_gen" -library "lib_packet_presence_detection_tb_gen" -name IP_TOOL_NAME "Qsys"
set_global_assignment -entity "packet_presence_detection_tb_gen" -library "lib_packet_presence_detection_tb_gen" -name IP_TOOL_VERSION "18.1"
set_global_assignment -entity "packet_presence_detection_tb_gen" -library "lib_packet_presence_detection_tb_gen" -name IP_TOOL_ENV "Qsys"
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name SPD_FILE [file join $::quartus(sip_path) "../packet_presence_detection_tb_gen.spd"]
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "../../packet_presence_detection_tb_gen.qsys"]

set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "packet_presence_detection_tb_gen.v"]
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "submodules/packet_presence_detection.sv"]
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "submodules/short_shift.v"]
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "submodules/long_shift.v"]
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "submodules/verbosity_pkg.sv"]
set_global_assignment -library "lib_packet_presence_detection_tb_gen" -name MISC_FILE [file join $::quartus(sip_path) "submodules/packet_presence_detection_tb_gen_conduit_bfm_0.sv"]
