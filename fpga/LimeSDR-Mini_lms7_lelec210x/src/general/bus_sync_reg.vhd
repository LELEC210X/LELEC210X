<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	bus_sync_reg.vhd
-- DESCRIPTION:	Synchronization with two register stages for bus signal
-- DATE:	Jan 13, 2016
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity bus_sync_reg is
   generic(
      bus_width   : integer:= 7
   );
   port (
      clk         : in std_logic;
      reset_n     : in std_logic;
      async_in    : in std_logic_vector(bus_width-1 downto 0);
      sync_out    : out std_logic_vector(bus_width-1 downto 0)
        );
end bus_sync_reg;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of bus_sync_reg is
--declare signals,  components here
signal sync_reg0,sync_reg1 : std_logic_vector (bus_width-1 downto 0);

<<<<<<< refs/remotes/upstream/main
  
=======

>>>>>>> Revert "enlever le chain de argu"
begin

 process(reset_n, clk)
    begin
      if reset_n='0' then
<<<<<<< refs/remotes/upstream/main
         sync_reg0<=(others=>'0'); 
         sync_reg1<=(others=>'0');          
=======
         sync_reg0<=(others=>'0');
         sync_reg1<=(others=>'0');
>>>>>>> Revert "enlever le chain de argu"
      elsif (clk'event and clk = '1') then
         sync_reg0<=async_in;
         sync_reg1<=sync_reg0;
 	    end if;
    end process;
<<<<<<< refs/remotes/upstream/main
    
sync_out<=sync_reg1;
  
end arch;   






=======

sync_out<=sync_reg1;

end arch;
>>>>>>> Revert "enlever le chain de argu"
