
module preamble_detect_tb_gen (
	clock_clk,
	reset_reset,
	sink_data,
	sink_valid,
	source_data,
	source_valid);	

	input		clock_clk;
	input		reset_reset;
	input	[23:0]	sink_data;
	input		sink_valid;
	output	[23:0]	source_data;
	output		source_valid;
endmodule
