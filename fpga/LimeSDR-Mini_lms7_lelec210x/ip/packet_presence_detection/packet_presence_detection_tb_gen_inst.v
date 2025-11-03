	packet_presence_detection_tb_gen u0 (
		.sink_valid              (<connected-to-sink_valid>),              //   sink.valid
		.sink_data               (<connected-to-sink_data>),               //       .data
		.source_data             (<connected-to-source_data>),             // source.data
		.source_valid            (<connected-to-source_valid>),            //       .valid
		.clk_clk                 (<connected-to-clk_clk>),                 //    clk.clk
		.reset_reset_n           (<connected-to-reset_reset_n>),           //  reset.reset_n
		.cfg_cfg_passthrough_len (<connected-to-cfg_cfg_passthrough_len>), //    cfg.cfg_passthrough_len
		.cfg_cfg_threshold       (<connected-to-cfg_cfg_threshold>),       //       .cfg_threshold
		.cfg_cfg_clear_rs        (<connected-to-cfg_cfg_clear_rs>),        //       .cfg_clear_rs
		.cfg_debug_count         (<connected-to-cfg_debug_count>),         //       .debug_count
		.cfg_debug_long_sum      (<connected-to-cfg_debug_long_sum>),      //       .debug_long_sum
		.cfg_debug_short_sum     (<connected-to-cfg_debug_short_sum>),     //       .debug_short_sum
		.cfg_cfg_enable_fir      (<connected-to-cfg_cfg_enable_fir>),      //       .cfg_enable_fir
		.cfg_cfg_enable_ppd      (<connected-to-cfg_cfg_enable_ppd>),      //       .cfg_enable_ppd
		.cfg_cfg_pass_sum_signal (<connected-to-cfg_cfg_pass_sum_signal>), //       .cfg_pass_sum_signal
		.cfg_cfg_red_sum_signal  (<connected-to-cfg_cfg_red_sum_signal>)   //       .cfg_red_sum_signal
	);

