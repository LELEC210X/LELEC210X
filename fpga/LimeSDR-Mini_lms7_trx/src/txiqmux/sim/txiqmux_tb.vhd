<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
-- FILE: 	txiqmux_tb.vhd
-- DESCRIPTION:	
-- DATE:	Feb 13, 2014
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
-- FILE: 	txiqmux_tb.vhd
-- DESCRIPTION:
-- DATE:	Feb 13, 2014
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity txiqmux_tb is
end txiqmux_tb;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------

architecture tb_behave of txiqmux_tb is
	constant clk0_period   : time := 10 ns;
<<<<<<< refs/remotes/upstream/main
	constant clk1_period   : time := 10 ns; 
  --signals
	signal clk0,clk1		: std_logic;
	signal reset_n       : std_logic; 
  
begin 
  
=======
	constant clk1_period   : time := 10 ns;
  --signals
	signal clk0,clk1		: std_logic;
	signal reset_n       : std_logic;

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
	
  
txiqmux_inst0 : entity work.txiqmux 
=======


txiqmux_inst0 : entity work.txiqmux
>>>>>>> Revert "enlever le chain de argu"
   generic map(
      diq_width      =>  12
   )
   port map(

      clk            => clk0,
      reset_n        => reset_n,
      test_ptrn_en   => '1',
      test_ptrn_fidm => '1',
      mux_sel        => '0',
      tx_diq_h       => (others=>'0'),
      tx_diq_l       => (others=>'0'),
      wfm_diq_h      => (others=>'1'),
      wfm_diq_l      => (others=>'1'),
      diq_h          => open,
      diq_l          => open
      );
<<<<<<< refs/remotes/upstream/main
      
	
	end tb_behave;
  
  


  
=======


	end tb_behave;
>>>>>>> Revert "enlever le chain de argu"
