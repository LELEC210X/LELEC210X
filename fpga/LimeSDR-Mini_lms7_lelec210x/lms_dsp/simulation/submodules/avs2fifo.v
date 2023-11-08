// avs2fifo.v

// This file was auto-generated as a prototype implementation of a module
// created in component editor.  It ties off all outputs to ground and
// ignores all inputs.  It needs to be edited to make it do something
// useful.
// 
// This file will not be automatically regenerated.  You should check it in
// to your version control system if you want to keep it.

`timescale 1 ps / 1 ps
module avs2fifo #(
		parameter datawidth = 48
	) (
		input  wire        clock_sink_clk,                       //            clock_sink.clk
		input  wire        reset_sink_reset,                     //            reset_sink.reset
		input  wire [datawidth-1:0] avalon_streaming_sink_data,  // avalon_streaming_sink.data
		input  wire        avalon_streaming_sink_valid,          //                      .valid
		output wire [datawidth-1:0] fifo_wrdata,                 //           conduit_end.wrdata
		output wire        fifo_wrreq                            //                      .wrreq
	);

	reg wrreq_reg;
	reg [datawidth-1:0] wrdata_reg;

	always @(posedge clock_sink_clk, posedge reset_sink_reset) begin
		if (reset_sink_reset) begin
			wrreq_reg <= 1'b0;
			wrdata_reg <= 'b0;
		end
		else begin
			wrreq_reg <= avalon_streaming_sink_valid;
			wrdata_reg <= avalon_streaming_sink_data;
		end
	end

	assign fifo_wrreq = wrreq_reg;
	assign fifo_wrdata = wrdata_reg;

endmodule
