// (C) 2001-2018 Intel Corporation. All rights reserved.
// Your use of Intel Corporation's design tools, logic functions and other 
// software and tools, and its AMPP partner logic functions, and any output 
// files from any of the foregoing (including device programming or simulation 
// files), and any associated documentation or information are expressly subject 
// to the terms and conditions of the Intel Program License Subscription 
// Agreement, Intel FPGA IP License Agreement, or other applicable 
// license agreement, including, without limitation, that your use is for the 
// sole purpose of programming logic devices manufactured by Intel and sold by 
// Intel or its authorized distributors.  Please refer to the applicable 
// agreement for further details.


// $File: //acds/main/ip/avalon_st/altera_avalon_st_splitter/altera_avalon_st_splitter.sv $
// $Revision: #3 $
// $Date: 2012/01/18 $
// $Author: pscheidt $
//------------------------------------------------------------------------------

`timescale 1ns / 1ns

module altera_avalon_st_splitter #(
   parameter 
      NUMBER_OF_OUTPUTS  = 2, 
      QUALIFY_VALID_OUT  = 1, 
      DATA_WIDTH         = 8,
      BITS_PER_SYMBOL    = 8,
      USE_PACKETS        = 0,   
      CHANNEL_WIDTH      = 1,	   
      ERROR_WIDTH        = 1,
      EMPTY_WIDTH        = 1
  )
(
   output wire                    in0_ready,
   input  wire                    in0_valid,
   input  wire  [DATA_WIDTH-1 :0] in0_data,
   input  wire  [CHANNEL_WIDTH-1 :0] in0_channel,
   input  wire  [ERROR_WIDTH-1   :0] in0_error,
   input  wire                    in0_startofpacket,
   input  wire                    in0_endofpacket,
   input  wire  [EMPTY_WIDTH-1   :0] in0_empty,
   
   input  wire                    out0_ready,
   output wire                    out0_valid,
   output wire  [DATA_WIDTH-1 :0] out0_data,
   output wire  [CHANNEL_WIDTH-1 :0] out0_channel,
   output wire  [ERROR_WIDTH-1   :0] out0_error,
   output wire                    out0_startofpacket,
   output wire                    out0_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out0_empty,
   
   input  wire                    out1_ready,
   output wire                    out1_valid,
   output wire  [DATA_WIDTH-1 :0] out1_data,
   output wire  [CHANNEL_WIDTH-1 :0] out1_channel,
   output wire  [ERROR_WIDTH-1   :0] out1_error,
   output wire                    out1_startofpacket,
   output wire                    out1_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out1_empty,
   
   input  wire                    out2_ready,
   output wire                    out2_valid,
   output wire  [DATA_WIDTH-1 :0] out2_data,
   output wire  [CHANNEL_WIDTH-1 :0] out2_channel,
   output wire  [ERROR_WIDTH-1   :0] out2_error,
   output wire                    out2_startofpacket,
   output wire                    out2_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out2_empty,
   
   input  wire                    out3_ready,
   output wire                    out3_valid,
   output wire  [DATA_WIDTH-1 :0] out3_data,
   output wire  [CHANNEL_WIDTH-1 :0] out3_channel,
   output wire  [ERROR_WIDTH-1   :0] out3_error,
   output wire                    out3_startofpacket,
   output wire                    out3_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out3_empty,
   
   input  wire                    out4_ready,
   output wire                    out4_valid,
   output wire  [DATA_WIDTH-1 :0] out4_data,
   output wire  [CHANNEL_WIDTH-1 :0] out4_channel,
   output wire  [ERROR_WIDTH-1   :0] out4_error,
   output wire                    out4_startofpacket,
   output wire                    out4_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out4_empty,
   
   input  wire                    out5_ready,
   output wire                    out5_valid,
   output wire  [DATA_WIDTH-1 :0] out5_data,
   output wire  [CHANNEL_WIDTH-1 :0] out5_channel,
   output wire  [ERROR_WIDTH-1   :0] out5_error,
   output wire                    out5_startofpacket,
   output wire                    out5_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out5_empty,
   
   input  wire                    out6_ready,
   output wire                    out6_valid,
   output wire  [DATA_WIDTH-1 :0] out6_data,
   output wire  [CHANNEL_WIDTH-1 :0] out6_channel,
   output wire  [ERROR_WIDTH-1   :0] out6_error,
   output wire                    out6_startofpacket,
   output wire                    out6_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out6_empty,
   
   input  wire                    out7_ready,
   output wire                    out7_valid,
   output wire  [DATA_WIDTH-1 :0] out7_data,
   output wire  [CHANNEL_WIDTH-1 :0] out7_channel,
   output wire  [ERROR_WIDTH-1   :0] out7_error,
   output wire                    out7_startofpacket,
   output wire                    out7_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out7_empty,
   
   input  wire                    out8_ready,
   output wire                    out8_valid,
   output wire  [DATA_WIDTH-1 :0] out8_data,
   output wire  [CHANNEL_WIDTH-1 :0] out8_channel,
   output wire  [ERROR_WIDTH-1   :0] out8_error,
   output wire                    out8_startofpacket,
   output wire                    out8_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out8_empty,
   
   input  wire                    out9_ready,
   output wire                    out9_valid,
   output wire  [DATA_WIDTH-1 :0] out9_data,
   output wire  [CHANNEL_WIDTH-1 :0] out9_channel,
   output wire  [ERROR_WIDTH-1   :0] out9_error,
   output wire                    out9_startofpacket,
   output wire                    out9_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out9_empty,
   
   input  wire                    out10_ready,
   output wire                    out10_valid,
   output wire  [DATA_WIDTH-1 :0] out10_data,
   output wire  [CHANNEL_WIDTH-1 :0] out10_channel,
   output wire  [ERROR_WIDTH-1   :0] out10_error,
   output wire                    out10_startofpacket,
   output wire                    out10_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out10_empty,
   
   input  wire                    out11_ready,
   output wire                    out11_valid,
   output wire  [DATA_WIDTH-1 :0] out11_data,
   output wire  [CHANNEL_WIDTH-1 :0] out11_channel,
   output wire  [ERROR_WIDTH-1   :0] out11_error,
   output wire                    out11_startofpacket,
   output wire                    out11_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out11_empty,
   
   input  wire                    out12_ready,
   output wire                    out12_valid,
   output wire  [DATA_WIDTH-1 :0] out12_data,
   output wire  [CHANNEL_WIDTH-1 :0] out12_channel,
   output wire  [ERROR_WIDTH-1   :0] out12_error,
   output wire                    out12_startofpacket,
   output wire                    out12_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out12_empty,
   
   input  wire                    out13_ready,
   output wire                    out13_valid,
   output wire  [DATA_WIDTH-1 :0] out13_data,
   output wire  [CHANNEL_WIDTH-1 :0] out13_channel,
   output wire  [ERROR_WIDTH-1   :0] out13_error,
   output wire                    out13_startofpacket,
   output wire                    out13_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out13_empty,
   
   input  wire                    out14_ready,
   output wire                    out14_valid,
   output wire  [DATA_WIDTH-1 :0] out14_data,
   output wire  [CHANNEL_WIDTH-1 :0] out14_channel,
   output wire  [ERROR_WIDTH-1   :0] out14_error,
   output wire                    out14_startofpacket,
   output wire                    out14_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out14_empty,
   
   input  wire                    out15_ready,
   output wire                    out15_valid,
   output wire  [DATA_WIDTH-1 :0] out15_data,
   output wire  [CHANNEL_WIDTH-1 :0] out15_channel,
   output wire  [ERROR_WIDTH-1   :0] out15_error,
   output wire                    out15_startofpacket,
   output wire                    out15_endofpacket,
   output wire  [EMPTY_WIDTH-1   :0] out15_empty,
   
   input  wire                    clk,
   input  wire                    reset
);


// ********************************************************************
// Module Wiring

wire   [15:0]            OutReady;
wire   [15:0]            OutValid;
wire   [DATA_WIDTH-1 :0] OutData    [15:0];
wire   [CHANNEL_WIDTH-1 :0] OutChannel [15:0];
wire   [ERROR_WIDTH-1   :0] OutError   [15:0];
wire   [15:0]            OutSOP;
wire   [15:0]            OutEOP;
wire   [EMPTY_WIDTH-1   :0] OutEmpty   [15:0];

genvar                   i, j;


// ********************************************************************
// Module Logic

assign in0_ready = &(OutReady[NUMBER_OF_OUTPUTS-1:0]);


generate
   for (i=0; i < NUMBER_OF_OUTPUTS; i=i+1) begin : SPLIT_PORT
      assign OutData[i]    = in0_data;
      assign OutChannel[i] = in0_channel;
      assign OutError[i]   = in0_error;
      assign OutSOP[i]     = in0_startofpacket;
      assign OutEOP[i]     = in0_endofpacket;
      assign OutEmpty[i]   = in0_empty;
   end
endgenerate


generate
   for (j=NUMBER_OF_OUTPUTS; j <16; j=j+1) begin : NULL_PORT
      assign OutData[j]    = {DATA_WIDTH{1'b0}};
      assign OutChannel[j] = {CHANNEL_WIDTH{1'b0}};
      assign OutError[j]   = {ERROR_WIDTH{1'b0}};
      assign OutSOP[j]     = 1'b0;
      assign OutEOP[j]     = 1'b0;
      assign OutEmpty[j]   = {EMPTY_WIDTH{1'b0}};
   end
endgenerate


generate
   if (QUALIFY_VALID_OUT) begin
      assign OutValid[0]  = &{in0_valid, OutReady[15:1]};
      assign OutValid[1]  = &{in0_valid, OutReady[15:2],  OutReady[0]};
      assign OutValid[2]  = &{in0_valid, OutReady[15:3],  OutReady[1:0]};
      assign OutValid[3]  = &{in0_valid, OutReady[15:4],  OutReady[2:0]};
      assign OutValid[4]  = &{in0_valid, OutReady[15:5],  OutReady[3:0]};
      assign OutValid[5]  = &{in0_valid, OutReady[15:6],  OutReady[4:0]};
      assign OutValid[6]  = &{in0_valid, OutReady[15:7],  OutReady[5:0]};
      assign OutValid[7]  = &{in0_valid, OutReady[15:8],  OutReady[6:0]};
      assign OutValid[8]  = &{in0_valid, OutReady[15:9],  OutReady[7:0]};
      assign OutValid[9]  = &{in0_valid, OutReady[15:10], OutReady[8:0]};
      assign OutValid[10] = &{in0_valid, OutReady[15:11], OutReady[9:0]};
      assign OutValid[11] = &{in0_valid, OutReady[15:12], OutReady[10:0]};
      assign OutValid[12] = &{in0_valid, OutReady[15:13], OutReady[11:0]};
      assign OutValid[13] = &{in0_valid, OutReady[15:14], OutReady[12:0]};
      assign OutValid[14] = &{in0_valid, OutReady[15],    OutReady[13:0]};
      assign OutValid[15] = &{in0_valid,                  OutReady[14:0]};
   end
   else begin
      assign OutValid[0]  = in0_valid;
      assign OutValid[1]  = in0_valid;
      assign OutValid[2]  = in0_valid;
      assign OutValid[3]  = in0_valid;
      assign OutValid[4]  = in0_valid;
      assign OutValid[5]  = in0_valid;
      assign OutValid[6]  = in0_valid;
      assign OutValid[7]  = in0_valid;
      assign OutValid[8]  = in0_valid;
      assign OutValid[9]  = in0_valid;
      assign OutValid[10] = in0_valid;
      assign OutValid[11] = in0_valid;
      assign OutValid[12] = in0_valid;
      assign OutValid[13] = in0_valid;
      assign OutValid[14] = in0_valid;
      assign OutValid[15] = in0_valid;
   end
endgenerate


assign OutReady[0]        = out0_ready;
assign out0_valid         = OutValid[0];
assign out0_data          = OutData[0];
assign out0_channel       = OutChannel[0];
assign out0_error         = OutError[0];
assign out0_startofpacket = OutSOP[0];
assign out0_endofpacket   = OutEOP[0];
assign out0_empty         = OutEmpty[0];

assign OutReady[1]        = out1_ready;
assign out1_valid         = OutValid[1];
assign out1_data          = OutData[1];
assign out1_channel       = OutChannel[1];
assign out1_error         = OutError[1];
assign out1_startofpacket = OutSOP[1];
assign out1_endofpacket   = OutEOP[1];
assign out1_empty         = OutEmpty[1];

assign OutReady[2]        = out2_ready;
assign out2_valid         = OutValid[2];
assign out2_data          = OutData[2];
assign out2_channel       = OutChannel[2];
assign out2_error         = OutError[2];
assign out2_startofpacket = OutSOP[2];
assign out2_endofpacket   = OutEOP[2];
assign out2_empty         = OutEmpty[2];

assign OutReady[3]        = out3_ready;
assign out3_valid         = OutValid[3];
assign out3_data          = OutData[3];
assign out3_channel       = OutChannel[3];
assign out3_error         = OutError[3];
assign out3_startofpacket = OutSOP[3];
assign out3_endofpacket   = OutEOP[3];
assign out3_empty         = OutEmpty[3];

assign OutReady[4]        = out4_ready;
assign out4_valid         = OutValid[4];
assign out4_data          = OutData[4];
assign out4_channel       = OutChannel[4];
assign out4_error         = OutError[4];
assign out4_startofpacket = OutSOP[4];
assign out4_endofpacket   = OutEOP[4];
assign out4_empty         = OutEmpty[4];

assign OutReady[5]        = out5_ready;
assign out5_valid         = OutValid[5];
assign out5_data          = OutData[5];
assign out5_channel       = OutChannel[5];
assign out5_error         = OutError[5];
assign out5_startofpacket = OutSOP[5];
assign out5_endofpacket   = OutEOP[5];
assign out5_empty         = OutEmpty[5];

assign OutReady[6]        = out6_ready;
assign out6_valid         = OutValid[6];
assign out6_data          = OutData[6];
assign out6_channel       = OutChannel[6];
assign out6_error         = OutError[6];
assign out6_startofpacket = OutSOP[6];
assign out6_endofpacket   = OutEOP[6];
assign out6_empty         = OutEmpty[6];

assign OutReady[7]        = out7_ready;
assign out7_valid         = OutValid[7];
assign out7_data          = OutData[7];
assign out7_channel       = OutChannel[7];
assign out7_error         = OutError[7];
assign out7_startofpacket = OutSOP[7];
assign out7_endofpacket   = OutEOP[7];
assign out7_empty         = OutEmpty[7];

assign OutReady[8]        = out8_ready;
assign out8_valid         = OutValid[8];
assign out8_data          = OutData[8];
assign out8_channel       = OutChannel[8];
assign out8_error         = OutError[8];
assign out8_startofpacket = OutSOP[8];
assign out8_endofpacket   = OutEOP[8];
assign out8_empty         = OutEmpty[8];

assign OutReady[9]        = out9_ready;
assign out9_valid         = OutValid[9];
assign out9_data          = OutData[9];
assign out9_channel       = OutChannel[9];
assign out9_error         = OutError[9];
assign out9_startofpacket = OutSOP[9];
assign out9_endofpacket   = OutEOP[9];
assign out9_empty         = OutEmpty[9];

assign OutReady[10]        = out10_ready;
assign out10_valid         = OutValid[10];
assign out10_data          = OutData[10];
assign out10_channel       = OutChannel[10];
assign out10_error         = OutError[10];
assign out10_startofpacket = OutSOP[10];
assign out10_endofpacket   = OutEOP[10];
assign out10_empty         = OutEmpty[10];

assign OutReady[11]        = out11_ready;
assign out11_valid         = OutValid[11];
assign out11_data          = OutData[11];
assign out11_channel       = OutChannel[11];
assign out11_error         = OutError[11];
assign out11_startofpacket = OutSOP[11];
assign out11_endofpacket   = OutEOP[11];
assign out11_empty         = OutEmpty[11];

assign OutReady[12]        = out12_ready;
assign out12_valid         = OutValid[12];
assign out12_data          = OutData[12];
assign out12_channel       = OutChannel[12];
assign out12_error         = OutError[12];
assign out12_startofpacket = OutSOP[12];
assign out12_endofpacket   = OutEOP[12];
assign out12_empty         = OutEmpty[12];

assign OutReady[13]        = out13_ready;
assign out13_valid         = OutValid[13];
assign out13_data          = OutData[13];
assign out13_channel       = OutChannel[13];
assign out13_error         = OutError[13];
assign out13_startofpacket = OutSOP[13];
assign out13_endofpacket   = OutEOP[13];
assign out13_empty         = OutEmpty[13];

assign OutReady[14]        = out14_ready;
assign out14_valid         = OutValid[14];
assign out14_data          = OutData[14];
assign out14_channel       = OutChannel[14];
assign out14_error         = OutError[14];
assign out14_startofpacket = OutSOP[14];
assign out14_endofpacket   = OutEOP[14];
assign out14_empty         = OutEmpty[14];

assign OutReady[15]        = out15_ready;
assign out15_valid         = OutValid[15];
assign out15_data          = OutData[15];
assign out15_channel       = OutChannel[15];
assign out15_error         = OutError[15];
assign out15_startofpacket = OutSOP[15];
assign out15_endofpacket   = OutEOP[15];
assign out15_empty         = OutEmpty[15];


endmodule
