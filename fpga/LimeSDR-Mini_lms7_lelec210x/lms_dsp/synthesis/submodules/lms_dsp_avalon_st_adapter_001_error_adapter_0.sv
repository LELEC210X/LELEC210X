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
// $Id: //acds/rel/13.1/ip/.../avalon-st_error_adapter.sv.terp#1 $
// $Revision: #1 $
// $Date: 2013/09/09 $
// $Author: dmunday $


// --------------------------------------------------------------------------------
//| Avalon Streaming Error Adapter
// --------------------------------------------------------------------------------

`timescale 1ns / 100ps

// ------------------------------------------
// Generation parameters:
//   output_name:        lms_dsp_avalon_st_adapter_001_error_adapter_0
<<<<<<< refs/remotes/upstream/main
//   use_ready:          true
=======
//   use_ready:          false
>>>>>>> Revert "enlever le chain de argu"
//   use_packets:        false
//   use_empty:          0
//   empty_width:        0
//   data_width:         24
//   channel_width:      0
<<<<<<< refs/remotes/upstream/main
//   in_error_width:     0
//   out_error_width:    2
//   in_errors_list      
//   in_errors_indices   0
//   out_errors_list     
=======
//   in_error_width:     2
//   out_error_width:    0
//   in_errors_list
//   in_errors_indices   0 1
//   out_errors_list
>>>>>>> Revert "enlever le chain de argu"
//   has_in_error_desc:  FALSE
//   has_out_error_desc: FALSE
//   out_has_other:      FALSE
//   out_other_index:    -1
<<<<<<< refs/remotes/upstream/main
//   dumpVar:            
=======
//   dumpVar:
>>>>>>> Revert "enlever le chain de argu"
//   inString:            in_error[
//   closeString:        ] |

// ------------------------------------------




module lms_dsp_avalon_st_adapter_001_error_adapter_0
(
 // Interface: in
<<<<<<< refs/remotes/upstream/main
 output reg         in_ready,
 input              in_valid,
 input [24-1: 0]     in_data,
 // Interface: out
 input               out_ready,
 output reg          out_valid,
 output reg [24-1: 0] out_data,
 output reg [2-1: 0] out_error,
=======
 input              in_valid,
 input [24-1: 0]     in_data,
 input [2-1: 0]     in_error,
 // Interface: out
 output reg          out_valid,
 output reg [24-1: 0] out_data,
>>>>>>> Revert "enlever le chain de argu"
  // Interface: clk
 input              clk,
 // Interface: reset
 input              reset_n

 /*AUTOARG*/);
<<<<<<< refs/remotes/upstream/main
   
   reg in_error = 0;
   initial in_error = 0;
=======

   reg out_error;
>>>>>>> Revert "enlever le chain de argu"

   // ---------------------------------------------------------------------
   //| Pass-through Mapping
   // ---------------------------------------------------------------------
   always_comb begin
<<<<<<< refs/remotes/upstream/main
      in_ready = out_ready;
=======
>>>>>>> Revert "enlever le chain de argu"
      out_valid = in_valid;
      out_data = in_data;

   end

   // ---------------------------------------------------------------------
<<<<<<< refs/remotes/upstream/main
   //| Error Mapping 
   // ---------------------------------------------------------------------
   always_comb begin
      out_error = 0;
      
      out_error = in_error;
                                    
   end //always @*
endmodule

=======
   //| Error Mapping
   // ---------------------------------------------------------------------
   always_comb begin
      out_error = 0;

      out_error = in_error;

   end //always @*
endmodule
>>>>>>> Revert "enlever le chain de argu"
