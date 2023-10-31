// (C) 2001-2018 Intel Corporation. All rights reserved.
<<<<<<< refs/remotes/upstream/main
// Your use of Intel Corporation's design tools, logic functions and other 
// software and tools, and its AMPP partner logic functions, and any output 
// files from any of the foregoing (including device programming or simulation 
// files), and any associated documentation or information are expressly subject 
// to the terms and conditions of the Intel Program License Subscription 
// Agreement, Intel FPGA IP License Agreement, or other applicable 
// license agreement, including, without limitation, that your use is for the 
// sole purpose of programming logic devices manufactured by Intel and sold by 
// Intel or its authorized distributors.  Please refer to the applicable 
=======
// Your use of Intel Corporation's design tools, logic functions and other
// software and tools, and its AMPP partner logic functions, and any output
// files from any of the foregoing (including device programming or simulation
// files), and any associated documentation or information are expressly subject
// to the terms and conditions of the Intel Program License Subscription
// Agreement, Intel FPGA IP License Agreement, or other applicable
// license agreement, including, without limitation, that your use is for the
// sole purpose of programming logic devices manufactured by Intel and sold by
// Intel or its authorized distributors.  Please refer to the applicable
>>>>>>> Revert "enlever le chain de argu"
// agreement for further details.


// (C) 2001-2013 Altera Corporation. All rights reserved.
<<<<<<< refs/remotes/upstream/main
// Your use of Altera Corporation's design tools, logic functions and other 
// software and tools, and its AMPP partner logic functions, and any output 
// files any of the foregoing (including device programming or simulation 
// files), and any associated documentation or information are expressly subject 
// to the terms and conditions of the Altera Program License Subscription 
// Agreement, Altera MegaCore Function License Agreement, or other applicable 
// license agreement, including, without limitation, that your use is for the 
// sole purpose of programming logic devices manufactured by Altera and sold by 
// Altera or its authorized distributors.  Please refer to the applicable 
// agreement for further details.

 
=======
// Your use of Altera Corporation's design tools, logic functions and other
// software and tools, and its AMPP partner logic functions, and any output
// files any of the foregoing (including device programming or simulation
// files), and any associated documentation or information are expressly subject
// to the terms and conditions of the Altera Program License Subscription
// Agreement, Altera MegaCore Function License Agreement, or other applicable
// license agreement, including, without limitation, that your use is for the
// sole purpose of programming logic devices manufactured by Altera and sold by
// Altera or its authorized distributors.  Please refer to the applicable
// agreement for further details.


>>>>>>> Revert "enlever le chain de argu"
// $Id: //acds/rel/13.1/ip/.../avalon-st_timing_adapter.sv.terp#1 $
// $Revision: #1 $
// $Date: 2013/09/27 $
// $Author: dmunday, korthner $

// --------------------------------------------------------------------------------
//| Avalon Streaming Timing Adapter
// --------------------------------------------------------------------------------

`timescale 1ns / 100ps
// ------------------------------------------
// Generation parameters:
//   output_name:        lms_dsp_avalon_st_adapter_timing_adapter_1
//   in_use_ready:       true
//   out_use_ready:      false
//   in_use_valid:       true
//   out_use_valid:      true
//   use_packets:        false
//   use_empty:          0
//   empty_width:        0
<<<<<<< refs/remotes/upstream/main
//   data_width:         48
//   channel_width:      0
//   error_width:        0
//   in_ready_latency:   0
//   out_ready_latency:  0
//   in_payload_width:   48
//   out_payload_width:  48
//   in_payload_map:     in_data
//   out_payload_map:    out_data
=======
//   data_width:         24
//   channel_width:      0
//   error_width:        2
//   in_ready_latency:   0
//   out_ready_latency:  0
//   in_payload_width:   26
//   out_payload_width:  26
//   in_payload_map:     in_data,in_error
//   out_payload_map:    out_data,out_error
>>>>>>> Revert "enlever le chain de argu"
// ------------------------------------------



module lms_dsp_avalon_st_adapter_timing_adapter_1
<<<<<<< refs/remotes/upstream/main
(  
 output reg         in_ready,
 input               in_valid,
 input     [48-1: 0]  in_data,
 // Interface: out
 output reg          out_valid,
 output reg [48-1: 0] out_data,
=======
(
 output reg         in_ready,
 input               in_valid,
 input     [24-1: 0]  in_data,
 input     [2-1: 0] in_error,
 // Interface: out
 output reg          out_valid,
 output reg [24-1: 0] out_data,
 output reg [2-1: 0] out_error,
>>>>>>> Revert "enlever le chain de argu"
  // Interface: clk
 input              clk,
 // Interface: reset
 input              reset_n

 /*AUTOARG*/);

   // ---------------------------------------------------------------------
   //| Signal Declarations
   // ---------------------------------------------------------------------
<<<<<<< refs/remotes/upstream/main
   
   reg [48-1:0]   in_payload;
   reg [48-1:0]   out_payload;
   reg [1-1:0]   ready;   
=======

   reg [26-1:0]   in_payload;
   reg [26-1:0]   out_payload;
   reg [1-1:0]   ready;
>>>>>>> Revert "enlever le chain de argu"

   // ---------------------------------------------------------------------
   //| Payload Mapping
   // ---------------------------------------------------------------------
   always @* begin
<<<<<<< refs/remotes/upstream/main
     in_payload = {in_data};
     {out_data} = out_payload;
=======
     in_payload = {in_data,in_error};
     {out_data,out_error} = out_payload;
>>>>>>> Revert "enlever le chain de argu"
   end

   // ---------------------------------------------------------------------
   //| Ready & valid signals.
   // ---------------------------------------------------------------------
   always_comb begin
     ready[0] = 1;
     out_valid = in_valid;
     out_payload = in_payload;
     in_ready    = ready[0];
   end




endmodule
<<<<<<< refs/remotes/upstream/main


=======
>>>>>>> Revert "enlever le chain de argu"
