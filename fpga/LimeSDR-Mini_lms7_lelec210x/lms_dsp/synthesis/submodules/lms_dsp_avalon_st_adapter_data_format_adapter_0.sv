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
// $Id: //acds/rel/13.1/ip/.../avalon-st_data_format_adapter.sv.terp#1 $
// $Revision: #1 $
// $Date: 2013/09/21 $
// $Author: dmunday $


// --------------------------------------------------------------------------------
//| Avalon Streaming Data Adapter
// --------------------------------------------------------------------------------

`timescale 1ns / 100ps

// ------------------------------------------
// Generation parameters:
//   output_name:        lms_dsp_avalon_st_adapter_data_format_adapter_0
//   usePackets:         false
//   hasInEmpty:         false
//   inEmptyWidth:       0
<<<<<<< refs/remotes/upstream/main
//   hasOutEmpty:        false 
//   outEmptyWidth:      0
//   inDataWidth:        24
//   outDataWidth:       48
//   channelWidth:       0
//   inErrorWidth:       0
//   outErrorWidth:      0
//   inSymbolsPerBeat:   2
//   outSymbolsPerBeat:  4
=======
//   hasOutEmpty:        false
//   outEmptyWidth:      0
//   inDataWidth:        48
//   outDataWidth:       24
//   channelWidth:       0
//   inErrorWidth:       0
//   outErrorWidth:      0
//   inSymbolsPerBeat:   4
//   outSymbolsPerBeat:  2
>>>>>>> Revert "enlever le chain de argu"
//   maxState:           3
//   stateWidth:         2
//   maxChannel:         0
//   symbolWidth:        12
//   numMemSymbols:      3
//   symbolWidth:        12


// ------------------------------------------

<<<<<<< refs/remotes/upstream/main
 
=======

>>>>>>> Revert "enlever le chain de argu"
module lms_dsp_avalon_st_adapter_data_format_adapter_0 (
 // Interface: in
 output reg         in_ready,
 input              in_valid,
<<<<<<< refs/remotes/upstream/main
 input [24-1 : 0]    in_data,
 // Interface: out
 input                out_ready,
 output reg           out_valid,
 output reg [48-1: 0]  out_data,
=======
 input [48-1 : 0]    in_data,
 // Interface: out
 input                out_ready,
 output reg           out_valid,
 output reg [24-1: 0]  out_data,
>>>>>>> Revert "enlever le chain de argu"

  // Interface: clk
 input              clk,
 // Interface: reset
 input              reset_n

);



   // ---------------------------------------------------------------------
   //| Signal Declarations
   // ---------------------------------------------------------------------
   reg         state_read_addr;
   wire [2-1:0]   state_from_memory;
   reg  [2-1:0]   state;
   reg  [2-1:0]   new_state;
   reg  [2-1:0]   state_d1;
<<<<<<< refs/remotes/upstream/main
    
   reg            in_ready_d1;
   reg            mem_readaddr; 
=======

   reg            in_ready_d1;
   reg            mem_readaddr;
>>>>>>> Revert "enlever le chain de argu"
   reg            mem_readaddr_d1;
   reg            a_ready;
   reg            a_valid;
   reg            a_channel;
<<<<<<< refs/remotes/upstream/main
   reg [12-1:0]    a_data0; 
   reg [12-1:0]    a_data1; 
=======
   reg [12-1:0]    a_data0;
   reg [12-1:0]    a_data1;
   reg [12-1:0]    a_data2;
   reg [12-1:0]    a_data3;
>>>>>>> Revert "enlever le chain de argu"
   reg            a_startofpacket;
   reg            a_endofpacket;
   reg            a_empty;
   reg            a_error;
   reg            b_ready;
   reg            b_valid;
   reg            b_channel;
<<<<<<< refs/remotes/upstream/main
   reg  [48-1:0]   b_data;
   reg            b_startofpacket; 
   wire           b_startofpacket_wire; 
   reg            b_endofpacket; 
   reg            b_empty;   
   reg            b_error; 
=======
   reg  [24-1:0]   b_data;
   reg            b_startofpacket;
   wire           b_startofpacket_wire;
   reg            b_endofpacket;
   reg            b_empty;
   reg            b_error;
>>>>>>> Revert "enlever le chain de argu"
   reg            mem_write0;
   reg  [12-1:0]   mem_writedata0;
   wire [12-1:0]   mem_readdata0;
   wire           mem_waitrequest0;
   reg  [12-1:0]   mem0[0:0];
   reg            mem_write1;
   reg  [12-1:0]   mem_writedata1;
   wire [12-1:0]   mem_readdata1;
   wire           mem_waitrequest1;
   reg  [12-1:0]   mem1[0:0];
   reg            mem_write2;
   reg  [12-1:0]   mem_writedata2;
   wire [12-1:0]   mem_readdata2;
   wire           mem_waitrequest2;
   reg  [12-1:0]   mem2[0:0];
   reg            sop_mem_writeenable;
   reg            sop_mem_writedata;
<<<<<<< refs/remotes/upstream/main
   wire           mem_waitrequest_sop; 

   wire           state_waitrequest;
   reg            state_waitrequest_d1; 
=======
   wire           mem_waitrequest_sop;

   wire           state_waitrequest;
   reg            state_waitrequest_d1;
>>>>>>> Revert "enlever le chain de argu"

   reg            in_channel = 0;
   reg            out_channel;

   reg in_startofpacket = 0;
   reg in_endofpacket   = 0;
   reg out_startofpacket;
   reg out_endofpacket;

<<<<<<< refs/remotes/upstream/main
   reg  [2-1:0] in_empty = 0;
   reg  [4-1:0] out_empty;

   reg in_error = 0;
   reg out_error; 

   wire           error_from_mem;
   reg            error_mem_writedata;
   reg          error_mem_writeenable;

   reg  [2-1:0]   state_register;
   reg            sop_register; 
=======
   reg  [4-1:0] in_empty = 0;
   reg  [2-1:0] out_empty;

   reg in_error = 0;
   reg out_error;


   reg  [2-1:0]   state_register;
   reg            sop_register;
>>>>>>> Revert "enlever le chain de argu"
   reg            error_register;
   reg  [12-1:0]   data0_register;
   reg  [12-1:0]   data1_register;
   reg  [12-1:0]   data2_register;

   // ---------------------------------------------------------------------
   //| Input Register Stage
   // ---------------------------------------------------------------------
   always @(posedge clk or negedge reset_n) begin
      if (!reset_n) begin
         a_valid   <= 0;
         a_channel <= 0;
         a_data0   <= 0;
         a_data1   <= 0;
<<<<<<< refs/remotes/upstream/main
         a_startofpacket <= 0;
         a_endofpacket   <= 0;
         a_empty <= 0; 
=======
         a_data2   <= 0;
         a_data3   <= 0;
         a_startofpacket <= 0;
         a_endofpacket   <= 0;
         a_empty <= 0;
>>>>>>> Revert "enlever le chain de argu"
         a_error <= 0;
      end else begin
         if (in_ready) begin
            a_valid   <= in_valid;
            a_channel <= in_channel;
            a_error   <= in_error;
<<<<<<< refs/remotes/upstream/main
            a_data0 <= in_data[23:12];
            a_data1 <= in_data[11:0];
            a_startofpacket <= in_startofpacket;
            a_endofpacket   <= in_endofpacket;
            a_empty         <= 0; 
            if (in_endofpacket)
               a_empty <= in_empty;
         end
      end 
   end

   always @* begin 
      state_read_addr = in_channel;
   end
   
=======
            a_data0 <= in_data[47:36];
            a_data1 <= in_data[35:24];
            a_data2 <= in_data[23:12];
            a_data3 <= in_data[11:0];
            a_startofpacket <= in_startofpacket;
            a_endofpacket   <= in_endofpacket;
            a_empty         <= 0;
            if (in_endofpacket)
               a_empty <= in_empty;
         end
      end
   end

   always @* begin
      state_read_addr = a_channel;
      if (in_ready)
         state_read_addr = in_channel;
   end

>>>>>>> Revert "enlever le chain de argu"

   // ---------------------------------------------------------------------
   //| State & Memory Keepers
   // ---------------------------------------------------------------------
   always @(posedge clk or negedge reset_n) begin
      if (!reset_n) begin
         in_ready_d1          <= 0;
         state_d1             <= 0;
         mem_readaddr_d1      <= 0;
         state_waitrequest_d1 <= 0;
      end else begin
         in_ready_d1          <= in_ready;
         state_d1             <= state;
         mem_readaddr_d1      <= mem_readaddr;
         state_waitrequest_d1 <= state_waitrequest;
      end
   end
<<<<<<< refs/remotes/upstream/main
   
=======

>>>>>>> Revert "enlever le chain de argu"
   always @(posedge clk or negedge reset_n) begin
      if (!reset_n) begin
         state_register <= 0;
         sop_register   <= 0;
         data0_register <= 0;
         data1_register <= 0;
         data2_register <= 0;
<<<<<<< refs/remotes/upstream/main
         error_register <= 0;
=======
>>>>>>> Revert "enlever le chain de argu"
      end else begin
         state_register <= new_state;
         if (sop_mem_writeenable)
            sop_register   <= sop_mem_writedata;
<<<<<<< refs/remotes/upstream/main
         if (a_valid)
            error_register <= error_mem_writedata;
=======
>>>>>>> Revert "enlever le chain de argu"
         if (mem_write0)
            data0_register <= mem_writedata0;
         if (mem_write1)
            data1_register <= mem_writedata1;
         if (mem_write2)
            data2_register <= mem_writedata2;
         end
      end
<<<<<<< refs/remotes/upstream/main
   
=======

>>>>>>> Revert "enlever le chain de argu"
      assign state_from_memory = state_register;
      assign b_startofpacket_wire = sop_register;
      assign mem_readdata0 = data0_register;
      assign mem_readdata1 = data1_register;
      assign mem_readdata2 = data2_register;
<<<<<<< refs/remotes/upstream/main
      assign error_from_mem = error_register;
   
=======

>>>>>>> Revert "enlever le chain de argu"
   // ---------------------------------------------------------------------
   //| State Machine
   // ---------------------------------------------------------------------
   always @* begin

<<<<<<< refs/remotes/upstream/main
      
=======

>>>>>>> Revert "enlever le chain de argu"
   b_ready = (out_ready || ~out_valid);

   a_ready   = 0;
   b_data    = 0;
   b_valid   = 0;
   b_channel = a_channel;
   b_error   = a_error;
<<<<<<< refs/remotes/upstream/main
      
   state = state_from_memory;
   if (~in_ready_d1)
      state = state_d1;
         
   error_mem_writedata = error_from_mem | a_error;
   if (state == 0)
      error_mem_writedata = a_error;
   b_error = error_mem_writedata;
      
=======

   state = state_from_memory;

>>>>>>> Revert "enlever le chain de argu"
   new_state           = state;
   mem_write0          = 0;
   mem_writedata0      = a_data0;
   mem_write1          = 0;
   mem_writedata1      = a_data0;
   mem_write2          = 0;
   mem_writedata2      = a_data0;
   sop_mem_writeenable = 0;

   b_endofpacket = a_endofpacket;
<<<<<<< refs/remotes/upstream/main
      
   b_startofpacket = 0;
      
   b_empty = 0;
       
   case (state) 
            0 : begin
            mem_writedata0 = a_data0;
            mem_writedata1 = a_data1;
            a_ready = 1;
            if (a_valid) begin
               new_state = state+1'b1;
               mem_write0 = 1;
               mem_write1 = 1;
            end
         end
         1 : begin
            b_data[47:36] = mem_readdata0;
            b_data[35:24] = mem_readdata1;
            b_data[23:12] = a_data0;
            b_data[11:0] = a_data1;
            if (out_ready || ~out_valid) begin
               a_ready = 1;
               if (a_valid) 
               begin
                  new_state = state+1'b1;
                  b_valid = 1;
               end
            end
         end
         2 : begin
            mem_writedata0 = a_data0;
            mem_writedata1 = a_data1;
            a_ready = 1;
            if (a_valid) begin
               new_state = state+1'b1;
               mem_write0 = 1;
               mem_write1 = 1;
            end
         end
         3 : begin
            b_data[47:36] = mem_readdata0;
            b_data[35:24] = mem_readdata1;
            b_data[23:12] = a_data0;
            b_data[11:0] = a_data1;
            if (out_ready || ~out_valid) begin
               a_ready = 1;
               if (a_valid) 
               begin
                  new_state = 0;
                  b_valid = 1;
               end
            end
         end
=======

   b_startofpacket = 0;

   b_empty = 0;

   case (state)
            0 : begin
            b_data[23:12] = a_data0;
            b_data[11:0] = a_data1;
            b_startofpacket = a_startofpacket;
            if (out_ready || ~out_valid) begin
               if (a_valid) begin
                  b_valid = 1;
                  new_state = state+1'b1;
                     if (a_endofpacket && (a_empty >= 2) ) begin
                        new_state = 0;
                        b_empty = a_empty - 2;
                        b_endofpacket = 1;
                        a_ready = 1;
                     end
                  end
               end
            end
         1 : begin
            b_data[23:12] = a_data2;
            b_data[11:0] = a_data3;
            b_startofpacket = 0;
            if (out_ready || ~out_valid) begin
            a_ready = 1;
               if (a_valid) begin
                  b_valid = 1;
                  new_state = state+1'b1;
                     if (a_endofpacket && (a_empty >= 0) ) begin
                        new_state = 0;
                        b_empty = a_empty - 0;
                        b_endofpacket = 1;
                        a_ready = 1;
                     end
                  end
               end
            end
         2 : begin
            b_data[23:12] = a_data0;
            b_data[11:0] = a_data1;
            b_startofpacket = 0;
            if (out_ready || ~out_valid) begin
               if (a_valid) begin
                  b_valid = 1;
                  new_state = state+1'b1;
                     if (a_endofpacket && (a_empty >= 2) ) begin
                        new_state = 0;
                        b_empty = a_empty - 2;
                        b_endofpacket = 1;
                        a_ready = 1;
                     end
                  end
               end
            end
         3 : begin
            b_data[23:12] = a_data2;
            b_data[11:0] = a_data3;
            b_startofpacket = 0;
            if (out_ready || ~out_valid) begin
            a_ready = 1;
               if (a_valid) begin
                  b_valid = 1;
                  new_state = 0;
                     if (a_endofpacket && (a_empty >= 0) ) begin
                        new_state = 0;
                        b_empty = a_empty - 0;
                        b_endofpacket = 1;
                        a_ready = 1;
                     end
                  end
               end
            end
>>>>>>> Revert "enlever le chain de argu"

   endcase

      in_ready = (a_ready || ~a_valid);

<<<<<<< refs/remotes/upstream/main
      mem_readaddr = in_channel; 
      if (~in_ready)
         mem_readaddr = mem_readaddr_d1;

      
=======
      mem_readaddr = in_channel;
      if (~in_ready)
         mem_readaddr = mem_readaddr_d1;


>>>>>>> Revert "enlever le chain de argu"
      sop_mem_writedata = 0;
      if (a_valid)
         sop_mem_writedata = a_startofpacket;
      if (b_ready && b_valid && b_startofpacket)
         sop_mem_writeenable = 1;

   end


   // ---------------------------------------------------------------------
   //| Output Register Stage
   // ---------------------------------------------------------------------
   always @(posedge clk or negedge reset_n) begin
      if (!reset_n) begin
         out_valid         <= 0;
         out_data          <= 0;
         out_channel       <= 0;
         out_startofpacket <= 0;
         out_endofpacket   <= 0;
         out_empty         <= 0;
         out_error         <= 0;
      end else begin
         if (out_ready || ~out_valid) begin
            out_valid         <= b_valid;
            out_data          <= b_data;
<<<<<<< refs/remotes/upstream/main
            out_channel       <= b_channel; 
=======
            out_channel       <= b_channel;
>>>>>>> Revert "enlever le chain de argu"
            out_startofpacket <= b_startofpacket;
            out_endofpacket   <= b_endofpacket;
            out_empty         <= b_empty;
            out_error         <= b_error;
         end
<<<<<<< refs/remotes/upstream/main
      end 
   end
   



endmodule

   

=======
      end
   end




endmodule
>>>>>>> Revert "enlever le chain de argu"
