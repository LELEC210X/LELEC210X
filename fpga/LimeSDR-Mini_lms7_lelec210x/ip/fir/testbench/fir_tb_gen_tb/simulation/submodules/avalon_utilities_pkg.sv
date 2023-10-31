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


// $Id: //acds/rel/18.1std/ip/sopc/components/verification/lib/avalon_utilities_pkg.sv#1 $
// $Revision: #1 $
// $Date: 2018/07/18 $
//-----------------------------------------------------------------------------
// =head1 NAME
// avalon_utilities_pkg
// =head1 SYNOPSIS
// Package for shared types and functions
//-----------------------------------------------------------------------------
// =head1 COPYRIGHT
// Copyright (c) 2008 Altera Corporation. All Rights Reserved.
// The information contained in this file is the property of Altera
<<<<<<< refs/remotes/upstream/main
// Corporation. Except as specifically authorized in writing by Altera 
// Corporation, the holder of this file shall keep all information 
// contained herein confidential and shall protect same in whole or in part 
// from disclosure and dissemination to all third parties. Use of this 
=======
// Corporation. Except as specifically authorized in writing by Altera
// Corporation, the holder of this file shall keep all information
// contained herein confidential and shall protect same in whole or in part
// from disclosure and dissemination to all third parties. Use of this
>>>>>>> Revert "enlever le chain de argu"
// program confirms your agreement with the terms of this license.
//-----------------------------------------------------------------------------
// =head1 DESCRIPTION
// This package contains shared types and functions.
// =cut
`timescale 1ns / 1ns

`ifndef _AVALON_UTILITIES_PKG_
`define _AVALON_UTILITIES_PKG_

package avalon_utilities_pkg;

   function automatic int clog2(
      bit [31:0] Depth
   );
<<<<<<< refs/remotes/upstream/main
      int	 i= Depth; 
=======
      int	 i= Depth;
>>>>>>> Revert "enlever le chain de argu"
      for(clog2 = 0; i > 0; clog2 = clog2 + 1)
        i = i >> 1;

      return clog2;
<<<<<<< refs/remotes/upstream/main
   endfunction 
=======
   endfunction
>>>>>>> Revert "enlever le chain de argu"

   function automatic int max(
      bit [31:0] one,
      bit [31:0] two
<<<<<<< refs/remotes/upstream/main
   );     
=======
   );
>>>>>>> Revert "enlever le chain de argu"
      if(one > two)
	return one;
      else
	return two;
<<<<<<< refs/remotes/upstream/main
   endfunction 
=======
   endfunction
>>>>>>> Revert "enlever le chain de argu"

   function automatic int lindex(
      bit [31:0] width
   );
<<<<<<< refs/remotes/upstream/main
      // returns the left index for a vector having a declared width 
      // when width is 0, then the left index is set to 0 rather than -1
      lindex = (width > 0) ? (width-1) : 0;
   endfunction
   
   typedef enum int {
      LOW      = 0,
      HIGH     = 1,
      RANDOM   = 2,  
      UNKNOWN  = 3
   } IdleOutputValue_t;
   
endpackage

`endif
   
=======
      // returns the left index for a vector having a declared width
      // when width is 0, then the left index is set to 0 rather than -1
      lindex = (width > 0) ? (width-1) : 0;
   endfunction

   typedef enum int {
      LOW      = 0,
      HIGH     = 1,
      RANDOM   = 2,
      UNKNOWN  = 3
   } IdleOutputValue_t;

endpackage

`endif
>>>>>>> Revert "enlever le chain de argu"
