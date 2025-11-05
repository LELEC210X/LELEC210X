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


// $Id: //acds/main/ip/sopc/components/verification/altera_tristate_conduit_bfm/altera_tristate_conduit_bfm.sv.terp#7 $
// $Revision: #7 $
// $Date: 2010/08/05 $
// $Author: klong $
//-----------------------------------------------------------------------------
// =head1 NAME
// altera_conduit_bfm
// =head1 SYNOPSIS
// Bus Functional Model (BFM) for a Standard Conduit BFM
//-----------------------------------------------------------------------------
// =head1 DESCRIPTION
// This is a Bus Functional Model (BFM) for a Standard Conduit Master.
// This BFM sampled the input/bidirection port value or driving user's value to 
// output ports when user call the API.  
// This BFM's HDL is been generated through terp file in Qsys/SOPC Builder.
// Generation parameters:
// output_name:                                       altera_conduit_bfm
// role:width:direction:                              cfg_clear_rs:1:output,cfg_enable_fir:1:output,cfg_enable_ppd:1:output,cfg_pass_sum_signal:1:output,cfg_passthrough_len:16:output,cfg_red_sum_signal:1:output,cfg_threshold:8:output,debug_count:32:input,debug_long_sum:32:input,debug_short_sum:32:input
// 1
//-----------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module altera_conduit_bfm
(
   clk,
   reset,
   reset_n,
   sig_cfg_clear_rs,
   sig_cfg_enable_fir,
   sig_cfg_enable_ppd,
   sig_cfg_pass_sum_signal,
   sig_cfg_passthrough_len,
   sig_cfg_red_sum_signal,
   sig_cfg_threshold,
   sig_debug_count,
   sig_debug_long_sum,
   sig_debug_short_sum
);

   //--------------------------------------------------------------------------
   // =head1 PINS 
   // =head2 User defined interface
   //--------------------------------------------------------------------------
   input clk;
   input reset;
   input reset_n;
   output sig_cfg_clear_rs;
   output sig_cfg_enable_fir;
   output sig_cfg_enable_ppd;
   output sig_cfg_pass_sum_signal;
   output [15 : 0] sig_cfg_passthrough_len;
   output sig_cfg_red_sum_signal;
   output [7 : 0] sig_cfg_threshold;
   input [31 : 0] sig_debug_count;
   input [31 : 0] sig_debug_long_sum;
   input [31 : 0] sig_debug_short_sum;

   // synthesis translate_off
   import verbosity_pkg::*;
   
   typedef logic ROLE_cfg_clear_rs_t;
   typedef logic ROLE_cfg_enable_fir_t;
   typedef logic ROLE_cfg_enable_ppd_t;
   typedef logic ROLE_cfg_pass_sum_signal_t;
   typedef logic [15 : 0] ROLE_cfg_passthrough_len_t;
   typedef logic ROLE_cfg_red_sum_signal_t;
   typedef logic [7 : 0] ROLE_cfg_threshold_t;
   typedef logic [31 : 0] ROLE_debug_count_t;
   typedef logic [31 : 0] ROLE_debug_long_sum_t;
   typedef logic [31 : 0] ROLE_debug_short_sum_t;

   reg sig_cfg_clear_rs_temp;
   reg sig_cfg_clear_rs_out;
   reg sig_cfg_enable_fir_temp;
   reg sig_cfg_enable_fir_out;
   reg sig_cfg_enable_ppd_temp;
   reg sig_cfg_enable_ppd_out;
   reg sig_cfg_pass_sum_signal_temp;
   reg sig_cfg_pass_sum_signal_out;
   reg [15 : 0] sig_cfg_passthrough_len_temp;
   reg [15 : 0] sig_cfg_passthrough_len_out;
   reg sig_cfg_red_sum_signal_temp;
   reg sig_cfg_red_sum_signal_out;
   reg [7 : 0] sig_cfg_threshold_temp;
   reg [7 : 0] sig_cfg_threshold_out;
   logic [31 : 0] sig_debug_count_in;
   logic [31 : 0] sig_debug_count_local;
   logic [31 : 0] sig_debug_long_sum_in;
   logic [31 : 0] sig_debug_long_sum_local;
   logic [31 : 0] sig_debug_short_sum_in;
   logic [31 : 0] sig_debug_short_sum_local;

   //--------------------------------------------------------------------------
   // =head1 Public Methods API
   // =pod
   // This section describes the public methods in the application programming
   // interface (API). The application program interface provides methods for 
   // a testbench which instantiates, controls and queries state in this BFM 
   // component. Test programs must only use these public access methods and 
   // events to communicate with this BFM component. The API and module pins
   // are the only interfaces of this component that are guaranteed to be
   // stable. The API will be maintained for the life of the product. 
   // While we cannot prevent a test program from directly accessing internal
   // tasks, functions, or data private to the BFM, there is no guarantee that
   // these will be present in the future. In fact, it is best for the user
   // to assume that the underlying implementation of this component can 
   // and will change.
   // =cut
   //--------------------------------------------------------------------------
   
   event signal_reset_asserted;
   event signal_input_debug_count_change;
   event signal_input_debug_long_sum_change;
   event signal_input_debug_short_sum_change;
   
   function automatic string get_version();  // public
      // Return BFM version string. For example, version 9.1 sp1 is "9.1sp1" 
      string ret_version = "18.1";
      return ret_version;
   endfunction

   // -------------------------------------------------------
   // cfg_clear_rs
   // -------------------------------------------------------

   function automatic void set_cfg_clear_rs (
      ROLE_cfg_clear_rs_t new_value
   );
      // Drive the new value to cfg_clear_rs.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_clear_rs_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // cfg_enable_fir
   // -------------------------------------------------------

   function automatic void set_cfg_enable_fir (
      ROLE_cfg_enable_fir_t new_value
   );
      // Drive the new value to cfg_enable_fir.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_enable_fir_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // cfg_enable_ppd
   // -------------------------------------------------------

   function automatic void set_cfg_enable_ppd (
      ROLE_cfg_enable_ppd_t new_value
   );
      // Drive the new value to cfg_enable_ppd.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_enable_ppd_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // cfg_pass_sum_signal
   // -------------------------------------------------------

   function automatic void set_cfg_pass_sum_signal (
      ROLE_cfg_pass_sum_signal_t new_value
   );
      // Drive the new value to cfg_pass_sum_signal.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_pass_sum_signal_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // cfg_passthrough_len
   // -------------------------------------------------------

   function automatic void set_cfg_passthrough_len (
      ROLE_cfg_passthrough_len_t new_value
   );
      // Drive the new value to cfg_passthrough_len.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_passthrough_len_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // cfg_red_sum_signal
   // -------------------------------------------------------

   function automatic void set_cfg_red_sum_signal (
      ROLE_cfg_red_sum_signal_t new_value
   );
      // Drive the new value to cfg_red_sum_signal.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_red_sum_signal_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // cfg_threshold
   // -------------------------------------------------------

   function automatic void set_cfg_threshold (
      ROLE_cfg_threshold_t new_value
   );
      // Drive the new value to cfg_threshold.
      
      $sformat(message, "%m: method called arg0 %0d", new_value); 
      print(VERBOSITY_DEBUG, message);
      
      sig_cfg_threshold_temp = new_value;
   endfunction

   // -------------------------------------------------------
   // debug_count
   // -------------------------------------------------------
   function automatic ROLE_debug_count_t get_debug_count();
   
      // Gets the debug_count input value.
      $sformat(message, "%m: called get_debug_count");
      print(VERBOSITY_DEBUG, message);
      return sig_debug_count_in;
      
   endfunction

   // -------------------------------------------------------
   // debug_long_sum
   // -------------------------------------------------------
   function automatic ROLE_debug_long_sum_t get_debug_long_sum();
   
      // Gets the debug_long_sum input value.
      $sformat(message, "%m: called get_debug_long_sum");
      print(VERBOSITY_DEBUG, message);
      return sig_debug_long_sum_in;
      
   endfunction

   // -------------------------------------------------------
   // debug_short_sum
   // -------------------------------------------------------
   function automatic ROLE_debug_short_sum_t get_debug_short_sum();
   
      // Gets the debug_short_sum input value.
      $sformat(message, "%m: called get_debug_short_sum");
      print(VERBOSITY_DEBUG, message);
      return sig_debug_short_sum_in;
      
   endfunction

   always @(posedge clk) begin
      sig_cfg_clear_rs_out <= sig_cfg_clear_rs_temp;
      sig_cfg_enable_fir_out <= sig_cfg_enable_fir_temp;
      sig_cfg_enable_ppd_out <= sig_cfg_enable_ppd_temp;
      sig_cfg_pass_sum_signal_out <= sig_cfg_pass_sum_signal_temp;
      sig_cfg_passthrough_len_out <= sig_cfg_passthrough_len_temp;
      sig_cfg_red_sum_signal_out <= sig_cfg_red_sum_signal_temp;
      sig_cfg_threshold_out <= sig_cfg_threshold_temp;
      sig_debug_count_in <= sig_debug_count;
      sig_debug_long_sum_in <= sig_debug_long_sum;
      sig_debug_short_sum_in <= sig_debug_short_sum;
   end
   
   assign sig_cfg_clear_rs = sig_cfg_clear_rs_out;
   assign sig_cfg_enable_fir = sig_cfg_enable_fir_out;
   assign sig_cfg_enable_ppd = sig_cfg_enable_ppd_out;
   assign sig_cfg_pass_sum_signal = sig_cfg_pass_sum_signal_out;
   assign sig_cfg_passthrough_len = sig_cfg_passthrough_len_out;
   assign sig_cfg_red_sum_signal = sig_cfg_red_sum_signal_out;
   assign sig_cfg_threshold = sig_cfg_threshold_out;

   always @(posedge reset or negedge reset_n) begin
      -> signal_reset_asserted;
   end

   always @(sig_debug_count_in) begin
      if (sig_debug_count_local != sig_debug_count_in)
         -> signal_input_debug_count_change;
      sig_debug_count_local = sig_debug_count_in;
   end
   
   always @(sig_debug_long_sum_in) begin
      if (sig_debug_long_sum_local != sig_debug_long_sum_in)
         -> signal_input_debug_long_sum_change;
      sig_debug_long_sum_local = sig_debug_long_sum_in;
   end
   
   always @(sig_debug_short_sum_in) begin
      if (sig_debug_short_sum_local != sig_debug_short_sum_in)
         -> signal_input_debug_short_sum_change;
      sig_debug_short_sum_local = sig_debug_short_sum_in;
   end
   


// synthesis translate_on

endmodule

