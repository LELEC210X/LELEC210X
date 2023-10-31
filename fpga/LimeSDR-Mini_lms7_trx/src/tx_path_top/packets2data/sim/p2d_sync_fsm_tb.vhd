-- ----------------------------------------------------------------------------
-- FILE:          p2d_sync_fsm_tb.vhd
<<<<<<< refs/remotes/upstream/main
-- DESCRIPTION:   
=======
-- DESCRIPTION:
>>>>>>> Revert "enlever le chain de argu"
-- DATE:          10:50 AM Thursday, October 19, 2017
-- AUTHOR(s):     Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTES:
-- ----------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity p2d_sync_fsm_tb is
end p2d_sync_fsm_tb;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------

architecture tb_behave of p2d_sync_fsm_tb is
   constant clk0_period    : time := 10 ns;
<<<<<<< refs/remotes/upstream/main
   constant clk1_period    : time := 10 ns; 
   --signals
   signal clk0,clk1        : std_logic;
   signal reset_n          : std_logic; 
   
=======
   constant clk1_period    : time := 10 ns;
   --signals
   signal clk0,clk1        : std_logic;
   signal reset_n          : std_logic;

>>>>>>> Revert "enlever le chain de argu"
   --dut 0
   signal dut0_pct_hdr_0_valid   : std_logic_vector(3 downto 0) := (others=>'0');
   signal dut0_pct_hdr_1_valid   : std_logic_vector(3 downto 0) := (others=>'1');
   signal dut0_pct_data_clr_n    : std_logic_vector(3 downto 0) := (others=>'1');
   signal dut0_pct_buff_rdy      : std_logic_vector(3 downto 0) := (others=>'1');
<<<<<<< refs/remotes/upstream/main
   
begin 
  
=======

begin

>>>>>>> Revert "enlever le chain de argu"
      clock0: process is
   begin
      clk0 <= '0'; wait for clk0_period/2;
      clk0 <= '1'; wait for clk0_period/2;
   end process clock0;

      clock: process is
   begin
      clk1 <= '0'; wait for clk1_period/2;
      clk1 <= '1'; wait for clk1_period/2;
   end process clock;
<<<<<<< refs/remotes/upstream/main
   
=======

>>>>>>> Revert "enlever le chain de argu"
      res: process is
   begin
      reset_n <= '0'; wait for 20 ns;
      reset_n <= '1'; wait;
   end process res;
<<<<<<< refs/remotes/upstream/main
   
=======

>>>>>>> Revert "enlever le chain de argu"
   process is
   begin
      dut0_pct_hdr_0_valid <= (others => '0');
      wait until reset_n = '1';
      wait until rising_edge(clk0);
      dut0_pct_hdr_0_valid <= "1010";
      wait until rising_edge(clk0);
      dut0_pct_hdr_0_valid <= "0000";
      wait;
   end process;
<<<<<<< refs/remotes/upstream/main
   
   
   
   
      -- design under test  
=======




      -- design under test
>>>>>>> Revert "enlever le chain de argu"

p2d_sync_fsm_dut0 : entity work.p2d_sync_fsm
   generic map(
      pct_size_w           =>  16,
      n_buff               =>  4 -- 2,4 valid values
   )
   port map(
      clk                  => clk0,
      reset_n              => reset_n,
<<<<<<< refs/remotes/upstream/main
      --Mode settings      
=======
      --Mode settings
>>>>>>> Revert "enlever le chain de argu"
      mode			         => '0', -- JESD207: 1; TRXIQ: 0
      trxiqpulse	         => '0', -- trxiqpulse on: 1; trxiqpulse off: 0
		ddr_en 		         => '1', -- DDR: 1; SDR: 0
		mimo_en		         => '0', -- SISO: 1; MIMO: 0
<<<<<<< refs/remotes/upstream/main
		ch_en			         => "01", --"01" - Ch. A, "10" - Ch. B, "11" - Ch. A and Ch. B.  
      sample_width         => "10", --"10"-12bit, "01"-14bit, "00"-16bit;
      
      pct_size             => x"000F",    --Whole packet size in 
                                                                           --in_pct_data_w words
      pct_sync_dis         => '0',
                                                                           
      smpl_nr              => (others=>'0'),
                                                                           
      pct_hdr_0            => x"0000000000000010",
      pct_hdr_0_valid      => dut0_pct_hdr_0_valid,
      
      pct_hdr_1            => (others=> '1'),
      pct_hdr_1_valid      => dut0_pct_hdr_1_valid,
     
      pct_data_clr_n       => dut0_pct_data_clr_n,      
      pct_buff_rdy         => dut0_pct_buff_rdy, --assert when whole packet is ready

      pct_buff_rd_en       => open   
      
        );

end tb_behave;

=======
		ch_en			         => "01", --"01" - Ch. A, "10" - Ch. B, "11" - Ch. A and Ch. B.
      sample_width         => "10", --"10"-12bit, "01"-14bit, "00"-16bit;

      pct_size             => x"000F",    --Whole packet size in
                                                                           --in_pct_data_w words
      pct_sync_dis         => '0',

      smpl_nr              => (others=>'0'),

      pct_hdr_0            => x"0000000000000010",
      pct_hdr_0_valid      => dut0_pct_hdr_0_valid,

      pct_hdr_1            => (others=> '1'),
      pct_hdr_1_valid      => dut0_pct_hdr_1_valid,

      pct_data_clr_n       => dut0_pct_data_clr_n,
      pct_buff_rdy         => dut0_pct_buff_rdy, --assert when whole packet is ready

      pct_buff_rd_en       => open

        );

end tb_behave;
>>>>>>> Revert "enlever le chain de argu"
