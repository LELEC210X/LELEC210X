
module lms_dsp (
	clk_clk,
	fifo_in_wdata,
	fifo_in_wrreq,
	fifo_out_wrdata,
	fifo_out_wrreq,
	preamble_detect_cfg_enable,
	preamble_detect_cfg_FILTER_LEN,
	preamble_detect_cfg_PASSTHROUGH_LEN,
	preamble_detect_cfg_THRESHOLD,
	preamble_detect_debug_sum,
	preamble_detect_debug_count,
	reset_reset_n);	

	input		clk_clk;
	input	[47:0]	fifo_in_wdata;
	input		fifo_in_wrreq;
	output	[47:0]	fifo_out_wrdata;
	output		fifo_out_wrreq;
	input		preamble_detect_cfg_enable;
	input	[5:0]	preamble_detect_cfg_FILTER_LEN;
	input	[15:0]	preamble_detect_cfg_PASSTHROUGH_LEN;
	input	[31:0]	preamble_detect_cfg_THRESHOLD;
	output	[31:0]	preamble_detect_debug_sum;
	output	[31:0]	preamble_detect_debug_count;
	input		reset_reset_n;
endmodule
