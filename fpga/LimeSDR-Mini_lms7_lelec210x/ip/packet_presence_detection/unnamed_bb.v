
module unnamed (
	cfg_PASSTHROUGH_LEN,
	cfg_THRESHOLD,
	cfg_clear_rs,
	cfg_enable,
	debug_count,
	debug_long_sum,
	debug_short_sum,
	avalon_streaming_sink_data,
	avalon_streaming_sink_valid,
	avalon_streaming_source_data,
	avalon_streaming_source_valid,
	clock_sink_clk,
	reset_sink_reset);	

	input	[15:0]	cfg_PASSTHROUGH_LEN;
	input	[7:0]	cfg_THRESHOLD;
	input		cfg_clear_rs;
	input		cfg_enable;
	output	[31:0]	debug_count;
	output	[31:0]	debug_long_sum;
	output	[31:0]	debug_short_sum;
	input	[23:0]	avalon_streaming_sink_data;
	input		avalon_streaming_sink_valid;
	output	[23:0]	avalon_streaming_source_data;
	output		avalon_streaming_source_valid;
	input		clock_sink_clk;
	input		reset_sink_reset;
endmodule
