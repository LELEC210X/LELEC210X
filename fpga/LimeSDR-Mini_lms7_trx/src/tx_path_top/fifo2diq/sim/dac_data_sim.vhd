
<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	adc_data_sim.vhd
-- DESCRIPTION:	Reads from file simulation ADC data of LMS7002
-- DATE:	Jan 10, 2017
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
use std.textio.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity dac_data_sim is
<<<<<<< refs/remotes/upstream/main
   generic( 
		file_name	: string 	:= "file.txt";
      data_width	: integer	:= 12  		
=======
   generic(
		file_name	: string 	:= "file.txt";
      data_width	: integer	:= 12
>>>>>>> Revert "enlever le chain de argu"
	);
	port (
      clk			: in std_logic;
      reset_n		: in std_logic;
		en				: in std_logic;
<<<<<<< refs/remotes/upstream/main
		AI				: out std_logic_vector(data_width-1 downto 0);	
		AQ				: out std_logic_vector(data_width-1 downto 0);	
		BI				: out std_logic_vector(data_width-1 downto 0);	
		BQ				: out std_logic_vector(data_width-1 downto 0)        
=======
		AI				: out std_logic_vector(data_width-1 downto 0);
		AQ				: out std_logic_vector(data_width-1 downto 0);
		BI				: out std_logic_vector(data_width-1 downto 0);
		BQ				: out std_logic_vector(data_width-1 downto 0)
>>>>>>> Revert "enlever le chain de argu"
        );
end dac_data_sim;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of dac_data_sim is
--declare signals,  components here
<<<<<<< refs/remotes/upstream/main
signal AI_reg : std_logic_vector(data_width-1 downto 0);	
signal AQ_reg : std_logic_vector(data_width-1 downto 0);	
signal BI_reg : std_logic_vector(data_width-1 downto 0);	
signal BQ_reg : std_logic_vector(data_width-1 downto 0);

file fp: text; 
=======
signal AI_reg : std_logic_vector(data_width-1 downto 0);
signal AQ_reg : std_logic_vector(data_width-1 downto 0);
signal BI_reg : std_logic_vector(data_width-1 downto 0);
signal BQ_reg : std_logic_vector(data_width-1 downto 0);

file fp: text;
>>>>>>> Revert "enlever le chain de argu"

begin

file_open(fp, file_name, READ_MODE);

--Reads iAI, iAQ, iBI, iBQ samples when en=1 at rising edge of clock
  read_samples : process(reset_n, clk)
    variable line_storage: line;
    variable line_string: string(20 downto 1);
    variable iAI, iAQ, iBI, iBQ: integer := 0;
    begin
      if reset_n='0' then
			AI_reg <= (others=>'0');
			AQ_reg <= (others=>'0');
			BI_reg <= (others=>'0');
<<<<<<< refs/remotes/upstream/main
			BQ_reg<= (others=>'0'); 
      elsif (clk'event and clk = '1') then
			if en='1' then 
=======
			BQ_reg<= (others=>'0');
      elsif (clk'event and clk = '1') then
			if en='1' then
>>>>>>> Revert "enlever le chain de argu"
				if ( not endfile(fp)) then
 	      		readline(fp, line_storage);
					read(line_storage, iAI);
					read(line_storage, iAQ);
					read(line_storage, iBI);
					read(line_storage, iBQ);
					AI_reg <= std_logic_vector( to_signed( iAI, data_width ));
					AQ_reg <= std_logic_vector( to_signed( iAQ, data_width ));
					BI_reg <= std_logic_vector( to_signed( iBI, data_width ));
					BQ_reg <= std_logic_vector( to_signed( iBQ, data_width ));
<<<<<<< refs/remotes/upstream/main
				else 
=======
				else
>>>>>>> Revert "enlever le chain de argu"
					AI_reg <= (others=>'0');
					AQ_reg <= (others=>'0');
					BI_reg <= (others=>'0');
					BQ_reg <= (others=>'0');
				end if;
<<<<<<< refs/remotes/upstream/main
			else 
=======
			else
>>>>>>> Revert "enlever le chain de argu"
					AI_reg <= AI_reg;
					AQ_reg <= AQ_reg;
					BI_reg <= BI_reg;
					BQ_reg <= BQ_reg;
			end if;
 	    end if;
    end process;

AI <= AI_reg;
AQ <= AQ_reg;
BI <= BI_reg;
BQ <= BQ_reg;

<<<<<<< refs/remotes/upstream/main
  
end arch;   





=======

end arch;
>>>>>>> Revert "enlever le chain de argu"
