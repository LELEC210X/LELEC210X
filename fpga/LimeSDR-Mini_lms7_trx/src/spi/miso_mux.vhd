<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	miso_mux.vhd
-- DESCRIPTION:	mux for spi miso signal
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
entity miso_mux is
  port (
<<<<<<< refs/remotes/upstream/main
        --input ports 
=======
        --input ports
>>>>>>> Revert "enlever le chain de argu"
        fpga_miso       : in std_logic;
        ext_miso		   : in std_logic;
		  fpga_cs			: in std_logic;
		  ext_cs				: in std_logic;

<<<<<<< refs/remotes/upstream/main
        --output ports 
=======
        --output ports
>>>>>>> Revert "enlever le chain de argu"
        out_miso			: out std_logic
        );
end miso_mux;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of miso_mux is
--declare signals,  components here


<<<<<<< refs/remotes/upstream/main
  
begin

out_miso<=fpga_miso when (fpga_cs='0') else 
				ext_miso when (fpga_cs='1' and ext_cs='0') else
				'Z';
  
end arch;   




=======

begin

out_miso<=fpga_miso when (fpga_cs='0') else
				ext_miso when (fpga_cs='1' and ext_cs='0') else
				'Z';

end arch;
>>>>>>> Revert "enlever le chain de argu"
