// fifo2avs.v

// This file was auto-generated as a prototype implementation of a module
// created in component editor.  It ties off all outputs to ground and
// ignores all inputs.  It needs to be edited to make it do something
// useful.
// 
// This file will not be automatically regenerated.  You should check it in
// to your version control system if you want to keep it.

`timescale 1 ps / 1 ps
module fifo2avs #(
		parameter datawidth = 48
	) (
		output wire [datawidth-1:0] avalon_streaming_source_data,    //                       .data
		output wire        avalon_streaming_source_valid,            //                       .valid
		input  wire        clock_sink_clk,                           //             clock_sink.clk
		input  wire        reset_sink_reset,                         //             reset_sink.reset
		input  wire [datawidth-1:0] fifo_wdata,                      //             conduit_in.wdata
		input  wire        fifo_wrreq                                //                       .wrreq
	);

	reg valid_reg;
	reg [datawidth-1:0] data_reg;

	always @(posedge clock_sink_clk, posedge reset_sink_reset) begin
		if (reset_sink_reset) begin
			valid_reg <= 1'b0;
			data_reg <= 'b0;
		end
		else begin
			data_reg <= fifo_wdata;
			valid_reg <= fifo_wrreq;
		end
	end

	assign avalon_streaming_source_valid = valid_reg;
	assign avalon_streaming_source_data = data_reg;

endmodule
