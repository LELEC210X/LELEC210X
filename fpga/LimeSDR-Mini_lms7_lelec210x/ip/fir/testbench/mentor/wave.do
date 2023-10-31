onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate -radix binary /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/clk_clk
add wave -noupdate -radix binary /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/reset_reset_n
add wave -noupdate -expand -group Input -radix hexadecimal /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/fir_compiler_ii_0_avalon_streaming_sink_data
add wave -noupdate -expand -group Input -radix hexadecimal /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/fir_compiler_ii_0_avalon_streaming_sink_valid
add wave -noupdate -expand -group Input -radix hexadecimal /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/fir_compiler_ii_0_avalon_streaming_sink_error
add wave -noupdate -expand -group Output -radix hexadecimal /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/fir_compiler_ii_0_avalon_streaming_source_data
add wave -noupdate -expand -group Output -radix hexadecimal /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/fir_compiler_ii_0_avalon_streaming_source_valid
add wave -noupdate -expand -group Output -radix hexadecimal /top_tb/fir_tb_gen_tb_inst/fir_tb_gen_inst/fir_compiler_ii_0_avalon_streaming_source_error
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {366753 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 322
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 1
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ps
update
WaveRestoreZoom {448991 ps} {602837 ps}
