
module lms_dsp (
	clk_clk,
	fifo_in_wdata,
	fifo_in_wrreq,
	fifo_out_wrdata,
	fifo_out_wrreq,
	ppd_cfg_passthrough_len,
	ppd_cfg_threshold,
	ppd_cfg_clear_rs,
	ppd_debug_count,
	ppd_debug_long_sum,
	ppd_debug_short_sum,
	ppd_cfg_enable_fir,
	ppd_cfg_enable_ppd,
	reset_reset_n);	

	input		clk_clk;
	input	[47:0]	fifo_in_wdata;
	input		fifo_in_wrreq;
	output	[47:0]	fifo_out_wrdata;
	output		fifo_out_wrreq;
	input	[15:0]	ppd_cfg_passthrough_len;
	input	[7:0]	ppd_cfg_threshold;
	input		ppd_cfg_clear_rs;
	output	[31:0]	ppd_debug_count;
	output	[31:0]	ppd_debug_long_sum;
	output	[31:0]	ppd_debug_short_sum;
	input		ppd_cfg_enable_fir;
	input		ppd_cfg_enable_ppd;
	input		reset_reset_n;
endmodule
