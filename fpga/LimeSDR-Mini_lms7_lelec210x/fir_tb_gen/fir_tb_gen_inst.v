	fir_tb_gen u0 (
		.clk_clk                                         (<connected-to-clk_clk>),                                         //                                       clk.clk
		.fir_compiler_ii_0_avalon_streaming_sink_data    (<connected-to-fir_compiler_ii_0_avalon_streaming_sink_data>),    //   fir_compiler_ii_0_avalon_streaming_sink.data
		.fir_compiler_ii_0_avalon_streaming_sink_valid   (<connected-to-fir_compiler_ii_0_avalon_streaming_sink_valid>),   //                                          .valid
		.fir_compiler_ii_0_avalon_streaming_sink_error   (<connected-to-fir_compiler_ii_0_avalon_streaming_sink_error>),   //                                          .error
		.fir_compiler_ii_0_avalon_streaming_source_data  (<connected-to-fir_compiler_ii_0_avalon_streaming_source_data>),  // fir_compiler_ii_0_avalon_streaming_source.data
		.fir_compiler_ii_0_avalon_streaming_source_valid (<connected-to-fir_compiler_ii_0_avalon_streaming_source_valid>), //                                          .valid
		.fir_compiler_ii_0_avalon_streaming_source_error (<connected-to-fir_compiler_ii_0_avalon_streaming_source_error>), //                                          .error
		.reset_reset_n                                   (<connected-to-reset_reset_n>)                                    //                                     reset.reset_n
	);

