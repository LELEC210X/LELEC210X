// preamble_detect.v

// This file was auto-generated as a prototype implementation of a module
// created in component editor.  It ties off all outputs to ground and
// ignores all inputs.  It needs to be edited to make it do something
// useful.
//
// This file will not be automatically regenerated.  You should check it in
// to your version control system if you want to keep it.

`timescale 1 ps / 1 ps

// Macro definitions to pack/unpack an array into a bus
// Basically functions to flatten and unflatten a vector in verilog
// This is required because an array cannot be used as a port (delay_line)

`define PACK_ARRAY(NAME,PK_WIDTH,PK_LEN,PK_SRC,PK_DEST)    genvar pk_idx; generate for (pk_idx=0; pk_idx<(PK_LEN); pk_idx=pk_idx+1) begin : pack_``NAME``_blk assign PK_DEST[((PK_WIDTH)*pk_idx+((PK_WIDTH)-1)):((PK_WIDTH)*pk_idx)] = PK_SRC[pk_idx][((PK_WIDTH)-1):0]; end endgenerate

`define UNPACK_ARRAY(NAME,PK_WIDTH,PK_LEN,PK_DEST,PK_SRC)  genvar unpk_idx; generate for (unpk_idx=0; unpk_idx<(PK_LEN); unpk_idx=unpk_idx+1) begin : pack_``NAME``_blk assign PK_DEST[unpk_idx][((PK_WIDTH)-1):0] = PK_SRC[((PK_WIDTH)*unpk_idx+(PK_WIDTH-1)):((PK_WIDTH)*unpk_idx)]; end endgenerate

// Feedthrough module /!\ Datapath length
module cmplx2mag #(
		parameter integer DATA_WIDTH_IN = 32,
		parameter integer DATA_WIDTH_OUT = 32
	)(
		input wire                       clock,
		input wire                       reset,
		input wire  [DATA_WIDTH_IN -1:0] i,   // int
		input wire  [DATA_WIDTH_IN -1:0] q,   // int
		output wire [DATA_WIDTH_OUT-1:0] mag  // uint
	);

	wire [DATA_WIDTH_IN-1:0]  abs_i, abs_q;
	reg  [DATA_WIDTH_OUT-1:0] mag_reg;

	assign abs_i = i[DATA_WIDTH_IN-1]? (~i+1): i;
  assign abs_q = q[DATA_WIDTH_IN-1]? (~q+1): q;

	wire [DATA_WIDTH_IN-1:0] max, min;
	assign max = (abs_i > abs_q)? abs_i: abs_q;
	assign min = (abs_i > abs_q)? abs_q: abs_i;

	always @(posedge clock) begin
		if (reset) begin
			mag_reg <= 'b0;
		end
		else begin
			mag_reg <= max + (min >> 2);
		end
	end

	assign mag = mag_reg;

endmodule

module delay_line #(
		parameter integer DATA_WIDTH = 32,
		parameter integer DELAY = 8
	)(
		input  wire                          clock,
		input  wire                          reset,
		input  wire                          enable,
		input  wire [DATA_WIDTH-1:0]         in,
		output wire [(DATA_WIDTH*DELAY-1):0] out_packed
	);

	reg [DATA_WIDTH-1:0] delay_reg [0:DELAY-1];

	always @(posedge clock) begin
		if (reset) begin
			for (integer i = 0; i < DELAY; i = i + 1) begin
				delay_reg[i] <= 'b0;
			end
		end
		else if (enable) begin
			delay_reg[0] <= in;
			for (integer i = 0; i < DELAY-1; i = i + 1) begin
				delay_reg[i+1] <= delay_reg[i];
			end
		end
	end

	`PACK_ARRAY(out_packed,DATA_WIDTH,DELAY,delay_reg,out_packed)

endmodule

module running_sum #(
		parameter integer DATA_WIDTH_IN    = 32,
		parameter integer DATA_WIDTH_OUT   = 32,
		parameter integer FILTER_LEN_WIDTH = 8
	)(
		input  wire                          clock,
		input  wire                          reset,
		input  wire                          enable,
		input  wire [(FILTER_LEN_WIDTH-1):0] filter_len,
		input  wire [(DATA_WIDTH_IN-1):0]    in,
		output wire [(DATA_WIDTH_OUT-1):0]   sum
	);

	localparam MAX_FILTER_LEN = 2**FILTER_LEN_WIDTH;

	reg  [(DATA_WIDTH_OUT-1):0] sum_reg;

	wire [(MAX_FILTER_LEN*DATA_WIDTH_IN-1):0] in_delayed_packed;
	wire [(DATA_WIDTH_IN-1):0] in_delayed_unpacked [0:(MAX_FILTER_LEN-1)];
	wire [(DATA_WIDTH_IN-1):0] in_delayed;

	delay_line #(
			.DATA_WIDTH(DATA_WIDTH_IN),
			.DELAY(MAX_FILTER_LEN))
		delay_line_inst (
			.clock(clock),
			.reset(reset),
			.enable(enable),
			.in(in),
			.out_packed(in_delayed_packed)
	);

	`UNPACK_ARRAY(in_delayed,DATA_WIDTH_IN,MAX_FILTER_LEN,in_delayed_unpacked,in_delayed_packed)
	assign in_delayed = in_delayed_unpacked[filter_len];

	always @(posedge clock) begin
		if (reset)
			sum_reg <= 'b0;
		else if (enable)
			sum_reg <= sum_reg + in - in_delayed; // We need a resetable delay_line
	end

	assign sum = sum_reg;

endmodule

module counter #(
		parameter integer DATA_WIDTH = 32
	)(
		input  wire                    clock,
		input  wire                    reset,
		input  wire                    enable,
		input  wire                    launch,
		input  wire [(DATA_WIDTH-1):0] max,
		output wire                    running,
		output wire [(DATA_WIDTH-1):0] count
	);

	reg [DATA_WIDTH-1:0] count_reg;
	reg running_reg;

	always @(posedge clock) begin
		if (reset) begin
			count_reg <= 'b0;
			running_reg <= 'b0;
		end
		else if (enable) begin
			// (if we were counting) or (if the counter is at zero and there is a launch signal)
			if ((count_reg > 'b0) & (count_reg < max) | (launch & (count_reg == 'b0))) begin
				count_reg   <= count_reg + 'b1;
				running_reg <= 'b1;
			end
			// else
			else begin
				count_reg   <= launch; // Do not skip a cycle if launch is high at the end of the count
				running_reg <= launch;
			end
		end
	end

	assign running = running_reg;
	assign count = count_reg;

endmodule

module preamble_detect #(
		parameter integer DATA_WIDTH = 12,
		parameter integer FILTER_LEN_WIDTH = 6,
		parameter integer PASSTHROUGH_LEN_WIDTH = 16
	)(
		input  wire                                clock_sink_clk,                //              clock_sink.clk
		input  wire                                reset_sink_reset,              //              reset_sink.reset
		input  wire                                cfg_enable,                    //                     cfg.enable
		input  wire [(FILTER_LEN_WIDTH-1):0]       cfg_FILTER_LEN,                //                     cfg.FILTER_LEN
		input  wire [(PASSTHROUGH_LEN_WIDTH-1):0]  cfg_PASSTHROUGH_LEN,           //                     cfg.PASSTHROUGH_LEN
		input  wire [31:0]                         cfg_THRESHOLD,                 //                     cfg.THRESHOLD
		input  wire [(2*DATA_WIDTH-1):0]           avalon_streaming_sink_data,    //   avalon_streaming_sink.data
		input  wire                                avalon_streaming_sink_valid,   //                        .valid
		output wire [(2*DATA_WIDTH-1):0]           avalon_streaming_source_data,  // avalon_streaming_source.data
		output wire                                avalon_streaming_source_valid, //                        .valid
		output wire [31:0]                         debug_sum,
		output wire [31:0]                         debug_count
	);
	// ************************************************************
	// *                 LOCALPARAM BUS WIDTHS                    *
	// ************************************************************
	localparam ACC_MAG_WIDTH = DATA_WIDTH + 1;
	localparam ACC_SUM_WIDTH = $clog2((2**ACC_MAG_WIDTH) * (2**FILTER_LEN_WIDTH));

	// ************************************************************
	// *                      CONTROLPATH                         *
	// ************************************************************

	localparam PIPELINE_LEN = 4; // Number of pipeline stages in this module

	// Pipeline all control and data signals
	wire [((2*DATA_WIDTH+2)*PIPELINE_LEN-1):0] pipelined_signals_packed;
	wire [((2*DATA_WIDTH+2)-1):0]              pipelined_signals [PIPELINE_LEN-1:0];
	wire [(2*DATA_WIDTH-1):0]                        data_reg_t0,       data_reg_t1,       data_reg_t2,       data_reg_t3,       data_reg_t4;
	wire                                            valid_reg_t0,      valid_reg_t1,      valid_reg_t2,      valid_reg_t3,      valid_reg_t4;
	wire                                       cfg_enable_reg_t0, cfg_enable_reg_t1, cfg_enable_reg_t2, cfg_enable_reg_t3, cfg_enable_reg_t4;

	// Pipeline of the data and valid signals
	assign {cfg_enable_reg_t0,valid_reg_t0,data_reg_t0} = {cfg_enable,avalon_streaming_sink_valid,avalon_streaming_sink_data};

	delay_line #(
			.DATA_WIDTH(2*DATA_WIDTH+2),
			.DELAY     (PIPELINE_LEN)
		) delay_line_inst (
			.clock     (clock_sink_clk),
			.reset     (reset_sink_reset),
			.enable    (1'b1),
			.in        ({cfg_enable_reg_t0,valid_reg_t0,data_reg_t0}),
			.out_packed(pipelined_signals_packed)
	);

	`UNPACK_ARRAY(pipelined_signals,(2*DATA_WIDTH+2),PIPELINE_LEN,pipelined_signals,pipelined_signals_packed)
	assign {cfg_enable_reg_t1,valid_reg_t1,data_reg_t1} = pipelined_signals[0];
	assign {cfg_enable_reg_t2,valid_reg_t2,data_reg_t2} = pipelined_signals[1];
	assign {cfg_enable_reg_t3,valid_reg_t3,data_reg_t3} = pipelined_signals[2];
	assign {cfg_enable_reg_t4,valid_reg_t4,data_reg_t4} = pipelined_signals[3];

	// ************************************************************
	// *                       DATAPATH                           *
	// ************************************************************

	wire [(ACC_MAG_WIDTH-1):0] mag_t1; // Complex magnitude estimation
	wire [(ACC_SUM_WIDTH-1):0] sum_t2; // Running sum of magnitudes
	wire passthrough_t3;					     // As long as the counter runs, this is at 1
	reg  out_valid_reg_t4;             // Output valid signal

	// STAGE 1 : Complex to Magnitude conversion
	cmplx2mag #(
			.DATA_WIDTH_IN (DATA_WIDTH),
			.DATA_WIDTH_OUT(ACC_MAG_WIDTH)
		) cmplx2mag_inst (
			.clock         (clock_sink_clk),
			.reset         (reset_sink_reset),
			.i             (data_reg_t0[(2*DATA_WIDTH-1):DATA_WIDTH]),
			.q             (data_reg_t0[(DATA_WIDTH-1):0]),
			.mag           (mag_t1)
	);

	// STAGE 2 : Moving Average Filter
	running_sum #(
			.DATA_WIDTH_IN (ACC_MAG_WIDTH),
			.DATA_WIDTH_OUT(ACC_SUM_WIDTH),
			.FILTER_LEN_WIDTH(FILTER_LEN_WIDTH)
		) running_sum_inst (
			.clock           (clock_sink_clk),
			.reset           (reset_sink_reset),
			.enable          (valid_reg_t1),
			.filter_len      (cfg_FILTER_LEN),
			.in              (mag_t1),
			.sum             (sum_t2)
	);
	assign debug_sum = sum_t2;

	// STAGE 3 : Threshold + Sample counter
	counter #(
			.DATA_WIDTH(PASSTHROUGH_LEN_WIDTH)
		) counter_inst (
			.clock     (clock_sink_clk),
			.reset     (reset_sink_reset),
			.enable    (valid_reg_t2),
			.launch    (sum_t2 > cfg_THRESHOLD),
			.max       (cfg_PASSTHROUGH_LEN),
			.running   (passthrough_t3),
			.count     (debug_count)
	);

	// STAGE 4 : Output register
	always @(posedge clock_sink_clk) begin
		if (reset_sink_reset) begin
			out_valid_reg_t4 <= 1'b0;
		end
		else begin
			out_valid_reg_t4 <= cfg_enable_reg_t3 ? (passthrough_t3 & valid_reg_t3) : valid_reg_t3;
		end
	end

	assign avalon_streaming_source_data  = data_reg_t4;
	assign avalon_streaming_source_valid = out_valid_reg_t4;

endmodule
