<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
-- FILE: pulse_gen_tb.vhd
-- DESCRIPTION: 
-- DATE: August 25, 2017
-- AUTHOR(s): asLime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
-- FILE: pulse_gen_tb.vhd
-- DESCRIPTION:
-- DATE: August 25, 2017
-- AUTHOR(s): asLime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity pulse_gen_tb is
end pulse_gen_tb;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------

architecture tb_behave of pulse_gen_tb is
   constant clk0_period       : time := 10 ns;
   constant clk1_period       : time := 10 ns;
   constant dut0_wait_cycles  : std_logic_vector(31 downto 0) := x"00000002";
<<<<<<< refs/remotes/upstream/main
   
   --signals
   signal clk0,clk1           : std_logic;
   signal reset_n             : std_logic; 

begin 
  
=======

   --signals
   signal clk0,clk1           : std_logic;
   signal reset_n             : std_logic;

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
   pulse_gen_dut0 : entity work.pulse_gen
   port map(

      clk         => clk0,
      reset_n     => reset_n,
      wait_cycles => dut0_wait_cycles,
      pulse       => open
   );
<<<<<<< refs/remotes/upstream/main
   

   
   end tb_behave;
  

=======



   end tb_behave;
>>>>>>> Revert "enlever le chain de argu"
