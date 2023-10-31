<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	sync_reg.vhd
-- DESCRIPTION:	Synchronization with two register stages
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
entity sync_reg is
   port (
      clk         : in std_logic;
      reset_n     : in std_logic;
      async_in    : in std_logic;
      sync_out    : out std_logic
        );
end sync_reg;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of sync_reg is
--declare signals,  components here
<<<<<<< refs/remotes/upstream/main
signal sync_reg : std_logic_vector (1 downto 0); 

  
=======
signal sync_reg : std_logic_vector (1 downto 0);


>>>>>>> Revert "enlever le chain de argu"
begin

 process(reset_n, clk)
    begin
      if reset_n='0' then
<<<<<<< refs/remotes/upstream/main
         sync_reg<=(others=>'0');  
=======
         sync_reg<=(others=>'0');
>>>>>>> Revert "enlever le chain de argu"
      elsif (clk'event and clk = '1') then
         sync_reg<=sync_reg(0) & async_in;
 	    end if;
    end process;
<<<<<<< refs/remotes/upstream/main
    
sync_out<=sync_reg(1);
  
end arch;   






=======

sync_out<=sync_reg(1);

end arch;
>>>>>>> Revert "enlever le chain de argu"
