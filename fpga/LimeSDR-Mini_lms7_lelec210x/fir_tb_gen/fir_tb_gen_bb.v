
module fir_tb_gen (
	clk_clk,
	fir_compiler_ii_0_avalon_streaming_sink_data,
	fir_compiler_ii_0_avalon_streaming_sink_valid,
	fir_compiler_ii_0_avalon_streaming_sink_error,
	fir_compiler_ii_0_avalon_streaming_source_data,
	fir_compiler_ii_0_avalon_streaming_source_valid,
	fir_compiler_ii_0_avalon_streaming_source_error,
	reset_reset_n);	

	input		clk_clk;
	input	[23:0]	fir_compiler_ii_0_avalon_streaming_sink_data;
	input		fir_compiler_ii_0_avalon_streaming_sink_valid;
	input	[1:0]	fir_compiler_ii_0_avalon_streaming_sink_error;
	output	[23:0]	fir_compiler_ii_0_avalon_streaming_source_data;
	output		fir_compiler_ii_0_avalon_streaming_source_valid;
	output	[1:0]	fir_compiler_ii_0_avalon_streaming_source_error;
	input		reset_reset_n;
endmodule
