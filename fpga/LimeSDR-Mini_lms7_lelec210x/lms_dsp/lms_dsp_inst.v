	lms_dsp u0 (
		.clk_clk                             (<connected-to-clk_clk>),                             //             clk.clk
		.fifo_in_wdata                       (<connected-to-fifo_in_wdata>),                       //         fifo_in.wdata
		.fifo_in_wrreq                       (<connected-to-fifo_in_wrreq>),                       //                .wrreq
		.fifo_out_wrdata                     (<connected-to-fifo_out_wrdata>),                     //        fifo_out.wrdata
		.fifo_out_wrreq                      (<connected-to-fifo_out_wrreq>),                      //                .wrreq
		.preamble_detect_cfg_enable          (<connected-to-preamble_detect_cfg_enable>),          // preamble_detect.cfg_enable
		.preamble_detect_cfg_FILTER_LEN      (<connected-to-preamble_detect_cfg_FILTER_LEN>),      //                .cfg_FILTER_LEN
		.preamble_detect_cfg_PASSTHROUGH_LEN (<connected-to-preamble_detect_cfg_PASSTHROUGH_LEN>), //                .cfg_PASSTHROUGH_LEN
		.preamble_detect_cfg_THRESHOLD       (<connected-to-preamble_detect_cfg_THRESHOLD>),       //                .cfg_THRESHOLD
		.preamble_detect_debug_sum           (<connected-to-preamble_detect_debug_sum>),           //                .debug_sum
		.preamble_detect_debug_count         (<connected-to-preamble_detect_debug_count>),         //                .debug_count
		.reset_reset_n                       (<connected-to-reset_reset_n>)                        //           reset.reset_n
	);

