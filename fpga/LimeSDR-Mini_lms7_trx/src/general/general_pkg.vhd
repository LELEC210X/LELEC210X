<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	general_pkg.vhd
-- DESCRIPTION:	Package for geenral functions
-- DATE:	June 8, 2017
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Package declaration
-- ----------------------------------------------------------------------------
package general_pkg is

function COUNT_ONES (vect : std_logic_vector)
      return integer;
<<<<<<< refs/remotes/upstream/main
      
=======

>>>>>>> Revert "enlever le chain de argu"
end  general_pkg;

-- ----------------------------------------------------------------------------
-- Package body
-- ----------------------------------------------------------------------------
package body general_pkg is

-- ----------------------------------------------------------------------------
-- Count ones in std_logic_vector
-- ----------------------------------------------------------------------------
<<<<<<< refs/remotes/upstream/main
   function COUNT_ONES (vect : std_logic_vector)  
      return integer is
      variable temp : natural := 0;
   begin  
      for i in vect'range loop
         if vect(i) = '1' then 
=======
   function COUNT_ONES (vect : std_logic_vector)
      return integer is
      variable temp : natural := 0;
   begin
      for i in vect'range loop
         if vect(i) = '1' then
>>>>>>> Revert "enlever le chain de argu"
            temp := temp + 1;
         end if;
      end loop;
      return temp;
   end COUNT_ONES;
<<<<<<< refs/remotes/upstream/main
   
   
   
end general_pkg;
      
      
=======



end general_pkg;
>>>>>>> Revert "enlever le chain de argu"
