
module lms_dsp (
	clk_clk,
	fifo_in_wdata,
	fifo_in_wrreq,
	fifo_out_wrdata,
	fifo_out_wrreq,
<<<<<<< refs/remotes/upstream/main
	ppd_cfg_passthrough_len,
	ppd_cfg_threshold,
	ppd_cfg_clear_rs,
	ppd_cfg_enable,
	ppd_debug_count,
	ppd_debug_long_sum,
	ppd_debug_short_sum,
	reset_reset_n);	
=======
	preamble_detect_cfg_enable,
	preamble_detect_cfg_FILTER_LEN,
	preamble_detect_cfg_PASSTHROUGH_LEN,
	preamble_detect_cfg_THRESHOLD,
	preamble_detect_debug_sum,
	preamble_detect_debug_count,
	reset_reset_n);
>>>>>>> Revert "enlever le chain de argu"

	input		clk_clk;
	input	[47:0]	fifo_in_wdata;
	input		fifo_in_wrreq;
	output	[47:0]	fifo_out_wrdata;
	output		fifo_out_wrreq;
<<<<<<< refs/remotes/upstream/main
	input	[15:0]	ppd_cfg_passthrough_len;
	input	[15:0]	ppd_cfg_threshold;
	input		ppd_cfg_clear_rs;
	input		ppd_cfg_enable;
	output	[31:0]	ppd_debug_count;
	output	[31:0]	ppd_debug_long_sum;
	output	[31:0]	ppd_debug_short_sum;
=======
	input		preamble_detect_cfg_enable;
	input	[5:0]	preamble_detect_cfg_FILTER_LEN;
	input	[15:0]	preamble_detect_cfg_PASSTHROUGH_LEN;
	input	[31:0]	preamble_detect_cfg_THRESHOLD;
	output	[31:0]	preamble_detect_debug_sum;
	output	[31:0]	preamble_detect_debug_count;
>>>>>>> Revert "enlever le chain de argu"
	input		reset_reset_n;
endmodule
