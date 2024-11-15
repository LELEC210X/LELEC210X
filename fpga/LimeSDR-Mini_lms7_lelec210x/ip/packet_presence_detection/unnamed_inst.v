	unnamed u0 (
		.cfg_PASSTHROUGH_LEN           (<connected-to-cfg_PASSTHROUGH_LEN>),           //                     cfg.cfg_passthrough_len
		.cfg_THRESHOLD                 (<connected-to-cfg_THRESHOLD>),                 //                        .cfg_threshold
		.cfg_clear_rs                  (<connected-to-cfg_clear_rs>),                  //                        .cfg_clear_rs
		.cfg_enable                    (<connected-to-cfg_enable>),                    //                        .cfg_enable
		.debug_count                   (<connected-to-debug_count>),                   //                        .debug_count
		.debug_long_sum                (<connected-to-debug_long_sum>),                //                        .debug_long_sum
		.debug_short_sum               (<connected-to-debug_short_sum>),               //                        .debug_short_sum
		.avalon_streaming_sink_data    (<connected-to-avalon_streaming_sink_data>),    //   avalon_streaming_sink.data
		.avalon_streaming_sink_valid   (<connected-to-avalon_streaming_sink_valid>),   //                        .valid
		.avalon_streaming_source_data  (<connected-to-avalon_streaming_source_data>),  // avalon_streaming_source.data
		.avalon_streaming_source_valid (<connected-to-avalon_streaming_source_valid>), //                        .valid
		.clock_sink_clk                (<connected-to-clock_sink_clk>),                //              clock_sink.clk
		.reset_sink_reset              (<connected-to-reset_sink_reset>)               //              reset_sink.reset
	);

