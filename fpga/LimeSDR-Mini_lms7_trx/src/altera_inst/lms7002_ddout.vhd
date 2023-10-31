<<<<<<< refs/remotes/upstream/main
-- ----------------------------------------------------------------------------	
=======
-- ----------------------------------------------------------------------------
>>>>>>> Revert "enlever le chain de argu"
-- FILE: 	lms7002_ddout.vhd
-- DESCRIPTION:	takes data in SDR and ouputs double data rate
-- DATE:	Mar 14, 2016
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

LIBRARY altera_mf;
USE altera_mf.altera_mf_components.all;

-- ----------------------------------------------------------------------------
-- Entity declaration
-- ----------------------------------------------------------------------------
entity lms7002_ddout is
	generic( dev_family	: string := "Cyclone IV E";
				iq_width		: integer :=12
	);
	port (
<<<<<<< refs/remotes/upstream/main
      --input ports 
=======
      --input ports
>>>>>>> Revert "enlever le chain de argu"
      clk       	: in std_logic;
      reset_n   	: in std_logic;
		data_in_h	: in std_logic_vector(iq_width downto 0);
		data_in_l	: in std_logic_vector(iq_width downto 0);
<<<<<<< refs/remotes/upstream/main
		--output ports 
		txiq		 	: out std_logic_vector(iq_width-1 downto 0);
		txiqsel	 	: out std_logic
		
=======
		--output ports
		txiq		 	: out std_logic_vector(iq_width-1 downto 0);
		txiqsel	 	: out std_logic

>>>>>>> Revert "enlever le chain de argu"
        );
end lms7002_ddout;

-- ----------------------------------------------------------------------------
-- Architecture
-- ----------------------------------------------------------------------------
architecture arch of lms7002_ddout is
--declare signals,  components here
signal aclr 	: std_logic;
signal datout	: std_logic_vector(iq_width downto 0);

begin


aclr<=not reset_n;

	ALTDDIO_OUT_component : ALTDDIO_OUT
	GENERIC MAP (
		extend_oe_disable 		=> "OFF",
		intended_device_family 	=> "Cyclone IV E",
		invert_output 				=> "OFF",
		lpm_hint 					=> "UNUSED",
		lpm_type 					=> "altddio_out",
		oe_reg 						=> "UNREGISTERED",
		power_up_high 				=> "OFF",
		width 						=> iq_width+1
	)
	PORT MAP (
		aclr 			=> aclr,
		datain_h 	=> data_in_h,
		datain_l 	=> data_in_l,
		outclock 	=> clk,
		dataout 		=> datout
	);
<<<<<<< refs/remotes/upstream/main
	
	txiq		<=datout(11 downto 0);
	txiqsel	<=datout(12);
	
  
end arch;   





=======

	txiq		<=datout(11 downto 0);
	txiqsel	<=datout(12);


end arch;
>>>>>>> Revert "enlever le chain de argu"
