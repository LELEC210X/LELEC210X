-- ----------------------------------------------------------------------------	
-- FILE: 	revisions.vhd
-- DESCRIPTION:	Project revision constatns
-- DATE:	Aug 22, 2016
-- AUTHOR(s):	Lime Microsystems
-- REVISIONS:
-- ----------------------------------------------------------------------------	
LIBRARY ieee;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_arith.all;
use IEEE.std_logic_unsigned.all;

package revisions is
	constant MAJOR_REV : INTEGER := 1;
	constant MINOR_REV : INTEGER := 1;
	constant BETA_REV : INTEGER := 1;
	constant COMPILE_REV : INTEGER := 30;
	constant COMPILE_YEAR_STAMP : INTEGER := 19;
	constant COMPILE_MONTH_STAMP : INTEGER := 05;
	constant COMPILE_DAY_STAMP : INTEGER := 07;
	constant COMPILE_HOUR_STAMP : INTEGER := 14;
	
	constant MAGIC_NUM : STD_LOGIC_VECTOR(31 downto 0) := X"D8A5F009";
   constant BOARD_ID : STD_LOGIC_VECTOR(15 downto 0) := X"0011"; -- LimeSDR-MINI
end revisions;
