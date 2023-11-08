-- ----------------------------------------------------------------------------	
-- FILE:    delay_chain.vhd
-- DESCRIPTION:   describe file
-- DATE: April 27, 2021
-- AUTHOR(s):  Lime Microsystems, Julien Verecken
-- REVISIONS:
-- ----------------------------------------------------------------------------	
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity delay_chain is
   generic( 
		data_width : integer := 64; --data width
      delay      : integer := 6   --delay in clock cycles
      );
   port (
      clk                  : in  std_logic;
      reset_n              : in  std_logic;
      data_in              : in  std_logic_vector(data_width-1 downto 0);
      data_out             : out std_logic_vector(data_width-1 downto 0)
   );
end delay_chain;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of delay_chain is
--declare signals,  components here
--internal signals
type my_array is array (0 to delay-1) of std_logic_vector(data_width-1 downto 0);
signal delay_chain   : my_array;


begin
-- ----------------------------------------------------------------------------
-- There is 6 clock cycle latency from smpl_fifo_inst1 to packet formation
-- and smpl_cnt has to be delayed 6 cycles
-- ----------------------------------------------------------------------------        
delay_registers : process(clk, reset_n)
begin
   if reset_n = '0' then 
      delay_chain <= (others=>(others=>'0'));
   elsif (clk'event AND clk='1') then 
      for i in 0 to 5 loop
         if i=0 then 
            delay_chain(i) <= data_in;
         else 
            delay_chain(i) <= delay_chain(i-1);
         end if;
      end loop;
   end if;
end process;
        
data_out <=  delay_chain(5);      
  
end arch;
