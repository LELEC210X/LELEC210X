
module packet_presence_detection_tb_gen (
	sink_valid,
	sink_data,
	source_data,
	source_valid,
	clk_clk,
	reset_reset_n,
	cfg_cfg_passthrough_len,
	cfg_cfg_threshold,
	cfg_cfg_clear_rs,
	cfg_debug_count,
	cfg_debug_long_sum,
	cfg_debug_short_sum,
	cfg_cfg_enable_fir,
	cfg_cfg_enable_ppd,
	cfg_cfg_pass_sum_signal,
	cfg_cfg_red_sum_signal);	

	input		sink_valid;
	input	[23:0]	sink_data;
	output	[23:0]	source_data;
	output		source_valid;
	input		clk_clk;
	input		reset_reset_n;
	input	[15:0]	cfg_cfg_passthrough_len;
	input	[7:0]	cfg_cfg_threshold;
	input		cfg_cfg_clear_rs;
	output	[31:0]	cfg_debug_count;
	output	[31:0]	cfg_debug_long_sum;
	output	[31:0]	cfg_debug_short_sum;
	input		cfg_cfg_enable_fir;
	input		cfg_cfg_enable_ppd;
	input		cfg_cfg_pass_sum_signal;
	input		cfg_cfg_red_sum_signal;
endmodule
