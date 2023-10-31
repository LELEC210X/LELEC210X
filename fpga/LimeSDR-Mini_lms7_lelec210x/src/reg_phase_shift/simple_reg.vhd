
<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	simple_reg.vhd
-- DESCRIPTION:	describe
-- DATE:	Feb 13, 2014
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
entity simple_reg is
  port (
<<<<<<< refs/remotes/upstream/main
        --input ports 
=======
        --input ports
>>>>>>> Revert "enlever le chain de argu"
			clk      : in std_logic;
			reset_n  : in std_logic;
			d 			: in std_logic;
			q			: out std_logic

<<<<<<< refs/remotes/upstream/main
        --output ports 
        
=======
        --output ports

>>>>>>> Revert "enlever le chain de argu"
        );
end simple_reg;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of simple_reg is
--declare signals,  components here

<<<<<<< refs/remotes/upstream/main
  
=======

>>>>>>> Revert "enlever le chain de argu"
begin

  process(reset_n, clk)
    begin
      if reset_n='0' then
<<<<<<< refs/remotes/upstream/main
        q<=('0');  
=======
        q<=('0');
>>>>>>> Revert "enlever le chain de argu"
 	    elsif (clk'event and clk = '1') then
 	      q<=d;
 	    end if;
    end process;
<<<<<<< refs/remotes/upstream/main
  
end arch;   




=======

end arch;
>>>>>>> Revert "enlever le chain de argu"
