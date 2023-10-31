-- ----------------------------------------------------------------------------
-- FILE:          periphcfg_pkg.vhd
-- DESCRIPTION:   Package for periphcfg module
-- DATE:          9:57 AM Monday, May 14, 2018
-- AUTHOR(s):     Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
--NOTES:
-- ----------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Package declaration
-- ----------------------------------------------------------------------------
package periphcfg_pkg is
<<<<<<< refs/remotes/upstream/main
   
   -- Outputs from the 
=======

   -- Outputs from the
>>>>>>> Revert "enlever le chain de argu"
   type t_FROM_PERIPHCFG is record
      BOARD_GPIO_OVRD      : std_logic_vector(15 downto 0);
      BOARD_GPIO_DIR       : std_logic_vector(15 downto 0);
      BOARD_GPIO_VAL       : std_logic_vector(15 downto 0);
      PERIPH_OUTPUT_OVRD_0 : std_logic_vector(15 downto 0);
      PERIPH_OUTPUT_VAL_0  : std_logic_vector(15 downto 0);
      PERIPH_OUTPUT_OVRD_1 : std_logic_vector(15 downto 0);
<<<<<<< refs/remotes/upstream/main
      PERIPH_OUTPUT_VAL_1  : std_logic_vector(15 downto 0); 
   end record t_FROM_PERIPHCFG;
  
=======
      PERIPH_OUTPUT_VAL_1  : std_logic_vector(15 downto 0);
   end record t_FROM_PERIPHCFG;

>>>>>>> Revert "enlever le chain de argu"
   -- Inputs to the .
   type t_TO_PERIPHCFG is record
      BOARD_GPIO_RD        : std_logic_vector(15 downto 0);
      PERIPH_INPUT_RD_0    : std_logic_vector(15 downto 0);
      PERIPH_INPUT_RD_1    : std_logic_vector(15 downto 0);
   end record t_TO_PERIPHCFG;
<<<<<<< refs/remotes/upstream/main
   



   

      
end package periphcfg_pkg;
=======







end package periphcfg_pkg;
>>>>>>> Revert "enlever le chain de argu"
