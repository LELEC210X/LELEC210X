-- ------------------------------------------------------------------------- 
-- High Level Design Compiler for Intel(R) FPGAs Version 18.1 (Release Build #625)
-- Quartus Prime development tool and MATLAB/Simulink Interface
-- 
-- Legal Notice: Copyright 2018 Intel Corporation.  All rights reserved.
-- Your use of  Intel Corporation's design tools,  logic functions and other
-- software and  tools, and its AMPP partner logic functions, and any output
-- files any  of the foregoing (including  device programming  or simulation
-- files), and  any associated  documentation  or information  are expressly
-- subject  to the terms and  conditions of the  Intel FPGA Software License
-- Agreement, Intel MegaCore Function License Agreement, or other applicable
-- license agreement,  including,  without limitation,  that your use is for
-- the  sole  purpose of  programming  logic devices  manufactured by  Intel
-- and  sold by Intel  or its authorized  distributors. Please refer  to the
-- applicable agreement for further details.
-- ---------------------------------------------------------------------------

-- VHDL created from fir_tb_gen_fir_compiler_ii_0_rtl_core
-- VHDL created on Wed Nov 01 09:14:37 2023


library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.MATH_REAL.all;
use std.TextIO.all;
use work.dspba_library_package.all;

LIBRARY altera_mf;
USE altera_mf.altera_mf_components.all;
LIBRARY lpm;
USE lpm.lpm_components.all;

entity fir_tb_gen_fir_compiler_ii_0_rtl_core is
    port (
        xIn_v : in std_logic_vector(0 downto 0);  -- sfix1
        xIn_c : in std_logic_vector(7 downto 0);  -- sfix8
        xIn_0 : in std_logic_vector(11 downto 0);  -- sfix12
        xIn_1 : in std_logic_vector(11 downto 0);  -- sfix12
        xOut_v : out std_logic_vector(0 downto 0);  -- ufix1
        xOut_c : out std_logic_vector(7 downto 0);  -- ufix8
        xOut_0 : out std_logic_vector(24 downto 0);  -- sfix25
        xOut_1 : out std_logic_vector(24 downto 0);  -- sfix25
        clk : in std_logic;
        areset : in std_logic
    );
end fir_tb_gen_fir_compiler_ii_0_rtl_core;

architecture normal of fir_tb_gen_fir_compiler_ii_0_rtl_core is

    attribute altera_attribute : string;
    attribute altera_attribute of normal : architecture is "-name AUTO_SHIFT_REGISTER_RECOGNITION OFF; -name PHYSICAL_SYNTHESIS_REGISTER_DUPLICATION ON; -name MESSAGE_DISABLE 10036; -name MESSAGE_DISABLE 10037; -name MESSAGE_DISABLE 14130; -name MESSAGE_DISABLE 14320; -name MESSAGE_DISABLE 15400; -name MESSAGE_DISABLE 14130; -name MESSAGE_DISABLE 10036; -name MESSAGE_DISABLE 12020; -name MESSAGE_DISABLE 12030; -name MESSAGE_DISABLE 12010; -name MESSAGE_DISABLE 12110; -name MESSAGE_DISABLE 14320; -name MESSAGE_DISABLE 13410; -name MESSAGE_DISABLE 113007";
    
    signal GND_q : STD_LOGIC_VECTOR (0 downto 0);
    signal VCC_q : STD_LOGIC_VECTOR (0 downto 0);
    signal d_u0_m0_wo0_memread_q_11_q : STD_LOGIC_VECTOR (0 downto 0);
    signal d_u0_m0_wo0_memread_q_13_q : STD_LOGIC_VECTOR (0 downto 0);
    signal d_u0_m0_wo0_compute_q_11_q : STD_LOGIC_VECTOR (0 downto 0);
    signal d_u0_m0_wo0_compute_q_13_q : STD_LOGIC_VECTOR (0 downto 0);
    signal d_u0_m0_wo0_compute_q_16_q : STD_LOGIC_VECTOR (0 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr1_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr2_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr3_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr4_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr5_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr5_q_13_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr6_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr6_q_14_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr7_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr8_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr8_q_12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr9_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr9_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr10_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr10_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr12_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr12_q_12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr13_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr13_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr14_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr14_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr15_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr15_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr16_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr16_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr17_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr17_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr18_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr18_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr19_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr20_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr20_q_12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr21_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr22_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr22_q_13_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr23_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr24_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u0_m0_wo0_wi0_r0_delayr24_q_14_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_wi0_r0_delayr25_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u0_m0_wo0_mtree_add0_4_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_4_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_4_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_4_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_6_a : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_6_b : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_6_o : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_6_q : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_7_a : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add0_7_b : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add0_7_o : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add0_7_q : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add0_8_a : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_8_b : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_8_o : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_8_q : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_add0_10_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_10_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_10_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_10_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add0_12_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_add0_12_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_add0_12_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_add0_12_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_add1_1_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add1_1_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add1_1_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add1_1_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_add1_2_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_2_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_2_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_2_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_3_a : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add1_3_b : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add1_3_o : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add1_3_q : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add1_4_a : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add1_4_b : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add1_4_o : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add1_4_q : STD_LOGIC_VECTOR (20 downto 0);
    signal u0_m0_wo0_mtree_add1_5_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_5_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_5_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add1_5_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_add2_1_a : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add2_1_b : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add2_1_o : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add2_1_q : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add2_2_a : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add2_2_b : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add2_2_o : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add2_2_q : STD_LOGIC_VECTOR (21 downto 0);
    signal u0_m0_wo0_mtree_add3_0_a : STD_LOGIC_VECTOR (23 downto 0);
    signal u0_m0_wo0_mtree_add3_0_b : STD_LOGIC_VECTOR (23 downto 0);
    signal u0_m0_wo0_mtree_add3_0_o : STD_LOGIC_VECTOR (23 downto 0);
    signal u0_m0_wo0_mtree_add3_0_q : STD_LOGIC_VECTOR (23 downto 0);
    signal u0_m0_wo0_mtree_add3_1_a : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add3_1_b : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add3_1_o : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add3_1_q : STD_LOGIC_VECTOR (22 downto 0);
    signal u0_m0_wo0_mtree_add4_0_a : STD_LOGIC_VECTOR (24 downto 0);
    signal u0_m0_wo0_mtree_add4_0_b : STD_LOGIC_VECTOR (24 downto 0);
    signal u0_m0_wo0_mtree_add4_0_o : STD_LOGIC_VECTOR (24 downto 0);
    signal u0_m0_wo0_mtree_add4_0_q : STD_LOGIC_VECTOR (24 downto 0);
    signal u0_m0_wo0_oseq_gated_reg_q : STD_LOGIC_VECTOR (0 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr1_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr2_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr3_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr4_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr5_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr5_q_13_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr6_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr6_q_14_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr7_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr8_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr8_q_12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr9_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr9_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr10_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr10_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr12_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr12_q_12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr13_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr13_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr14_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr14_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr15_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr15_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr16_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr16_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr17_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr17_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr18_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr18_q_11_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr19_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr20_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr20_q_12_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr21_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr22_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr22_q_13_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr23_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr24_q : STD_LOGIC_VECTOR (11 downto 0);
    signal d_u1_m0_wo0_wi0_r0_delayr24_q_14_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_wi0_r0_delayr25_q : STD_LOGIC_VECTOR (11 downto 0);
    signal u1_m0_wo0_mtree_add0_4_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_4_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_4_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_4_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_6_a : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_6_b : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_6_o : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_6_q : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_7_a : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add0_7_b : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add0_7_o : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add0_7_q : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add0_8_a : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_8_b : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_8_o : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_8_q : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_add0_10_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_10_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_10_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_10_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add0_12_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_add0_12_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_add0_12_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_add0_12_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_add1_1_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add1_1_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add1_1_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add1_1_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_add1_2_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_2_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_2_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_2_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_3_a : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add1_3_b : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add1_3_o : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add1_3_q : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add1_4_a : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add1_4_b : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add1_4_o : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add1_4_q : STD_LOGIC_VECTOR (20 downto 0);
    signal u1_m0_wo0_mtree_add1_5_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_5_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_5_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add1_5_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_add2_1_a : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add2_1_b : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add2_1_o : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add2_1_q : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add2_2_a : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add2_2_b : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add2_2_o : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add2_2_q : STD_LOGIC_VECTOR (21 downto 0);
    signal u1_m0_wo0_mtree_add3_0_a : STD_LOGIC_VECTOR (23 downto 0);
    signal u1_m0_wo0_mtree_add3_0_b : STD_LOGIC_VECTOR (23 downto 0);
    signal u1_m0_wo0_mtree_add3_0_o : STD_LOGIC_VECTOR (23 downto 0);
    signal u1_m0_wo0_mtree_add3_0_q : STD_LOGIC_VECTOR (23 downto 0);
    signal u1_m0_wo0_mtree_add3_1_a : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add3_1_b : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add3_1_o : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add3_1_q : STD_LOGIC_VECTOR (22 downto 0);
    signal u1_m0_wo0_mtree_add4_0_a : STD_LOGIC_VECTOR (24 downto 0);
    signal u1_m0_wo0_mtree_add4_0_b : STD_LOGIC_VECTOR (24 downto 0);
    signal u1_m0_wo0_mtree_add4_0_o : STD_LOGIC_VECTOR (24 downto 0);
    signal u1_m0_wo0_mtree_add4_0_q : STD_LOGIC_VECTOR (24 downto 0);
    signal u0_m0_wo0_mtree_mult1_25_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_25_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_25_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_25_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_22_sub_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_22_sub_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_22_sub_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_22_sub_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_2_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_2_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_2_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_sub_2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_3_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_3_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_3_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_add_3_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_1_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_1_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_1_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_1_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_sub_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_add_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_15_sub_1_a : STD_LOGIC_VECTOR (19 downto 0);
    signal u0_m0_wo0_mtree_mult1_15_sub_1_b : STD_LOGIC_VECTOR (19 downto 0);
    signal u0_m0_wo0_mtree_mult1_15_sub_1_o : STD_LOGIC_VECTOR (19 downto 0);
    signal u0_m0_wo0_mtree_mult1_15_sub_1_q : STD_LOGIC_VECTOR (19 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_add_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_1_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_1_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_1_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_1_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_sub_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_3_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_3_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_3_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_add_3_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_2_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_2_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_2_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_sub_2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_8_sub_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_8_sub_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_8_sub_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_8_sub_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_5_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_5_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_5_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_5_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_25_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_25_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_25_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_25_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_22_sub_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_22_sub_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_22_sub_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_22_sub_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_2_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_2_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_2_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_sub_2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_3_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_3_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_3_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_add_3_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_1_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_1_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_1_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_1_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_sub_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_add_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_15_sub_1_a : STD_LOGIC_VECTOR (19 downto 0);
    signal u1_m0_wo0_mtree_mult1_15_sub_1_b : STD_LOGIC_VECTOR (19 downto 0);
    signal u1_m0_wo0_mtree_mult1_15_sub_1_o : STD_LOGIC_VECTOR (19 downto 0);
    signal u1_m0_wo0_mtree_mult1_15_sub_1_q : STD_LOGIC_VECTOR (19 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_add_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_1_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_1_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_1_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_1_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_3_a : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_3_b : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_3_o : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_sub_3_q : STD_LOGIC_VECTOR (17 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_3_a : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_3_b : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_3_o : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_add_3_q : STD_LOGIC_VECTOR (15 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_2_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_2_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_2_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_sub_2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_add_1_a : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_add_1_b : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_add_1_o : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_add_1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_8_sub_1_a : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_8_sub_1_b : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_8_sub_1_o : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_8_sub_1_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_5_sub_0_a : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_5_sub_0_b : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_5_sub_0_o : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_5_sub_0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_22_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_22_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_shift1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_20_shift1_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_18_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_shift0_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_shift0_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_17_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_16_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_15_shift0_q : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_mult1_15_shift0_qint : STD_LOGIC_VECTOR (18 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_14_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_shift0_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_shift0_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_13_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_12_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_shift1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_10_shift1_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u0_m0_wo0_mtree_mult1_8_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_8_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_22_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_22_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_shift1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_20_shift1_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_18_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_shift0_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_shift0_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_17_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_16_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_15_shift0_q : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_mult1_15_shift0_qint : STD_LOGIC_VECTOR (18 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_14_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_shift0_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_shift0_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_shift2_q : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_13_shift2_qint : STD_LOGIC_VECTOR (16 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_12_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_shift1_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_10_shift1_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_shift0_q : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_shift0_qint : STD_LOGIC_VECTOR (12 downto 0);
    signal u1_m0_wo0_mtree_mult1_8_shift0_q : STD_LOGIC_VECTOR (13 downto 0);
    signal u1_m0_wo0_mtree_mult1_8_shift0_qint : STD_LOGIC_VECTOR (13 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_21_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u0_m0_wo0_mtree_mult1_9_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_21_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_shift2_q : STD_LOGIC_VECTOR (14 downto 0);
    signal u1_m0_wo0_mtree_mult1_9_shift2_qint : STD_LOGIC_VECTOR (14 downto 0);

begin


    -- VCC(CONSTANT,1)@0
    VCC_q <= "1";

    -- u1_m0_wo0_wi0_r0_delayr1(DELAY,159)@10
    u1_m0_wo0_wi0_r0_delayr1 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => xIn_1, xout => u1_m0_wo0_wi0_r0_delayr1_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr2(DELAY,160)@10
    u1_m0_wo0_wi0_r0_delayr2 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr1_q, xout => u1_m0_wo0_wi0_r0_delayr2_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr3(DELAY,161)@10
    u1_m0_wo0_wi0_r0_delayr3 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr2_q, xout => u1_m0_wo0_wi0_r0_delayr3_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr4(DELAY,162)@10
    u1_m0_wo0_wi0_r0_delayr4 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr3_q, xout => u1_m0_wo0_wi0_r0_delayr4_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr5(DELAY,163)@10
    u1_m0_wo0_wi0_r0_delayr5 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr4_q, xout => u1_m0_wo0_wi0_r0_delayr5_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr5_q_13(DELAY,443)@10 + 3
    d_u1_m0_wo0_wi0_r0_delayr5_q_13 : dspba_delay
    GENERIC MAP ( width => 12, depth => 3, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr5_q, xout => d_u1_m0_wo0_wi0_r0_delayr5_q_13_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_25_sub_0(SUB,378)@13 + 1
    u1_m0_wo0_mtree_mult1_25_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u1_m0_wo0_mtree_mult1_25_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => d_u1_m0_wo0_wi0_r0_delayr5_q_13_q(11)) & d_u1_m0_wo0_wi0_r0_delayr5_q_13_q));
    u1_m0_wo0_mtree_mult1_25_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_25_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_25_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_25_sub_0_a) - SIGNED(u1_m0_wo0_mtree_mult1_25_sub_0_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_25_sub_0_q <= u1_m0_wo0_mtree_mult1_25_sub_0_o(12 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr6(DELAY,164)@10
    u1_m0_wo0_wi0_r0_delayr6 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr5_q, xout => u1_m0_wo0_wi0_r0_delayr6_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr6_q_14(DELAY,444)@10 + 4
    d_u1_m0_wo0_wi0_r0_delayr6_q_14 : dspba_delay
    GENERIC MAP ( width => 12, depth => 4, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr6_q, xout => d_u1_m0_wo0_wi0_r0_delayr6_q_14_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_add0_12(ADD,266)@14 + 1
    u1_m0_wo0_mtree_add0_12_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => d_u1_m0_wo0_wi0_r0_delayr6_q_14_q(11)) & d_u1_m0_wo0_wi0_r0_delayr6_q_14_q));
    u1_m0_wo0_mtree_add0_12_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u1_m0_wo0_mtree_mult1_25_sub_0_q(12)) & u1_m0_wo0_mtree_mult1_25_sub_0_q));
    u1_m0_wo0_mtree_add0_12_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add0_12_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add0_12_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add0_12_a) + SIGNED(u1_m0_wo0_mtree_add0_12_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add0_12_q <= u1_m0_wo0_mtree_add0_12_o(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_22_shift0(BITSHIFT,379)@12
    u1_m0_wo0_mtree_mult1_22_shift0_qint <= d_u1_m0_wo0_wi0_r0_delayr8_q_12_q & "00";
    u1_m0_wo0_mtree_mult1_22_shift0_q <= u1_m0_wo0_mtree_mult1_22_shift0_qint(13 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr7(DELAY,165)@10
    u1_m0_wo0_wi0_r0_delayr7 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr6_q, xout => u1_m0_wo0_wi0_r0_delayr7_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr8(DELAY,166)@10
    u1_m0_wo0_wi0_r0_delayr8 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr7_q, xout => u1_m0_wo0_wi0_r0_delayr8_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr8_q_12(DELAY,445)@10 + 2
    d_u1_m0_wo0_wi0_r0_delayr8_q_12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr8_q, xout => d_u1_m0_wo0_wi0_r0_delayr8_q_12_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_22_sub_1(SUB,380)@12 + 1
    u1_m0_wo0_mtree_mult1_22_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => d_u1_m0_wo0_wi0_r0_delayr8_q_12_q(11)) & d_u1_m0_wo0_wi0_r0_delayr8_q_12_q));
    u1_m0_wo0_mtree_mult1_22_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u1_m0_wo0_mtree_mult1_22_shift0_q(13)) & u1_m0_wo0_mtree_mult1_22_shift0_q));
    u1_m0_wo0_mtree_mult1_22_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_22_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_22_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_22_sub_1_a) - SIGNED(u1_m0_wo0_mtree_mult1_22_sub_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_22_sub_1_q <= u1_m0_wo0_mtree_mult1_22_sub_1_o(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_21_shift0(BITSHIFT,381)@11
    u1_m0_wo0_mtree_mult1_21_shift0_qint <= d_u1_m0_wo0_wi0_r0_delayr9_q_11_q & "0";
    u1_m0_wo0_mtree_mult1_21_shift0_q <= u1_m0_wo0_mtree_mult1_21_shift0_qint(12 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr9(DELAY,167)@10
    u1_m0_wo0_wi0_r0_delayr9 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr8_q, xout => u1_m0_wo0_wi0_r0_delayr9_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr9_q_11(DELAY,446)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr9_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr9_q, xout => d_u1_m0_wo0_wi0_r0_delayr9_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_21_add_1(ADD,382)@11 + 1
    u1_m0_wo0_mtree_mult1_21_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => d_u1_m0_wo0_wi0_r0_delayr9_q_11_q(11)) & d_u1_m0_wo0_wi0_r0_delayr9_q_11_q));
    u1_m0_wo0_mtree_mult1_21_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u1_m0_wo0_mtree_mult1_21_shift0_q(12)) & u1_m0_wo0_mtree_mult1_21_shift0_q));
    u1_m0_wo0_mtree_mult1_21_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_21_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_21_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_21_add_1_a) + SIGNED(u1_m0_wo0_mtree_mult1_21_add_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_21_add_1_q <= u1_m0_wo0_mtree_mult1_21_add_1_o(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_21_shift2(BITSHIFT,383)@12
    u1_m0_wo0_mtree_mult1_21_shift2_qint <= u1_m0_wo0_mtree_mult1_21_add_1_q & "0";
    u1_m0_wo0_mtree_mult1_21_shift2_q <= u1_m0_wo0_mtree_mult1_21_shift2_qint(14 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr10(DELAY,168)@10
    u1_m0_wo0_wi0_r0_delayr10 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr9_q, xout => u1_m0_wo0_wi0_r0_delayr10_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr10_q_11(DELAY,447)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr10_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr10_q, xout => d_u1_m0_wo0_wi0_r0_delayr10_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_20_shift1(BITSHIFT,385)@11
    u1_m0_wo0_mtree_mult1_20_shift1_qint <= d_u1_m0_wo0_wi0_r0_delayr10_q_11_q & "00";
    u1_m0_wo0_mtree_mult1_20_shift1_q <= u1_m0_wo0_mtree_mult1_20_shift1_qint(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_20_sub_0(SUB,384)@10 + 1
    u1_m0_wo0_mtree_mult1_20_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u1_m0_wo0_mtree_mult1_20_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => u1_m0_wo0_wi0_r0_delayr10_q(11)) & u1_m0_wo0_wi0_r0_delayr10_q));
    u1_m0_wo0_mtree_mult1_20_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_20_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_20_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_20_sub_0_a) - SIGNED(u1_m0_wo0_mtree_mult1_20_sub_0_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_20_sub_0_q <= u1_m0_wo0_mtree_mult1_20_sub_0_o(12 downto 0);

    -- u1_m0_wo0_mtree_mult1_20_sub_2(SUB,386)@11 + 1
    u1_m0_wo0_mtree_mult1_20_sub_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 13 => u1_m0_wo0_mtree_mult1_20_sub_0_q(12)) & u1_m0_wo0_mtree_mult1_20_sub_0_q));
    u1_m0_wo0_mtree_mult1_20_sub_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u1_m0_wo0_mtree_mult1_20_shift1_q(13)) & u1_m0_wo0_mtree_mult1_20_shift1_q));
    u1_m0_wo0_mtree_mult1_20_sub_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_20_sub_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_20_sub_2_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_20_sub_2_a) - SIGNED(u1_m0_wo0_mtree_mult1_20_sub_2_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_20_sub_2_q <= u1_m0_wo0_mtree_mult1_20_sub_2_o(14 downto 0);

    -- u1_m0_wo0_mtree_add0_10(ADD,264)@12 + 1
    u1_m0_wo0_mtree_add0_10_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_20_sub_2_q(14)) & u1_m0_wo0_mtree_mult1_20_sub_2_q));
    u1_m0_wo0_mtree_add0_10_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_21_shift2_q(14)) & u1_m0_wo0_mtree_mult1_21_shift2_q));
    u1_m0_wo0_mtree_add0_10_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add0_10_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add0_10_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add0_10_a) + SIGNED(u1_m0_wo0_mtree_add0_10_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add0_10_q <= u1_m0_wo0_mtree_add0_10_o(15 downto 0);

    -- u1_m0_wo0_mtree_add1_5(ADD,274)@13 + 1
    u1_m0_wo0_mtree_add1_5_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u1_m0_wo0_mtree_add0_10_q(15)) & u1_m0_wo0_mtree_add0_10_q));
    u1_m0_wo0_mtree_add1_5_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u1_m0_wo0_mtree_mult1_22_sub_1_q(14)) & u1_m0_wo0_mtree_mult1_22_sub_1_q));
    u1_m0_wo0_mtree_add1_5_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add1_5_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add1_5_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add1_5_a) + SIGNED(u1_m0_wo0_mtree_add1_5_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add1_5_q <= u1_m0_wo0_mtree_add1_5_o(17 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr11(DELAY,169)@10
    u1_m0_wo0_wi0_r0_delayr11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr10_q, xout => u1_m0_wo0_wi0_r0_delayr11_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr12(DELAY,170)@10
    u1_m0_wo0_wi0_r0_delayr12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr11_q, xout => u1_m0_wo0_wi0_r0_delayr12_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr12_q_11(DELAY,448)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr12_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr12_q, xout => d_u1_m0_wo0_wi0_r0_delayr12_q_11_q, clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr12_q_12(DELAY,449)@11 + 1
    d_u1_m0_wo0_wi0_r0_delayr12_q_12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u1_m0_wo0_wi0_r0_delayr12_q_11_q, xout => d_u1_m0_wo0_wi0_r0_delayr12_q_12_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_18_shift2(BITSHIFT,389)@12
    u1_m0_wo0_mtree_mult1_18_shift2_qint <= d_u1_m0_wo0_wi0_r0_delayr12_q_12_q & "000";
    u1_m0_wo0_mtree_mult1_18_shift2_q <= u1_m0_wo0_mtree_mult1_18_shift2_qint(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_18_shift0(BITSHIFT,387)@11
    u1_m0_wo0_mtree_mult1_18_shift0_qint <= d_u1_m0_wo0_wi0_r0_delayr12_q_11_q & "0";
    u1_m0_wo0_mtree_mult1_18_shift0_q <= u1_m0_wo0_mtree_mult1_18_shift0_qint(12 downto 0);

    -- u1_m0_wo0_mtree_mult1_18_add_1(ADD,388)@11 + 1
    u1_m0_wo0_mtree_mult1_18_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => d_u1_m0_wo0_wi0_r0_delayr12_q_11_q(11)) & d_u1_m0_wo0_wi0_r0_delayr12_q_11_q));
    u1_m0_wo0_mtree_mult1_18_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u1_m0_wo0_mtree_mult1_18_shift0_q(12)) & u1_m0_wo0_mtree_mult1_18_shift0_q));
    u1_m0_wo0_mtree_mult1_18_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_18_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_18_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_18_add_1_a) + SIGNED(u1_m0_wo0_mtree_mult1_18_add_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_18_add_1_q <= u1_m0_wo0_mtree_mult1_18_add_1_o(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_18_add_3(ADD,390)@12 + 1
    u1_m0_wo0_mtree_mult1_18_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 14 => u1_m0_wo0_mtree_mult1_18_add_1_q(13)) & u1_m0_wo0_mtree_mult1_18_add_1_q));
    u1_m0_wo0_mtree_mult1_18_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_18_shift2_q(14)) & u1_m0_wo0_mtree_mult1_18_shift2_q));
    u1_m0_wo0_mtree_mult1_18_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_18_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_18_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_18_add_3_a) + SIGNED(u1_m0_wo0_mtree_mult1_18_add_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_18_add_3_q <= u1_m0_wo0_mtree_mult1_18_add_3_o(15 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr13(DELAY,171)@10
    u1_m0_wo0_wi0_r0_delayr13 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr12_q, xout => u1_m0_wo0_wi0_r0_delayr13_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr13_q_11(DELAY,450)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr13_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr13_q, xout => d_u1_m0_wo0_wi0_r0_delayr13_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_17_shift2(BITSHIFT,393)@11
    u1_m0_wo0_mtree_mult1_17_shift2_qint <= d_u1_m0_wo0_wi0_r0_delayr13_q_11_q & "00000";
    u1_m0_wo0_mtree_mult1_17_shift2_q <= u1_m0_wo0_mtree_mult1_17_shift2_qint(16 downto 0);

    -- u1_m0_wo0_mtree_mult1_17_shift0(BITSHIFT,391)@10
    u1_m0_wo0_mtree_mult1_17_shift0_qint <= u1_m0_wo0_wi0_r0_delayr13_q & "000";
    u1_m0_wo0_mtree_mult1_17_shift0_q <= u1_m0_wo0_mtree_mult1_17_shift0_qint(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_17_sub_1(SUB,392)@10 + 1
    u1_m0_wo0_mtree_mult1_17_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_17_shift0_q(14)) & u1_m0_wo0_mtree_mult1_17_shift0_q));
    u1_m0_wo0_mtree_mult1_17_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 12 => u1_m0_wo0_wi0_r0_delayr13_q(11)) & u1_m0_wo0_wi0_r0_delayr13_q));
    u1_m0_wo0_mtree_mult1_17_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_17_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_17_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_17_sub_1_a) - SIGNED(u1_m0_wo0_mtree_mult1_17_sub_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_17_sub_1_q <= u1_m0_wo0_mtree_mult1_17_sub_1_o(15 downto 0);

    -- u1_m0_wo0_mtree_mult1_17_sub_3(SUB,394)@11 + 1
    u1_m0_wo0_mtree_mult1_17_sub_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u1_m0_wo0_mtree_mult1_17_sub_1_q(15)) & u1_m0_wo0_mtree_mult1_17_sub_1_q));
    u1_m0_wo0_mtree_mult1_17_sub_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u1_m0_wo0_mtree_mult1_17_shift2_q(16)) & u1_m0_wo0_mtree_mult1_17_shift2_q));
    u1_m0_wo0_mtree_mult1_17_sub_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_17_sub_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_17_sub_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_17_sub_3_a) - SIGNED(u1_m0_wo0_mtree_mult1_17_sub_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_17_sub_3_q <= u1_m0_wo0_mtree_mult1_17_sub_3_o(17 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr14(DELAY,172)@10
    u1_m0_wo0_wi0_r0_delayr14 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr13_q, xout => u1_m0_wo0_wi0_r0_delayr14_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr14_q_11(DELAY,451)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr14_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr14_q, xout => d_u1_m0_wo0_wi0_r0_delayr14_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_16_shift2(BITSHIFT,397)@11
    u1_m0_wo0_mtree_mult1_16_shift2_qint <= d_u1_m0_wo0_wi0_r0_delayr14_q_11_q & "00000";
    u1_m0_wo0_mtree_mult1_16_shift2_q <= u1_m0_wo0_mtree_mult1_16_shift2_qint(16 downto 0);

    -- u1_m0_wo0_mtree_mult1_16_shift0(BITSHIFT,395)@10
    u1_m0_wo0_mtree_mult1_16_shift0_qint <= u1_m0_wo0_wi0_r0_delayr14_q & "00";
    u1_m0_wo0_mtree_mult1_16_shift0_q <= u1_m0_wo0_mtree_mult1_16_shift0_qint(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_16_add_1(ADD,396)@10 + 1
    u1_m0_wo0_mtree_mult1_16_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => u1_m0_wo0_wi0_r0_delayr14_q(11)) & u1_m0_wo0_wi0_r0_delayr14_q));
    u1_m0_wo0_mtree_mult1_16_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u1_m0_wo0_mtree_mult1_16_shift0_q(13)) & u1_m0_wo0_mtree_mult1_16_shift0_q));
    u1_m0_wo0_mtree_mult1_16_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_16_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_16_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_16_add_1_a) + SIGNED(u1_m0_wo0_mtree_mult1_16_add_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_16_add_1_q <= u1_m0_wo0_mtree_mult1_16_add_1_o(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_16_add_3(ADD,398)@11 + 1
    u1_m0_wo0_mtree_mult1_16_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u1_m0_wo0_mtree_mult1_16_add_1_q(14)) & u1_m0_wo0_mtree_mult1_16_add_1_q));
    u1_m0_wo0_mtree_mult1_16_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u1_m0_wo0_mtree_mult1_16_shift2_q(16)) & u1_m0_wo0_mtree_mult1_16_shift2_q));
    u1_m0_wo0_mtree_mult1_16_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_16_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_16_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_16_add_3_a) + SIGNED(u1_m0_wo0_mtree_mult1_16_add_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_16_add_3_q <= u1_m0_wo0_mtree_mult1_16_add_3_o(17 downto 0);

    -- u1_m0_wo0_mtree_add0_8(ADD,262)@12 + 1
    u1_m0_wo0_mtree_add0_8_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 18 => u1_m0_wo0_mtree_mult1_16_add_3_q(17)) & u1_m0_wo0_mtree_mult1_16_add_3_q));
    u1_m0_wo0_mtree_add0_8_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 18 => u1_m0_wo0_mtree_mult1_17_sub_3_q(17)) & u1_m0_wo0_mtree_mult1_17_sub_3_q));
    u1_m0_wo0_mtree_add0_8_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add0_8_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add0_8_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add0_8_a) + SIGNED(u1_m0_wo0_mtree_add0_8_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add0_8_q <= u1_m0_wo0_mtree_add0_8_o(18 downto 0);

    -- u1_m0_wo0_mtree_add1_4(ADD,273)@13 + 1
    u1_m0_wo0_mtree_add1_4_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 19 => u1_m0_wo0_mtree_add0_8_q(18)) & u1_m0_wo0_mtree_add0_8_q));
    u1_m0_wo0_mtree_add1_4_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 16 => u1_m0_wo0_mtree_mult1_18_add_3_q(15)) & u1_m0_wo0_mtree_mult1_18_add_3_q));
    u1_m0_wo0_mtree_add1_4_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add1_4_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add1_4_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add1_4_a) + SIGNED(u1_m0_wo0_mtree_add1_4_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add1_4_q <= u1_m0_wo0_mtree_add1_4_o(20 downto 0);

    -- u1_m0_wo0_mtree_add2_2(ADD,279)@14 + 1
    u1_m0_wo0_mtree_add2_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 21 => u1_m0_wo0_mtree_add1_4_q(20)) & u1_m0_wo0_mtree_add1_4_q));
    u1_m0_wo0_mtree_add2_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 18 => u1_m0_wo0_mtree_add1_5_q(17)) & u1_m0_wo0_mtree_add1_5_q));
    u1_m0_wo0_mtree_add2_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add2_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add2_2_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add2_2_a) + SIGNED(u1_m0_wo0_mtree_add2_2_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add2_2_q <= u1_m0_wo0_mtree_add2_2_o(21 downto 0);

    -- u1_m0_wo0_mtree_add3_1(ADD,282)@15 + 1
    u1_m0_wo0_mtree_add3_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 22 => u1_m0_wo0_mtree_add2_2_q(21)) & u1_m0_wo0_mtree_add2_2_q));
    u1_m0_wo0_mtree_add3_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 14 => u1_m0_wo0_mtree_add0_12_q(13)) & u1_m0_wo0_mtree_add0_12_q));
    u1_m0_wo0_mtree_add3_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add3_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add3_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add3_1_a) + SIGNED(u1_m0_wo0_mtree_add3_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add3_1_q <= u1_m0_wo0_mtree_add3_1_o(22 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr15(DELAY,173)@10
    u1_m0_wo0_wi0_r0_delayr15 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr14_q, xout => u1_m0_wo0_wi0_r0_delayr15_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr15_q_11(DELAY,452)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr15_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr15_q, xout => d_u1_m0_wo0_wi0_r0_delayr15_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_15_shift0(BITSHIFT,399)@11
    u1_m0_wo0_mtree_mult1_15_shift0_qint <= d_u1_m0_wo0_wi0_r0_delayr15_q_11_q & "0000000";
    u1_m0_wo0_mtree_mult1_15_shift0_q <= u1_m0_wo0_mtree_mult1_15_shift0_qint(18 downto 0);

    -- u1_m0_wo0_mtree_mult1_15_sub_1(SUB,400)@11 + 1
    u1_m0_wo0_mtree_mult1_15_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((19 downto 19 => u1_m0_wo0_mtree_mult1_15_shift0_q(18)) & u1_m0_wo0_mtree_mult1_15_shift0_q));
    u1_m0_wo0_mtree_mult1_15_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((19 downto 12 => d_u1_m0_wo0_wi0_r0_delayr15_q_11_q(11)) & d_u1_m0_wo0_wi0_r0_delayr15_q_11_q));
    u1_m0_wo0_mtree_mult1_15_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_15_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_15_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_15_sub_1_a) - SIGNED(u1_m0_wo0_mtree_mult1_15_sub_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_15_sub_1_q <= u1_m0_wo0_mtree_mult1_15_sub_1_o(19 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr16(DELAY,174)@10
    u1_m0_wo0_wi0_r0_delayr16 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr15_q, xout => u1_m0_wo0_wi0_r0_delayr16_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr16_q_11(DELAY,453)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr16_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr16_q, xout => d_u1_m0_wo0_wi0_r0_delayr16_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_14_shift2(BITSHIFT,403)@11
    u1_m0_wo0_mtree_mult1_14_shift2_qint <= d_u1_m0_wo0_wi0_r0_delayr16_q_11_q & "00000";
    u1_m0_wo0_mtree_mult1_14_shift2_q <= u1_m0_wo0_mtree_mult1_14_shift2_qint(16 downto 0);

    -- u1_m0_wo0_mtree_mult1_14_shift0(BITSHIFT,401)@10
    u1_m0_wo0_mtree_mult1_14_shift0_qint <= u1_m0_wo0_wi0_r0_delayr16_q & "00";
    u1_m0_wo0_mtree_mult1_14_shift0_q <= u1_m0_wo0_mtree_mult1_14_shift0_qint(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_14_add_1(ADD,402)@10 + 1
    u1_m0_wo0_mtree_mult1_14_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => u1_m0_wo0_wi0_r0_delayr16_q(11)) & u1_m0_wo0_wi0_r0_delayr16_q));
    u1_m0_wo0_mtree_mult1_14_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u1_m0_wo0_mtree_mult1_14_shift0_q(13)) & u1_m0_wo0_mtree_mult1_14_shift0_q));
    u1_m0_wo0_mtree_mult1_14_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_14_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_14_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_14_add_1_a) + SIGNED(u1_m0_wo0_mtree_mult1_14_add_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_14_add_1_q <= u1_m0_wo0_mtree_mult1_14_add_1_o(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_14_add_3(ADD,404)@11 + 1
    u1_m0_wo0_mtree_mult1_14_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u1_m0_wo0_mtree_mult1_14_add_1_q(14)) & u1_m0_wo0_mtree_mult1_14_add_1_q));
    u1_m0_wo0_mtree_mult1_14_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u1_m0_wo0_mtree_mult1_14_shift2_q(16)) & u1_m0_wo0_mtree_mult1_14_shift2_q));
    u1_m0_wo0_mtree_mult1_14_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_14_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_14_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_14_add_3_a) + SIGNED(u1_m0_wo0_mtree_mult1_14_add_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_14_add_3_q <= u1_m0_wo0_mtree_mult1_14_add_3_o(17 downto 0);

    -- u1_m0_wo0_mtree_add0_7(ADD,261)@12 + 1
    u1_m0_wo0_mtree_add0_7_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 18 => u1_m0_wo0_mtree_mult1_14_add_3_q(17)) & u1_m0_wo0_mtree_mult1_14_add_3_q));
    u1_m0_wo0_mtree_add0_7_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 20 => u1_m0_wo0_mtree_mult1_15_sub_1_q(19)) & u1_m0_wo0_mtree_mult1_15_sub_1_q));
    u1_m0_wo0_mtree_add0_7_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add0_7_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add0_7_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add0_7_a) + SIGNED(u1_m0_wo0_mtree_add0_7_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add0_7_q <= u1_m0_wo0_mtree_add0_7_o(20 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr17(DELAY,175)@10
    u1_m0_wo0_wi0_r0_delayr17 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr16_q, xout => u1_m0_wo0_wi0_r0_delayr17_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr17_q_11(DELAY,454)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr17_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr17_q, xout => d_u1_m0_wo0_wi0_r0_delayr17_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_13_shift2(BITSHIFT,407)@11
    u1_m0_wo0_mtree_mult1_13_shift2_qint <= d_u1_m0_wo0_wi0_r0_delayr17_q_11_q & "00000";
    u1_m0_wo0_mtree_mult1_13_shift2_q <= u1_m0_wo0_mtree_mult1_13_shift2_qint(16 downto 0);

    -- u1_m0_wo0_mtree_mult1_13_shift0(BITSHIFT,405)@10
    u1_m0_wo0_mtree_mult1_13_shift0_qint <= u1_m0_wo0_wi0_r0_delayr17_q & "000";
    u1_m0_wo0_mtree_mult1_13_shift0_q <= u1_m0_wo0_mtree_mult1_13_shift0_qint(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_13_sub_1(SUB,406)@10 + 1
    u1_m0_wo0_mtree_mult1_13_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_13_shift0_q(14)) & u1_m0_wo0_mtree_mult1_13_shift0_q));
    u1_m0_wo0_mtree_mult1_13_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 12 => u1_m0_wo0_wi0_r0_delayr17_q(11)) & u1_m0_wo0_wi0_r0_delayr17_q));
    u1_m0_wo0_mtree_mult1_13_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_13_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_13_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_13_sub_1_a) - SIGNED(u1_m0_wo0_mtree_mult1_13_sub_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_13_sub_1_q <= u1_m0_wo0_mtree_mult1_13_sub_1_o(15 downto 0);

    -- u1_m0_wo0_mtree_mult1_13_sub_3(SUB,408)@11 + 1
    u1_m0_wo0_mtree_mult1_13_sub_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u1_m0_wo0_mtree_mult1_13_sub_1_q(15)) & u1_m0_wo0_mtree_mult1_13_sub_1_q));
    u1_m0_wo0_mtree_mult1_13_sub_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u1_m0_wo0_mtree_mult1_13_shift2_q(16)) & u1_m0_wo0_mtree_mult1_13_shift2_q));
    u1_m0_wo0_mtree_mult1_13_sub_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_13_sub_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_13_sub_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_13_sub_3_a) - SIGNED(u1_m0_wo0_mtree_mult1_13_sub_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_13_sub_3_q <= u1_m0_wo0_mtree_mult1_13_sub_3_o(17 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr18(DELAY,176)@10
    u1_m0_wo0_wi0_r0_delayr18 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr17_q, xout => u1_m0_wo0_wi0_r0_delayr18_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr18_q_11(DELAY,455)@10 + 1
    d_u1_m0_wo0_wi0_r0_delayr18_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr18_q, xout => d_u1_m0_wo0_wi0_r0_delayr18_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_12_shift2(BITSHIFT,411)@11
    u1_m0_wo0_mtree_mult1_12_shift2_qint <= d_u1_m0_wo0_wi0_r0_delayr18_q_11_q & "000";
    u1_m0_wo0_mtree_mult1_12_shift2_q <= u1_m0_wo0_mtree_mult1_12_shift2_qint(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_12_shift0(BITSHIFT,409)@10
    u1_m0_wo0_mtree_mult1_12_shift0_qint <= u1_m0_wo0_wi0_r0_delayr18_q & "0";
    u1_m0_wo0_mtree_mult1_12_shift0_q <= u1_m0_wo0_mtree_mult1_12_shift0_qint(12 downto 0);

    -- u1_m0_wo0_mtree_mult1_12_add_1(ADD,410)@10 + 1
    u1_m0_wo0_mtree_mult1_12_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => u1_m0_wo0_wi0_r0_delayr18_q(11)) & u1_m0_wo0_wi0_r0_delayr18_q));
    u1_m0_wo0_mtree_mult1_12_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u1_m0_wo0_mtree_mult1_12_shift0_q(12)) & u1_m0_wo0_mtree_mult1_12_shift0_q));
    u1_m0_wo0_mtree_mult1_12_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_12_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_12_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_12_add_1_a) + SIGNED(u1_m0_wo0_mtree_mult1_12_add_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_12_add_1_q <= u1_m0_wo0_mtree_mult1_12_add_1_o(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_12_add_3(ADD,412)@11 + 1
    u1_m0_wo0_mtree_mult1_12_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 14 => u1_m0_wo0_mtree_mult1_12_add_1_q(13)) & u1_m0_wo0_mtree_mult1_12_add_1_q));
    u1_m0_wo0_mtree_mult1_12_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_12_shift2_q(14)) & u1_m0_wo0_mtree_mult1_12_shift2_q));
    u1_m0_wo0_mtree_mult1_12_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_12_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_12_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_12_add_3_a) + SIGNED(u1_m0_wo0_mtree_mult1_12_add_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_12_add_3_q <= u1_m0_wo0_mtree_mult1_12_add_3_o(15 downto 0);

    -- u1_m0_wo0_mtree_add0_6(ADD,260)@12 + 1
    u1_m0_wo0_mtree_add0_6_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 16 => u1_m0_wo0_mtree_mult1_12_add_3_q(15)) & u1_m0_wo0_mtree_mult1_12_add_3_q));
    u1_m0_wo0_mtree_add0_6_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 18 => u1_m0_wo0_mtree_mult1_13_sub_3_q(17)) & u1_m0_wo0_mtree_mult1_13_sub_3_q));
    u1_m0_wo0_mtree_add0_6_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add0_6_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add0_6_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add0_6_a) + SIGNED(u1_m0_wo0_mtree_add0_6_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add0_6_q <= u1_m0_wo0_mtree_add0_6_o(18 downto 0);

    -- u1_m0_wo0_mtree_add1_3(ADD,272)@13 + 1
    u1_m0_wo0_mtree_add1_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 19 => u1_m0_wo0_mtree_add0_6_q(18)) & u1_m0_wo0_mtree_add0_6_q));
    u1_m0_wo0_mtree_add1_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 21 => u1_m0_wo0_mtree_add0_7_q(20)) & u1_m0_wo0_mtree_add0_7_q));
    u1_m0_wo0_mtree_add1_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add1_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add1_3_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add1_3_a) + SIGNED(u1_m0_wo0_mtree_add1_3_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add1_3_q <= u1_m0_wo0_mtree_add1_3_o(21 downto 0);

    -- d_u0_m0_wo0_memread_q_11(DELAY,422)@10 + 1
    d_u0_m0_wo0_memread_q_11 : dspba_delay
    GENERIC MAP ( width => 1, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => xIn_v, xout => d_u0_m0_wo0_memread_q_11_q, clk => clk, aclr => areset );

    -- d_u0_m0_wo0_compute_q_11(DELAY,424)@10 + 1
    d_u0_m0_wo0_compute_q_11 : dspba_delay
    GENERIC MAP ( width => 1, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => xIn_v, xout => d_u0_m0_wo0_compute_q_11_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr19(DELAY,177)@11
    u1_m0_wo0_wi0_r0_delayr19 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u1_m0_wo0_wi0_r0_delayr18_q_11_q, xout => u1_m0_wo0_wi0_r0_delayr19_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr20(DELAY,178)@11
    u1_m0_wo0_wi0_r0_delayr20 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr19_q, xout => u1_m0_wo0_wi0_r0_delayr20_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr20_q_12(DELAY,456)@11 + 1
    d_u1_m0_wo0_wi0_r0_delayr20_q_12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr20_q, xout => d_u1_m0_wo0_wi0_r0_delayr20_q_12_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_10_shift1(BITSHIFT,414)@12
    u1_m0_wo0_mtree_mult1_10_shift1_qint <= d_u1_m0_wo0_wi0_r0_delayr20_q_12_q & "00";
    u1_m0_wo0_mtree_mult1_10_shift1_q <= u1_m0_wo0_mtree_mult1_10_shift1_qint(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_10_sub_0(SUB,413)@11 + 1
    u1_m0_wo0_mtree_mult1_10_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u1_m0_wo0_mtree_mult1_10_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => u1_m0_wo0_wi0_r0_delayr20_q(11)) & u1_m0_wo0_wi0_r0_delayr20_q));
    u1_m0_wo0_mtree_mult1_10_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_10_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_10_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_10_sub_0_a) - SIGNED(u1_m0_wo0_mtree_mult1_10_sub_0_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_10_sub_0_q <= u1_m0_wo0_mtree_mult1_10_sub_0_o(12 downto 0);

    -- u1_m0_wo0_mtree_mult1_10_sub_2(SUB,415)@12 + 1
    u1_m0_wo0_mtree_mult1_10_sub_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 13 => u1_m0_wo0_mtree_mult1_10_sub_0_q(12)) & u1_m0_wo0_mtree_mult1_10_sub_0_q));
    u1_m0_wo0_mtree_mult1_10_sub_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u1_m0_wo0_mtree_mult1_10_shift1_q(13)) & u1_m0_wo0_mtree_mult1_10_shift1_q));
    u1_m0_wo0_mtree_mult1_10_sub_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_10_sub_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_10_sub_2_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_10_sub_2_a) - SIGNED(u1_m0_wo0_mtree_mult1_10_sub_2_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_10_sub_2_q <= u1_m0_wo0_mtree_mult1_10_sub_2_o(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_9_shift0(BITSHIFT,416)@11
    u1_m0_wo0_mtree_mult1_9_shift0_qint <= u1_m0_wo0_wi0_r0_delayr21_q & "0";
    u1_m0_wo0_mtree_mult1_9_shift0_q <= u1_m0_wo0_mtree_mult1_9_shift0_qint(12 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr21(DELAY,179)@11
    u1_m0_wo0_wi0_r0_delayr21 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr20_q, xout => u1_m0_wo0_wi0_r0_delayr21_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_9_add_1(ADD,417)@11 + 1
    u1_m0_wo0_mtree_mult1_9_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => u1_m0_wo0_wi0_r0_delayr21_q(11)) & u1_m0_wo0_wi0_r0_delayr21_q));
    u1_m0_wo0_mtree_mult1_9_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u1_m0_wo0_mtree_mult1_9_shift0_q(12)) & u1_m0_wo0_mtree_mult1_9_shift0_q));
    u1_m0_wo0_mtree_mult1_9_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_9_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_9_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_9_add_1_a) + SIGNED(u1_m0_wo0_mtree_mult1_9_add_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_9_add_1_q <= u1_m0_wo0_mtree_mult1_9_add_1_o(13 downto 0);

    -- u1_m0_wo0_mtree_mult1_9_shift2(BITSHIFT,418)@12
    u1_m0_wo0_mtree_mult1_9_shift2_qint <= u1_m0_wo0_mtree_mult1_9_add_1_q & "0";
    u1_m0_wo0_mtree_mult1_9_shift2_q <= u1_m0_wo0_mtree_mult1_9_shift2_qint(14 downto 0);

    -- u1_m0_wo0_mtree_mult1_8_shift0(BITSHIFT,419)@11
    u1_m0_wo0_mtree_mult1_8_shift0_qint <= u1_m0_wo0_wi0_r0_delayr22_q & "00";
    u1_m0_wo0_mtree_mult1_8_shift0_q <= u1_m0_wo0_mtree_mult1_8_shift0_qint(13 downto 0);

    -- u1_m0_wo0_wi0_r0_delayr22(DELAY,180)@11
    u1_m0_wo0_wi0_r0_delayr22 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr21_q, xout => u1_m0_wo0_wi0_r0_delayr22_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_8_sub_1(SUB,420)@11 + 1
    u1_m0_wo0_mtree_mult1_8_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => u1_m0_wo0_wi0_r0_delayr22_q(11)) & u1_m0_wo0_wi0_r0_delayr22_q));
    u1_m0_wo0_mtree_mult1_8_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u1_m0_wo0_mtree_mult1_8_shift0_q(13)) & u1_m0_wo0_mtree_mult1_8_shift0_q));
    u1_m0_wo0_mtree_mult1_8_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_8_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_8_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_8_sub_1_a) - SIGNED(u1_m0_wo0_mtree_mult1_8_sub_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_8_sub_1_q <= u1_m0_wo0_mtree_mult1_8_sub_1_o(14 downto 0);

    -- u1_m0_wo0_mtree_add0_4(ADD,258)@12 + 1
    u1_m0_wo0_mtree_add0_4_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_8_sub_1_q(14)) & u1_m0_wo0_mtree_mult1_8_sub_1_q));
    u1_m0_wo0_mtree_add0_4_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u1_m0_wo0_mtree_mult1_9_shift2_q(14)) & u1_m0_wo0_mtree_mult1_9_shift2_q));
    u1_m0_wo0_mtree_add0_4_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add0_4_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add0_4_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add0_4_a) + SIGNED(u1_m0_wo0_mtree_add0_4_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add0_4_q <= u1_m0_wo0_mtree_add0_4_o(15 downto 0);

    -- u1_m0_wo0_mtree_add1_2(ADD,271)@13 + 1
    u1_m0_wo0_mtree_add1_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u1_m0_wo0_mtree_add0_4_q(15)) & u1_m0_wo0_mtree_add0_4_q));
    u1_m0_wo0_mtree_add1_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u1_m0_wo0_mtree_mult1_10_sub_2_q(14)) & u1_m0_wo0_mtree_mult1_10_sub_2_q));
    u1_m0_wo0_mtree_add1_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add1_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add1_2_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add1_2_a) + SIGNED(u1_m0_wo0_mtree_add1_2_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add1_2_q <= u1_m0_wo0_mtree_add1_2_o(17 downto 0);

    -- u1_m0_wo0_mtree_add2_1(ADD,278)@14 + 1
    u1_m0_wo0_mtree_add2_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 18 => u1_m0_wo0_mtree_add1_2_q(17)) & u1_m0_wo0_mtree_add1_2_q));
    u1_m0_wo0_mtree_add2_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 22 => u1_m0_wo0_mtree_add1_3_q(21)) & u1_m0_wo0_mtree_add1_3_q));
    u1_m0_wo0_mtree_add2_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add2_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add2_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add2_1_a) + SIGNED(u1_m0_wo0_mtree_add2_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add2_1_q <= u1_m0_wo0_mtree_add2_1_o(22 downto 0);

    -- d_u0_m0_wo0_memread_q_13(DELAY,423)@11 + 2
    d_u0_m0_wo0_memread_q_13 : dspba_delay
    GENERIC MAP ( width => 1, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u0_m0_wo0_memread_q_11_q, xout => d_u0_m0_wo0_memread_q_13_q, clk => clk, aclr => areset );

    -- d_u0_m0_wo0_compute_q_13(DELAY,425)@11 + 2
    d_u0_m0_wo0_compute_q_13 : dspba_delay
    GENERIC MAP ( width => 1, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u0_m0_wo0_compute_q_11_q, xout => d_u0_m0_wo0_compute_q_13_q, clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr22_q_13(DELAY,457)@11 + 2
    d_u1_m0_wo0_wi0_r0_delayr22_q_13 : dspba_delay
    GENERIC MAP ( width => 12, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr22_q, xout => d_u1_m0_wo0_wi0_r0_delayr22_q_13_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr23(DELAY,181)@13
    u1_m0_wo0_wi0_r0_delayr23 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u1_m0_wo0_wi0_r0_delayr22_q_13_q, xout => u1_m0_wo0_wi0_r0_delayr23_q, ena => d_u0_m0_wo0_compute_q_13_q(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr24(DELAY,182)@13
    u1_m0_wo0_wi0_r0_delayr24 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr23_q, xout => u1_m0_wo0_wi0_r0_delayr24_q, ena => d_u0_m0_wo0_compute_q_13_q(0), clk => clk, aclr => areset );

    -- d_u1_m0_wo0_wi0_r0_delayr24_q_14(DELAY,458)@13 + 1
    d_u1_m0_wo0_wi0_r0_delayr24_q_14 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr24_q, xout => d_u1_m0_wo0_wi0_r0_delayr24_q_14_q, clk => clk, aclr => areset );

    -- u1_m0_wo0_wi0_r0_delayr25(DELAY,183)@13
    u1_m0_wo0_wi0_r0_delayr25 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u1_m0_wo0_wi0_r0_delayr24_q, xout => u1_m0_wo0_wi0_r0_delayr25_q, ena => d_u0_m0_wo0_compute_q_13_q(0), clk => clk, aclr => areset );

    -- u1_m0_wo0_mtree_mult1_5_sub_0(SUB,421)@13 + 1
    u1_m0_wo0_mtree_mult1_5_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u1_m0_wo0_mtree_mult1_5_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => u1_m0_wo0_wi0_r0_delayr25_q(11)) & u1_m0_wo0_wi0_r0_delayr25_q));
    u1_m0_wo0_mtree_mult1_5_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_mult1_5_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_mult1_5_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_mult1_5_sub_0_a) - SIGNED(u1_m0_wo0_mtree_mult1_5_sub_0_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_mult1_5_sub_0_q <= u1_m0_wo0_mtree_mult1_5_sub_0_o(12 downto 0);

    -- u1_m0_wo0_mtree_add1_1(ADD,270)@14 + 1
    u1_m0_wo0_mtree_add1_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 13 => u1_m0_wo0_mtree_mult1_5_sub_0_q(12)) & u1_m0_wo0_mtree_mult1_5_sub_0_q));
    u1_m0_wo0_mtree_add1_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 12 => d_u1_m0_wo0_wi0_r0_delayr24_q_14_q(11)) & d_u1_m0_wo0_wi0_r0_delayr24_q_14_q));
    u1_m0_wo0_mtree_add1_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add1_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add1_1_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add1_1_a) + SIGNED(u1_m0_wo0_mtree_add1_1_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add1_1_q <= u1_m0_wo0_mtree_add1_1_o(15 downto 0);

    -- u1_m0_wo0_mtree_add3_0(ADD,281)@15 + 1
    u1_m0_wo0_mtree_add3_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((23 downto 16 => u1_m0_wo0_mtree_add1_1_q(15)) & u1_m0_wo0_mtree_add1_1_q));
    u1_m0_wo0_mtree_add3_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((23 downto 23 => u1_m0_wo0_mtree_add2_1_q(22)) & u1_m0_wo0_mtree_add2_1_q));
    u1_m0_wo0_mtree_add3_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add3_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add3_0_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add3_0_a) + SIGNED(u1_m0_wo0_mtree_add3_0_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add3_0_q <= u1_m0_wo0_mtree_add3_0_o(23 downto 0);

    -- u1_m0_wo0_mtree_add4_0(ADD,283)@16 + 1
    u1_m0_wo0_mtree_add4_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((24 downto 24 => u1_m0_wo0_mtree_add3_0_q(23)) & u1_m0_wo0_mtree_add3_0_q));
    u1_m0_wo0_mtree_add4_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((24 downto 23 => u1_m0_wo0_mtree_add3_1_q(22)) & u1_m0_wo0_mtree_add3_1_q));
    u1_m0_wo0_mtree_add4_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u1_m0_wo0_mtree_add4_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u1_m0_wo0_mtree_add4_0_o <= STD_LOGIC_VECTOR(SIGNED(u1_m0_wo0_mtree_add4_0_a) + SIGNED(u1_m0_wo0_mtree_add4_0_b));
        END IF;
    END PROCESS;
    u1_m0_wo0_mtree_add4_0_q <= u1_m0_wo0_mtree_add4_0_o(24 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr1(DELAY,21)@10
    u0_m0_wo0_wi0_r0_delayr1 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => xIn_0, xout => u0_m0_wo0_wi0_r0_delayr1_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr2(DELAY,22)@10
    u0_m0_wo0_wi0_r0_delayr2 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr1_q, xout => u0_m0_wo0_wi0_r0_delayr2_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr3(DELAY,23)@10
    u0_m0_wo0_wi0_r0_delayr3 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr2_q, xout => u0_m0_wo0_wi0_r0_delayr3_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr4(DELAY,24)@10
    u0_m0_wo0_wi0_r0_delayr4 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr3_q, xout => u0_m0_wo0_wi0_r0_delayr4_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr5(DELAY,25)@10
    u0_m0_wo0_wi0_r0_delayr5 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr4_q, xout => u0_m0_wo0_wi0_r0_delayr5_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr5_q_13(DELAY,427)@10 + 3
    d_u0_m0_wo0_wi0_r0_delayr5_q_13 : dspba_delay
    GENERIC MAP ( width => 12, depth => 3, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr5_q, xout => d_u0_m0_wo0_wi0_r0_delayr5_q_13_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_25_sub_0(SUB,334)@13 + 1
    u0_m0_wo0_mtree_mult1_25_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u0_m0_wo0_mtree_mult1_25_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => d_u0_m0_wo0_wi0_r0_delayr5_q_13_q(11)) & d_u0_m0_wo0_wi0_r0_delayr5_q_13_q));
    u0_m0_wo0_mtree_mult1_25_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_25_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_25_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_25_sub_0_a) - SIGNED(u0_m0_wo0_mtree_mult1_25_sub_0_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_25_sub_0_q <= u0_m0_wo0_mtree_mult1_25_sub_0_o(12 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr6(DELAY,26)@10
    u0_m0_wo0_wi0_r0_delayr6 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr5_q, xout => u0_m0_wo0_wi0_r0_delayr6_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr6_q_14(DELAY,428)@10 + 4
    d_u0_m0_wo0_wi0_r0_delayr6_q_14 : dspba_delay
    GENERIC MAP ( width => 12, depth => 4, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr6_q, xout => d_u0_m0_wo0_wi0_r0_delayr6_q_14_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_add0_12(ADD,128)@14 + 1
    u0_m0_wo0_mtree_add0_12_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => d_u0_m0_wo0_wi0_r0_delayr6_q_14_q(11)) & d_u0_m0_wo0_wi0_r0_delayr6_q_14_q));
    u0_m0_wo0_mtree_add0_12_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u0_m0_wo0_mtree_mult1_25_sub_0_q(12)) & u0_m0_wo0_mtree_mult1_25_sub_0_q));
    u0_m0_wo0_mtree_add0_12_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add0_12_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add0_12_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add0_12_a) + SIGNED(u0_m0_wo0_mtree_add0_12_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add0_12_q <= u0_m0_wo0_mtree_add0_12_o(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_22_shift0(BITSHIFT,335)@12
    u0_m0_wo0_mtree_mult1_22_shift0_qint <= d_u0_m0_wo0_wi0_r0_delayr8_q_12_q & "00";
    u0_m0_wo0_mtree_mult1_22_shift0_q <= u0_m0_wo0_mtree_mult1_22_shift0_qint(13 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr7(DELAY,27)@10
    u0_m0_wo0_wi0_r0_delayr7 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr6_q, xout => u0_m0_wo0_wi0_r0_delayr7_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr8(DELAY,28)@10
    u0_m0_wo0_wi0_r0_delayr8 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr7_q, xout => u0_m0_wo0_wi0_r0_delayr8_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr8_q_12(DELAY,429)@10 + 2
    d_u0_m0_wo0_wi0_r0_delayr8_q_12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr8_q, xout => d_u0_m0_wo0_wi0_r0_delayr8_q_12_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_22_sub_1(SUB,336)@12 + 1
    u0_m0_wo0_mtree_mult1_22_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => d_u0_m0_wo0_wi0_r0_delayr8_q_12_q(11)) & d_u0_m0_wo0_wi0_r0_delayr8_q_12_q));
    u0_m0_wo0_mtree_mult1_22_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u0_m0_wo0_mtree_mult1_22_shift0_q(13)) & u0_m0_wo0_mtree_mult1_22_shift0_q));
    u0_m0_wo0_mtree_mult1_22_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_22_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_22_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_22_sub_1_a) - SIGNED(u0_m0_wo0_mtree_mult1_22_sub_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_22_sub_1_q <= u0_m0_wo0_mtree_mult1_22_sub_1_o(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_21_shift0(BITSHIFT,337)@11
    u0_m0_wo0_mtree_mult1_21_shift0_qint <= d_u0_m0_wo0_wi0_r0_delayr9_q_11_q & "0";
    u0_m0_wo0_mtree_mult1_21_shift0_q <= u0_m0_wo0_mtree_mult1_21_shift0_qint(12 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr9(DELAY,29)@10
    u0_m0_wo0_wi0_r0_delayr9 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr8_q, xout => u0_m0_wo0_wi0_r0_delayr9_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr9_q_11(DELAY,430)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr9_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr9_q, xout => d_u0_m0_wo0_wi0_r0_delayr9_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_21_add_1(ADD,338)@11 + 1
    u0_m0_wo0_mtree_mult1_21_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => d_u0_m0_wo0_wi0_r0_delayr9_q_11_q(11)) & d_u0_m0_wo0_wi0_r0_delayr9_q_11_q));
    u0_m0_wo0_mtree_mult1_21_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u0_m0_wo0_mtree_mult1_21_shift0_q(12)) & u0_m0_wo0_mtree_mult1_21_shift0_q));
    u0_m0_wo0_mtree_mult1_21_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_21_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_21_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_21_add_1_a) + SIGNED(u0_m0_wo0_mtree_mult1_21_add_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_21_add_1_q <= u0_m0_wo0_mtree_mult1_21_add_1_o(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_21_shift2(BITSHIFT,339)@12
    u0_m0_wo0_mtree_mult1_21_shift2_qint <= u0_m0_wo0_mtree_mult1_21_add_1_q & "0";
    u0_m0_wo0_mtree_mult1_21_shift2_q <= u0_m0_wo0_mtree_mult1_21_shift2_qint(14 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr10(DELAY,30)@10
    u0_m0_wo0_wi0_r0_delayr10 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr9_q, xout => u0_m0_wo0_wi0_r0_delayr10_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr10_q_11(DELAY,431)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr10_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr10_q, xout => d_u0_m0_wo0_wi0_r0_delayr10_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_20_shift1(BITSHIFT,341)@11
    u0_m0_wo0_mtree_mult1_20_shift1_qint <= d_u0_m0_wo0_wi0_r0_delayr10_q_11_q & "00";
    u0_m0_wo0_mtree_mult1_20_shift1_q <= u0_m0_wo0_mtree_mult1_20_shift1_qint(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_20_sub_0(SUB,340)@10 + 1
    u0_m0_wo0_mtree_mult1_20_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u0_m0_wo0_mtree_mult1_20_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => u0_m0_wo0_wi0_r0_delayr10_q(11)) & u0_m0_wo0_wi0_r0_delayr10_q));
    u0_m0_wo0_mtree_mult1_20_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_20_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_20_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_20_sub_0_a) - SIGNED(u0_m0_wo0_mtree_mult1_20_sub_0_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_20_sub_0_q <= u0_m0_wo0_mtree_mult1_20_sub_0_o(12 downto 0);

    -- u0_m0_wo0_mtree_mult1_20_sub_2(SUB,342)@11 + 1
    u0_m0_wo0_mtree_mult1_20_sub_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 13 => u0_m0_wo0_mtree_mult1_20_sub_0_q(12)) & u0_m0_wo0_mtree_mult1_20_sub_0_q));
    u0_m0_wo0_mtree_mult1_20_sub_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u0_m0_wo0_mtree_mult1_20_shift1_q(13)) & u0_m0_wo0_mtree_mult1_20_shift1_q));
    u0_m0_wo0_mtree_mult1_20_sub_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_20_sub_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_20_sub_2_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_20_sub_2_a) - SIGNED(u0_m0_wo0_mtree_mult1_20_sub_2_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_20_sub_2_q <= u0_m0_wo0_mtree_mult1_20_sub_2_o(14 downto 0);

    -- u0_m0_wo0_mtree_add0_10(ADD,126)@12 + 1
    u0_m0_wo0_mtree_add0_10_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_20_sub_2_q(14)) & u0_m0_wo0_mtree_mult1_20_sub_2_q));
    u0_m0_wo0_mtree_add0_10_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_21_shift2_q(14)) & u0_m0_wo0_mtree_mult1_21_shift2_q));
    u0_m0_wo0_mtree_add0_10_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add0_10_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add0_10_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add0_10_a) + SIGNED(u0_m0_wo0_mtree_add0_10_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add0_10_q <= u0_m0_wo0_mtree_add0_10_o(15 downto 0);

    -- u0_m0_wo0_mtree_add1_5(ADD,136)@13 + 1
    u0_m0_wo0_mtree_add1_5_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u0_m0_wo0_mtree_add0_10_q(15)) & u0_m0_wo0_mtree_add0_10_q));
    u0_m0_wo0_mtree_add1_5_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u0_m0_wo0_mtree_mult1_22_sub_1_q(14)) & u0_m0_wo0_mtree_mult1_22_sub_1_q));
    u0_m0_wo0_mtree_add1_5_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add1_5_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add1_5_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add1_5_a) + SIGNED(u0_m0_wo0_mtree_add1_5_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add1_5_q <= u0_m0_wo0_mtree_add1_5_o(17 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr11(DELAY,31)@10
    u0_m0_wo0_wi0_r0_delayr11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr10_q, xout => u0_m0_wo0_wi0_r0_delayr11_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr12(DELAY,32)@10
    u0_m0_wo0_wi0_r0_delayr12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr11_q, xout => u0_m0_wo0_wi0_r0_delayr12_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr12_q_11(DELAY,432)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr12_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr12_q, xout => d_u0_m0_wo0_wi0_r0_delayr12_q_11_q, clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr12_q_12(DELAY,433)@11 + 1
    d_u0_m0_wo0_wi0_r0_delayr12_q_12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u0_m0_wo0_wi0_r0_delayr12_q_11_q, xout => d_u0_m0_wo0_wi0_r0_delayr12_q_12_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_18_shift2(BITSHIFT,345)@12
    u0_m0_wo0_mtree_mult1_18_shift2_qint <= d_u0_m0_wo0_wi0_r0_delayr12_q_12_q & "000";
    u0_m0_wo0_mtree_mult1_18_shift2_q <= u0_m0_wo0_mtree_mult1_18_shift2_qint(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_18_shift0(BITSHIFT,343)@11
    u0_m0_wo0_mtree_mult1_18_shift0_qint <= d_u0_m0_wo0_wi0_r0_delayr12_q_11_q & "0";
    u0_m0_wo0_mtree_mult1_18_shift0_q <= u0_m0_wo0_mtree_mult1_18_shift0_qint(12 downto 0);

    -- u0_m0_wo0_mtree_mult1_18_add_1(ADD,344)@11 + 1
    u0_m0_wo0_mtree_mult1_18_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => d_u0_m0_wo0_wi0_r0_delayr12_q_11_q(11)) & d_u0_m0_wo0_wi0_r0_delayr12_q_11_q));
    u0_m0_wo0_mtree_mult1_18_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u0_m0_wo0_mtree_mult1_18_shift0_q(12)) & u0_m0_wo0_mtree_mult1_18_shift0_q));
    u0_m0_wo0_mtree_mult1_18_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_18_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_18_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_18_add_1_a) + SIGNED(u0_m0_wo0_mtree_mult1_18_add_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_18_add_1_q <= u0_m0_wo0_mtree_mult1_18_add_1_o(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_18_add_3(ADD,346)@12 + 1
    u0_m0_wo0_mtree_mult1_18_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 14 => u0_m0_wo0_mtree_mult1_18_add_1_q(13)) & u0_m0_wo0_mtree_mult1_18_add_1_q));
    u0_m0_wo0_mtree_mult1_18_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_18_shift2_q(14)) & u0_m0_wo0_mtree_mult1_18_shift2_q));
    u0_m0_wo0_mtree_mult1_18_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_18_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_18_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_18_add_3_a) + SIGNED(u0_m0_wo0_mtree_mult1_18_add_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_18_add_3_q <= u0_m0_wo0_mtree_mult1_18_add_3_o(15 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr13(DELAY,33)@10
    u0_m0_wo0_wi0_r0_delayr13 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr12_q, xout => u0_m0_wo0_wi0_r0_delayr13_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr13_q_11(DELAY,434)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr13_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr13_q, xout => d_u0_m0_wo0_wi0_r0_delayr13_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_17_shift2(BITSHIFT,349)@11
    u0_m0_wo0_mtree_mult1_17_shift2_qint <= d_u0_m0_wo0_wi0_r0_delayr13_q_11_q & "00000";
    u0_m0_wo0_mtree_mult1_17_shift2_q <= u0_m0_wo0_mtree_mult1_17_shift2_qint(16 downto 0);

    -- u0_m0_wo0_mtree_mult1_17_shift0(BITSHIFT,347)@10
    u0_m0_wo0_mtree_mult1_17_shift0_qint <= u0_m0_wo0_wi0_r0_delayr13_q & "000";
    u0_m0_wo0_mtree_mult1_17_shift0_q <= u0_m0_wo0_mtree_mult1_17_shift0_qint(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_17_sub_1(SUB,348)@10 + 1
    u0_m0_wo0_mtree_mult1_17_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_17_shift0_q(14)) & u0_m0_wo0_mtree_mult1_17_shift0_q));
    u0_m0_wo0_mtree_mult1_17_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 12 => u0_m0_wo0_wi0_r0_delayr13_q(11)) & u0_m0_wo0_wi0_r0_delayr13_q));
    u0_m0_wo0_mtree_mult1_17_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_17_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_17_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_17_sub_1_a) - SIGNED(u0_m0_wo0_mtree_mult1_17_sub_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_17_sub_1_q <= u0_m0_wo0_mtree_mult1_17_sub_1_o(15 downto 0);

    -- u0_m0_wo0_mtree_mult1_17_sub_3(SUB,350)@11 + 1
    u0_m0_wo0_mtree_mult1_17_sub_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u0_m0_wo0_mtree_mult1_17_sub_1_q(15)) & u0_m0_wo0_mtree_mult1_17_sub_1_q));
    u0_m0_wo0_mtree_mult1_17_sub_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u0_m0_wo0_mtree_mult1_17_shift2_q(16)) & u0_m0_wo0_mtree_mult1_17_shift2_q));
    u0_m0_wo0_mtree_mult1_17_sub_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_17_sub_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_17_sub_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_17_sub_3_a) - SIGNED(u0_m0_wo0_mtree_mult1_17_sub_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_17_sub_3_q <= u0_m0_wo0_mtree_mult1_17_sub_3_o(17 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr14(DELAY,34)@10
    u0_m0_wo0_wi0_r0_delayr14 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr13_q, xout => u0_m0_wo0_wi0_r0_delayr14_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr14_q_11(DELAY,435)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr14_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr14_q, xout => d_u0_m0_wo0_wi0_r0_delayr14_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_16_shift2(BITSHIFT,353)@11
    u0_m0_wo0_mtree_mult1_16_shift2_qint <= d_u0_m0_wo0_wi0_r0_delayr14_q_11_q & "00000";
    u0_m0_wo0_mtree_mult1_16_shift2_q <= u0_m0_wo0_mtree_mult1_16_shift2_qint(16 downto 0);

    -- u0_m0_wo0_mtree_mult1_16_shift0(BITSHIFT,351)@10
    u0_m0_wo0_mtree_mult1_16_shift0_qint <= u0_m0_wo0_wi0_r0_delayr14_q & "00";
    u0_m0_wo0_mtree_mult1_16_shift0_q <= u0_m0_wo0_mtree_mult1_16_shift0_qint(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_16_add_1(ADD,352)@10 + 1
    u0_m0_wo0_mtree_mult1_16_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => u0_m0_wo0_wi0_r0_delayr14_q(11)) & u0_m0_wo0_wi0_r0_delayr14_q));
    u0_m0_wo0_mtree_mult1_16_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u0_m0_wo0_mtree_mult1_16_shift0_q(13)) & u0_m0_wo0_mtree_mult1_16_shift0_q));
    u0_m0_wo0_mtree_mult1_16_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_16_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_16_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_16_add_1_a) + SIGNED(u0_m0_wo0_mtree_mult1_16_add_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_16_add_1_q <= u0_m0_wo0_mtree_mult1_16_add_1_o(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_16_add_3(ADD,354)@11 + 1
    u0_m0_wo0_mtree_mult1_16_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u0_m0_wo0_mtree_mult1_16_add_1_q(14)) & u0_m0_wo0_mtree_mult1_16_add_1_q));
    u0_m0_wo0_mtree_mult1_16_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u0_m0_wo0_mtree_mult1_16_shift2_q(16)) & u0_m0_wo0_mtree_mult1_16_shift2_q));
    u0_m0_wo0_mtree_mult1_16_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_16_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_16_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_16_add_3_a) + SIGNED(u0_m0_wo0_mtree_mult1_16_add_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_16_add_3_q <= u0_m0_wo0_mtree_mult1_16_add_3_o(17 downto 0);

    -- u0_m0_wo0_mtree_add0_8(ADD,124)@12 + 1
    u0_m0_wo0_mtree_add0_8_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 18 => u0_m0_wo0_mtree_mult1_16_add_3_q(17)) & u0_m0_wo0_mtree_mult1_16_add_3_q));
    u0_m0_wo0_mtree_add0_8_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 18 => u0_m0_wo0_mtree_mult1_17_sub_3_q(17)) & u0_m0_wo0_mtree_mult1_17_sub_3_q));
    u0_m0_wo0_mtree_add0_8_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add0_8_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add0_8_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add0_8_a) + SIGNED(u0_m0_wo0_mtree_add0_8_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add0_8_q <= u0_m0_wo0_mtree_add0_8_o(18 downto 0);

    -- u0_m0_wo0_mtree_add1_4(ADD,135)@13 + 1
    u0_m0_wo0_mtree_add1_4_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 19 => u0_m0_wo0_mtree_add0_8_q(18)) & u0_m0_wo0_mtree_add0_8_q));
    u0_m0_wo0_mtree_add1_4_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 16 => u0_m0_wo0_mtree_mult1_18_add_3_q(15)) & u0_m0_wo0_mtree_mult1_18_add_3_q));
    u0_m0_wo0_mtree_add1_4_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add1_4_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add1_4_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add1_4_a) + SIGNED(u0_m0_wo0_mtree_add1_4_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add1_4_q <= u0_m0_wo0_mtree_add1_4_o(20 downto 0);

    -- u0_m0_wo0_mtree_add2_2(ADD,141)@14 + 1
    u0_m0_wo0_mtree_add2_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 21 => u0_m0_wo0_mtree_add1_4_q(20)) & u0_m0_wo0_mtree_add1_4_q));
    u0_m0_wo0_mtree_add2_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 18 => u0_m0_wo0_mtree_add1_5_q(17)) & u0_m0_wo0_mtree_add1_5_q));
    u0_m0_wo0_mtree_add2_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add2_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add2_2_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add2_2_a) + SIGNED(u0_m0_wo0_mtree_add2_2_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add2_2_q <= u0_m0_wo0_mtree_add2_2_o(21 downto 0);

    -- u0_m0_wo0_mtree_add3_1(ADD,144)@15 + 1
    u0_m0_wo0_mtree_add3_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 22 => u0_m0_wo0_mtree_add2_2_q(21)) & u0_m0_wo0_mtree_add2_2_q));
    u0_m0_wo0_mtree_add3_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 14 => u0_m0_wo0_mtree_add0_12_q(13)) & u0_m0_wo0_mtree_add0_12_q));
    u0_m0_wo0_mtree_add3_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add3_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add3_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add3_1_a) + SIGNED(u0_m0_wo0_mtree_add3_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add3_1_q <= u0_m0_wo0_mtree_add3_1_o(22 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr15(DELAY,35)@10
    u0_m0_wo0_wi0_r0_delayr15 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr14_q, xout => u0_m0_wo0_wi0_r0_delayr15_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr15_q_11(DELAY,436)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr15_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr15_q, xout => d_u0_m0_wo0_wi0_r0_delayr15_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_15_shift0(BITSHIFT,355)@11
    u0_m0_wo0_mtree_mult1_15_shift0_qint <= d_u0_m0_wo0_wi0_r0_delayr15_q_11_q & "0000000";
    u0_m0_wo0_mtree_mult1_15_shift0_q <= u0_m0_wo0_mtree_mult1_15_shift0_qint(18 downto 0);

    -- u0_m0_wo0_mtree_mult1_15_sub_1(SUB,356)@11 + 1
    u0_m0_wo0_mtree_mult1_15_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((19 downto 19 => u0_m0_wo0_mtree_mult1_15_shift0_q(18)) & u0_m0_wo0_mtree_mult1_15_shift0_q));
    u0_m0_wo0_mtree_mult1_15_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((19 downto 12 => d_u0_m0_wo0_wi0_r0_delayr15_q_11_q(11)) & d_u0_m0_wo0_wi0_r0_delayr15_q_11_q));
    u0_m0_wo0_mtree_mult1_15_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_15_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_15_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_15_sub_1_a) - SIGNED(u0_m0_wo0_mtree_mult1_15_sub_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_15_sub_1_q <= u0_m0_wo0_mtree_mult1_15_sub_1_o(19 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr16(DELAY,36)@10
    u0_m0_wo0_wi0_r0_delayr16 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr15_q, xout => u0_m0_wo0_wi0_r0_delayr16_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr16_q_11(DELAY,437)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr16_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr16_q, xout => d_u0_m0_wo0_wi0_r0_delayr16_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_14_shift2(BITSHIFT,359)@11
    u0_m0_wo0_mtree_mult1_14_shift2_qint <= d_u0_m0_wo0_wi0_r0_delayr16_q_11_q & "00000";
    u0_m0_wo0_mtree_mult1_14_shift2_q <= u0_m0_wo0_mtree_mult1_14_shift2_qint(16 downto 0);

    -- u0_m0_wo0_mtree_mult1_14_shift0(BITSHIFT,357)@10
    u0_m0_wo0_mtree_mult1_14_shift0_qint <= u0_m0_wo0_wi0_r0_delayr16_q & "00";
    u0_m0_wo0_mtree_mult1_14_shift0_q <= u0_m0_wo0_mtree_mult1_14_shift0_qint(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_14_add_1(ADD,358)@10 + 1
    u0_m0_wo0_mtree_mult1_14_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => u0_m0_wo0_wi0_r0_delayr16_q(11)) & u0_m0_wo0_wi0_r0_delayr16_q));
    u0_m0_wo0_mtree_mult1_14_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u0_m0_wo0_mtree_mult1_14_shift0_q(13)) & u0_m0_wo0_mtree_mult1_14_shift0_q));
    u0_m0_wo0_mtree_mult1_14_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_14_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_14_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_14_add_1_a) + SIGNED(u0_m0_wo0_mtree_mult1_14_add_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_14_add_1_q <= u0_m0_wo0_mtree_mult1_14_add_1_o(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_14_add_3(ADD,360)@11 + 1
    u0_m0_wo0_mtree_mult1_14_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u0_m0_wo0_mtree_mult1_14_add_1_q(14)) & u0_m0_wo0_mtree_mult1_14_add_1_q));
    u0_m0_wo0_mtree_mult1_14_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u0_m0_wo0_mtree_mult1_14_shift2_q(16)) & u0_m0_wo0_mtree_mult1_14_shift2_q));
    u0_m0_wo0_mtree_mult1_14_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_14_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_14_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_14_add_3_a) + SIGNED(u0_m0_wo0_mtree_mult1_14_add_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_14_add_3_q <= u0_m0_wo0_mtree_mult1_14_add_3_o(17 downto 0);

    -- u0_m0_wo0_mtree_add0_7(ADD,123)@12 + 1
    u0_m0_wo0_mtree_add0_7_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 18 => u0_m0_wo0_mtree_mult1_14_add_3_q(17)) & u0_m0_wo0_mtree_mult1_14_add_3_q));
    u0_m0_wo0_mtree_add0_7_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((20 downto 20 => u0_m0_wo0_mtree_mult1_15_sub_1_q(19)) & u0_m0_wo0_mtree_mult1_15_sub_1_q));
    u0_m0_wo0_mtree_add0_7_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add0_7_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add0_7_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add0_7_a) + SIGNED(u0_m0_wo0_mtree_add0_7_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add0_7_q <= u0_m0_wo0_mtree_add0_7_o(20 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr17(DELAY,37)@10
    u0_m0_wo0_wi0_r0_delayr17 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr16_q, xout => u0_m0_wo0_wi0_r0_delayr17_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr17_q_11(DELAY,438)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr17_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr17_q, xout => d_u0_m0_wo0_wi0_r0_delayr17_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_13_shift2(BITSHIFT,363)@11
    u0_m0_wo0_mtree_mult1_13_shift2_qint <= d_u0_m0_wo0_wi0_r0_delayr17_q_11_q & "00000";
    u0_m0_wo0_mtree_mult1_13_shift2_q <= u0_m0_wo0_mtree_mult1_13_shift2_qint(16 downto 0);

    -- u0_m0_wo0_mtree_mult1_13_shift0(BITSHIFT,361)@10
    u0_m0_wo0_mtree_mult1_13_shift0_qint <= u0_m0_wo0_wi0_r0_delayr17_q & "000";
    u0_m0_wo0_mtree_mult1_13_shift0_q <= u0_m0_wo0_mtree_mult1_13_shift0_qint(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_13_sub_1(SUB,362)@10 + 1
    u0_m0_wo0_mtree_mult1_13_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_13_shift0_q(14)) & u0_m0_wo0_mtree_mult1_13_shift0_q));
    u0_m0_wo0_mtree_mult1_13_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 12 => u0_m0_wo0_wi0_r0_delayr17_q(11)) & u0_m0_wo0_wi0_r0_delayr17_q));
    u0_m0_wo0_mtree_mult1_13_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_13_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_13_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_13_sub_1_a) - SIGNED(u0_m0_wo0_mtree_mult1_13_sub_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_13_sub_1_q <= u0_m0_wo0_mtree_mult1_13_sub_1_o(15 downto 0);

    -- u0_m0_wo0_mtree_mult1_13_sub_3(SUB,364)@11 + 1
    u0_m0_wo0_mtree_mult1_13_sub_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u0_m0_wo0_mtree_mult1_13_sub_1_q(15)) & u0_m0_wo0_mtree_mult1_13_sub_1_q));
    u0_m0_wo0_mtree_mult1_13_sub_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 17 => u0_m0_wo0_mtree_mult1_13_shift2_q(16)) & u0_m0_wo0_mtree_mult1_13_shift2_q));
    u0_m0_wo0_mtree_mult1_13_sub_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_13_sub_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_13_sub_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_13_sub_3_a) - SIGNED(u0_m0_wo0_mtree_mult1_13_sub_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_13_sub_3_q <= u0_m0_wo0_mtree_mult1_13_sub_3_o(17 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr18(DELAY,38)@10
    u0_m0_wo0_wi0_r0_delayr18 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr17_q, xout => u0_m0_wo0_wi0_r0_delayr18_q, ena => xIn_v(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr18_q_11(DELAY,439)@10 + 1
    d_u0_m0_wo0_wi0_r0_delayr18_q_11 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr18_q, xout => d_u0_m0_wo0_wi0_r0_delayr18_q_11_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_12_shift2(BITSHIFT,367)@11
    u0_m0_wo0_mtree_mult1_12_shift2_qint <= d_u0_m0_wo0_wi0_r0_delayr18_q_11_q & "000";
    u0_m0_wo0_mtree_mult1_12_shift2_q <= u0_m0_wo0_mtree_mult1_12_shift2_qint(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_12_shift0(BITSHIFT,365)@10
    u0_m0_wo0_mtree_mult1_12_shift0_qint <= u0_m0_wo0_wi0_r0_delayr18_q & "0";
    u0_m0_wo0_mtree_mult1_12_shift0_q <= u0_m0_wo0_mtree_mult1_12_shift0_qint(12 downto 0);

    -- u0_m0_wo0_mtree_mult1_12_add_1(ADD,366)@10 + 1
    u0_m0_wo0_mtree_mult1_12_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => u0_m0_wo0_wi0_r0_delayr18_q(11)) & u0_m0_wo0_wi0_r0_delayr18_q));
    u0_m0_wo0_mtree_mult1_12_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u0_m0_wo0_mtree_mult1_12_shift0_q(12)) & u0_m0_wo0_mtree_mult1_12_shift0_q));
    u0_m0_wo0_mtree_mult1_12_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_12_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_12_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_12_add_1_a) + SIGNED(u0_m0_wo0_mtree_mult1_12_add_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_12_add_1_q <= u0_m0_wo0_mtree_mult1_12_add_1_o(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_12_add_3(ADD,368)@11 + 1
    u0_m0_wo0_mtree_mult1_12_add_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 14 => u0_m0_wo0_mtree_mult1_12_add_1_q(13)) & u0_m0_wo0_mtree_mult1_12_add_1_q));
    u0_m0_wo0_mtree_mult1_12_add_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_12_shift2_q(14)) & u0_m0_wo0_mtree_mult1_12_shift2_q));
    u0_m0_wo0_mtree_mult1_12_add_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_12_add_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_12_add_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_12_add_3_a) + SIGNED(u0_m0_wo0_mtree_mult1_12_add_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_12_add_3_q <= u0_m0_wo0_mtree_mult1_12_add_3_o(15 downto 0);

    -- u0_m0_wo0_mtree_add0_6(ADD,122)@12 + 1
    u0_m0_wo0_mtree_add0_6_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 16 => u0_m0_wo0_mtree_mult1_12_add_3_q(15)) & u0_m0_wo0_mtree_mult1_12_add_3_q));
    u0_m0_wo0_mtree_add0_6_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((18 downto 18 => u0_m0_wo0_mtree_mult1_13_sub_3_q(17)) & u0_m0_wo0_mtree_mult1_13_sub_3_q));
    u0_m0_wo0_mtree_add0_6_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add0_6_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add0_6_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add0_6_a) + SIGNED(u0_m0_wo0_mtree_add0_6_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add0_6_q <= u0_m0_wo0_mtree_add0_6_o(18 downto 0);

    -- u0_m0_wo0_mtree_add1_3(ADD,134)@13 + 1
    u0_m0_wo0_mtree_add1_3_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 19 => u0_m0_wo0_mtree_add0_6_q(18)) & u0_m0_wo0_mtree_add0_6_q));
    u0_m0_wo0_mtree_add1_3_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((21 downto 21 => u0_m0_wo0_mtree_add0_7_q(20)) & u0_m0_wo0_mtree_add0_7_q));
    u0_m0_wo0_mtree_add1_3_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add1_3_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add1_3_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add1_3_a) + SIGNED(u0_m0_wo0_mtree_add1_3_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add1_3_q <= u0_m0_wo0_mtree_add1_3_o(21 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr19(DELAY,39)@11
    u0_m0_wo0_wi0_r0_delayr19 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u0_m0_wo0_wi0_r0_delayr18_q_11_q, xout => u0_m0_wo0_wi0_r0_delayr19_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr20(DELAY,40)@11
    u0_m0_wo0_wi0_r0_delayr20 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr19_q, xout => u0_m0_wo0_wi0_r0_delayr20_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr20_q_12(DELAY,440)@11 + 1
    d_u0_m0_wo0_wi0_r0_delayr20_q_12 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr20_q, xout => d_u0_m0_wo0_wi0_r0_delayr20_q_12_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_10_shift1(BITSHIFT,370)@12
    u0_m0_wo0_mtree_mult1_10_shift1_qint <= d_u0_m0_wo0_wi0_r0_delayr20_q_12_q & "00";
    u0_m0_wo0_mtree_mult1_10_shift1_q <= u0_m0_wo0_mtree_mult1_10_shift1_qint(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_10_sub_0(SUB,369)@11 + 1
    u0_m0_wo0_mtree_mult1_10_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u0_m0_wo0_mtree_mult1_10_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => u0_m0_wo0_wi0_r0_delayr20_q(11)) & u0_m0_wo0_wi0_r0_delayr20_q));
    u0_m0_wo0_mtree_mult1_10_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_10_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_10_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_10_sub_0_a) - SIGNED(u0_m0_wo0_mtree_mult1_10_sub_0_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_10_sub_0_q <= u0_m0_wo0_mtree_mult1_10_sub_0_o(12 downto 0);

    -- u0_m0_wo0_mtree_mult1_10_sub_2(SUB,371)@12 + 1
    u0_m0_wo0_mtree_mult1_10_sub_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 13 => u0_m0_wo0_mtree_mult1_10_sub_0_q(12)) & u0_m0_wo0_mtree_mult1_10_sub_0_q));
    u0_m0_wo0_mtree_mult1_10_sub_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u0_m0_wo0_mtree_mult1_10_shift1_q(13)) & u0_m0_wo0_mtree_mult1_10_shift1_q));
    u0_m0_wo0_mtree_mult1_10_sub_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_10_sub_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_10_sub_2_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_10_sub_2_a) - SIGNED(u0_m0_wo0_mtree_mult1_10_sub_2_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_10_sub_2_q <= u0_m0_wo0_mtree_mult1_10_sub_2_o(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_9_shift0(BITSHIFT,372)@11
    u0_m0_wo0_mtree_mult1_9_shift0_qint <= u0_m0_wo0_wi0_r0_delayr21_q & "0";
    u0_m0_wo0_mtree_mult1_9_shift0_q <= u0_m0_wo0_mtree_mult1_9_shift0_qint(12 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr21(DELAY,41)@11
    u0_m0_wo0_wi0_r0_delayr21 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr20_q, xout => u0_m0_wo0_wi0_r0_delayr21_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_9_add_1(ADD,373)@11 + 1
    u0_m0_wo0_mtree_mult1_9_add_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 12 => u0_m0_wo0_wi0_r0_delayr21_q(11)) & u0_m0_wo0_wi0_r0_delayr21_q));
    u0_m0_wo0_mtree_mult1_9_add_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((13 downto 13 => u0_m0_wo0_mtree_mult1_9_shift0_q(12)) & u0_m0_wo0_mtree_mult1_9_shift0_q));
    u0_m0_wo0_mtree_mult1_9_add_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_9_add_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_9_add_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_9_add_1_a) + SIGNED(u0_m0_wo0_mtree_mult1_9_add_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_9_add_1_q <= u0_m0_wo0_mtree_mult1_9_add_1_o(13 downto 0);

    -- u0_m0_wo0_mtree_mult1_9_shift2(BITSHIFT,374)@12
    u0_m0_wo0_mtree_mult1_9_shift2_qint <= u0_m0_wo0_mtree_mult1_9_add_1_q & "0";
    u0_m0_wo0_mtree_mult1_9_shift2_q <= u0_m0_wo0_mtree_mult1_9_shift2_qint(14 downto 0);

    -- u0_m0_wo0_mtree_mult1_8_shift0(BITSHIFT,375)@11
    u0_m0_wo0_mtree_mult1_8_shift0_qint <= u0_m0_wo0_wi0_r0_delayr22_q & "00";
    u0_m0_wo0_mtree_mult1_8_shift0_q <= u0_m0_wo0_mtree_mult1_8_shift0_qint(13 downto 0);

    -- u0_m0_wo0_wi0_r0_delayr22(DELAY,42)@11
    u0_m0_wo0_wi0_r0_delayr22 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr21_q, xout => u0_m0_wo0_wi0_r0_delayr22_q, ena => d_u0_m0_wo0_compute_q_11_q(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_8_sub_1(SUB,376)@11 + 1
    u0_m0_wo0_mtree_mult1_8_sub_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 12 => u0_m0_wo0_wi0_r0_delayr22_q(11)) & u0_m0_wo0_wi0_r0_delayr22_q));
    u0_m0_wo0_mtree_mult1_8_sub_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((14 downto 14 => u0_m0_wo0_mtree_mult1_8_shift0_q(13)) & u0_m0_wo0_mtree_mult1_8_shift0_q));
    u0_m0_wo0_mtree_mult1_8_sub_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_8_sub_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_8_sub_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_8_sub_1_a) - SIGNED(u0_m0_wo0_mtree_mult1_8_sub_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_8_sub_1_q <= u0_m0_wo0_mtree_mult1_8_sub_1_o(14 downto 0);

    -- u0_m0_wo0_mtree_add0_4(ADD,120)@12 + 1
    u0_m0_wo0_mtree_add0_4_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_8_sub_1_q(14)) & u0_m0_wo0_mtree_mult1_8_sub_1_q));
    u0_m0_wo0_mtree_add0_4_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 15 => u0_m0_wo0_mtree_mult1_9_shift2_q(14)) & u0_m0_wo0_mtree_mult1_9_shift2_q));
    u0_m0_wo0_mtree_add0_4_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add0_4_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add0_4_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add0_4_a) + SIGNED(u0_m0_wo0_mtree_add0_4_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add0_4_q <= u0_m0_wo0_mtree_add0_4_o(15 downto 0);

    -- u0_m0_wo0_mtree_add1_2(ADD,133)@13 + 1
    u0_m0_wo0_mtree_add1_2_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 16 => u0_m0_wo0_mtree_add0_4_q(15)) & u0_m0_wo0_mtree_add0_4_q));
    u0_m0_wo0_mtree_add1_2_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((17 downto 15 => u0_m0_wo0_mtree_mult1_10_sub_2_q(14)) & u0_m0_wo0_mtree_mult1_10_sub_2_q));
    u0_m0_wo0_mtree_add1_2_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add1_2_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add1_2_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add1_2_a) + SIGNED(u0_m0_wo0_mtree_add1_2_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add1_2_q <= u0_m0_wo0_mtree_add1_2_o(17 downto 0);

    -- u0_m0_wo0_mtree_add2_1(ADD,140)@14 + 1
    u0_m0_wo0_mtree_add2_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 18 => u0_m0_wo0_mtree_add1_2_q(17)) & u0_m0_wo0_mtree_add1_2_q));
    u0_m0_wo0_mtree_add2_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((22 downto 22 => u0_m0_wo0_mtree_add1_3_q(21)) & u0_m0_wo0_mtree_add1_3_q));
    u0_m0_wo0_mtree_add2_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add2_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add2_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add2_1_a) + SIGNED(u0_m0_wo0_mtree_add2_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add2_1_q <= u0_m0_wo0_mtree_add2_1_o(22 downto 0);

    -- d_u0_m0_wo0_wi0_r0_delayr22_q_13(DELAY,441)@11 + 2
    d_u0_m0_wo0_wi0_r0_delayr22_q_13 : dspba_delay
    GENERIC MAP ( width => 12, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr22_q, xout => d_u0_m0_wo0_wi0_r0_delayr22_q_13_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr23(DELAY,43)@13
    u0_m0_wo0_wi0_r0_delayr23 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u0_m0_wo0_wi0_r0_delayr22_q_13_q, xout => u0_m0_wo0_wi0_r0_delayr23_q, ena => d_u0_m0_wo0_compute_q_13_q(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr24(DELAY,44)@13
    u0_m0_wo0_wi0_r0_delayr24 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr23_q, xout => u0_m0_wo0_wi0_r0_delayr24_q, ena => d_u0_m0_wo0_compute_q_13_q(0), clk => clk, aclr => areset );

    -- d_u0_m0_wo0_wi0_r0_delayr24_q_14(DELAY,442)@13 + 1
    d_u0_m0_wo0_wi0_r0_delayr24_q_14 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr24_q, xout => d_u0_m0_wo0_wi0_r0_delayr24_q_14_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_wi0_r0_delayr25(DELAY,45)@13
    u0_m0_wo0_wi0_r0_delayr25 : dspba_delay
    GENERIC MAP ( width => 12, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => u0_m0_wo0_wi0_r0_delayr24_q, xout => u0_m0_wo0_wi0_r0_delayr25_q, ena => d_u0_m0_wo0_compute_q_13_q(0), clk => clk, aclr => areset );

    -- u0_m0_wo0_mtree_mult1_5_sub_0(SUB,377)@13 + 1
    u0_m0_wo0_mtree_mult1_5_sub_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 1 => GND_q(0)) & GND_q));
    u0_m0_wo0_mtree_mult1_5_sub_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((12 downto 12 => u0_m0_wo0_wi0_r0_delayr25_q(11)) & u0_m0_wo0_wi0_r0_delayr25_q));
    u0_m0_wo0_mtree_mult1_5_sub_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_mult1_5_sub_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_mult1_5_sub_0_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_mult1_5_sub_0_a) - SIGNED(u0_m0_wo0_mtree_mult1_5_sub_0_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_mult1_5_sub_0_q <= u0_m0_wo0_mtree_mult1_5_sub_0_o(12 downto 0);

    -- u0_m0_wo0_mtree_add1_1(ADD,132)@14 + 1
    u0_m0_wo0_mtree_add1_1_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 13 => u0_m0_wo0_mtree_mult1_5_sub_0_q(12)) & u0_m0_wo0_mtree_mult1_5_sub_0_q));
    u0_m0_wo0_mtree_add1_1_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((15 downto 12 => d_u0_m0_wo0_wi0_r0_delayr24_q_14_q(11)) & d_u0_m0_wo0_wi0_r0_delayr24_q_14_q));
    u0_m0_wo0_mtree_add1_1_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add1_1_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add1_1_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add1_1_a) + SIGNED(u0_m0_wo0_mtree_add1_1_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add1_1_q <= u0_m0_wo0_mtree_add1_1_o(15 downto 0);

    -- u0_m0_wo0_mtree_add3_0(ADD,143)@15 + 1
    u0_m0_wo0_mtree_add3_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((23 downto 16 => u0_m0_wo0_mtree_add1_1_q(15)) & u0_m0_wo0_mtree_add1_1_q));
    u0_m0_wo0_mtree_add3_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((23 downto 23 => u0_m0_wo0_mtree_add2_1_q(22)) & u0_m0_wo0_mtree_add2_1_q));
    u0_m0_wo0_mtree_add3_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add3_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add3_0_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add3_0_a) + SIGNED(u0_m0_wo0_mtree_add3_0_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add3_0_q <= u0_m0_wo0_mtree_add3_0_o(23 downto 0);

    -- u0_m0_wo0_mtree_add4_0(ADD,145)@16 + 1
    u0_m0_wo0_mtree_add4_0_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((24 downto 24 => u0_m0_wo0_mtree_add3_0_q(23)) & u0_m0_wo0_mtree_add3_0_q));
    u0_m0_wo0_mtree_add4_0_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((24 downto 23 => u0_m0_wo0_mtree_add3_1_q(22)) & u0_m0_wo0_mtree_add3_1_q));
    u0_m0_wo0_mtree_add4_0_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_mtree_add4_0_o <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_mtree_add4_0_o <= STD_LOGIC_VECTOR(SIGNED(u0_m0_wo0_mtree_add4_0_a) + SIGNED(u0_m0_wo0_mtree_add4_0_b));
        END IF;
    END PROCESS;
    u0_m0_wo0_mtree_add4_0_q <= u0_m0_wo0_mtree_add4_0_o(24 downto 0);

    -- GND(CONSTANT,0)@0
    GND_q <= "0";

    -- d_u0_m0_wo0_compute_q_16(DELAY,426)@13 + 3
    d_u0_m0_wo0_compute_q_16 : dspba_delay
    GENERIC MAP ( width => 1, depth => 3, reset_kind => "ASYNC" )
    PORT MAP ( xin => d_u0_m0_wo0_compute_q_13_q, xout => d_u0_m0_wo0_compute_q_16_q, clk => clk, aclr => areset );

    -- u0_m0_wo0_oseq_gated_reg(REG,146)@16 + 1
    u0_m0_wo0_oseq_gated_reg_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            u0_m0_wo0_oseq_gated_reg_q <= "0";
        ELSIF (clk'EVENT AND clk = '1') THEN
            u0_m0_wo0_oseq_gated_reg_q <= STD_LOGIC_VECTOR(d_u0_m0_wo0_compute_q_16_q);
        END IF;
    END PROCESS;

    -- xOut(PORTOUT,293)@17 + 1
    xOut_v <= u0_m0_wo0_oseq_gated_reg_q;
    xOut_c <= STD_LOGIC_VECTOR("0000000" & GND_q);
    xOut_0 <= u0_m0_wo0_mtree_add4_0_q;
    xOut_1 <= u1_m0_wo0_mtree_add4_0_q;

END normal;
